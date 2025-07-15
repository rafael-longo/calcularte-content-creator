import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from agents import Agent, Runner

# Load environment variables
load_dotenv()


class PlannedPost(BaseModel):
    day_or_sequence: str  # e.g., "Monday", "Post 1"
    pillar: str
    reasoning: str


class ContentPlan(BaseModel):
    plan: List[PlannedPost]

class ContentPillarDetail(BaseModel):
    pillar: str
    description: str

class BrandVoiceReport(BaseModel):
    executive_summary: str
    key_content_pillars: List[ContentPillarDetail]  # e.g., [{"pillar": "Humor", "description": "..."}]
    audience_persona_summary: str
    tone_of_voice_analysis: str
    language_style_details: str  # Includes emoji and colloquialism usage
    country_culture_details: str
    hashtag_strategy_summary: str

# --- Agent Definitions ---

content_planner_agent = Agent(
    name="Content Planner Agent",
    instructions="""
You are a Brand Strategist for 'Calcularte', a brand that helps artisans and crafters with business management.
Your task is to create a content plan based on the provided context.
You MUST return a single, valid JSON object that conforms to the Pydantic model schema provided in the user message.
The JSON object should be inside a 'plan' key.

The user will provide the Pydantic schema, the time frame, the current date, and brand context.

Instructions for Analysis:
1.  **Analyze Time & Seasonality:** Based on the current date and time frame from the user input, identify key seasonal opportunities.
2.  **Ensure Variety:** Review recent post themes from the user input to avoid repetition.
3.  **Identify Top Pillars:** Analyze the brand context from the user input to determine historically engaging content pillars.
4.  **Synthesize Plan:** Combine these insights to create a balanced and timely content plan. Justify each choice in the 'reasoning' field.

**Strict Output Rules:**
- If the requested `time_frame` is 'day', you MUST generate a plan containing exactly one (1) `PlannedPost` item. The `day_or_sequence` field for this item MUST be the day of the week corresponding to the provided `current_date`.
- If the requested `time_frame` is 'week', you MUST generate a plan containing multiple `PlannedPost` items, typically for days of the week, including the weekend (e.g., Monday, Wednesday, Friday, Sunday).
- If the requested `time_frame` is 'month', you MUST generate a plan that covers the main themes and events for the entire month, sequenced logically.
""",
    output_type=ContentPlan,
    model="gpt-4.1-mini"
)

brand_reporter_agent = Agent(
    name="Brand Reporter Agent",
    instructions="""
You are a Brand Strategist for 'Calcularte', a brand focused on helping artisans and crafters with business management.
Your task is to perform a holistic analysis of the brand's voice based on a sample of their Instagram posts and generate a comprehensive report.
You MUST return a single, valid JSON object that conforms to the Pydantic model schema provided in the user message.

The user will provide the Pydantic schema and the sampled content for analysis.

Instructions for Analysis:
1.  **Executive Summary:** Start with a high-level summary of the brand's overall voice and communication strategy.
2.  **Key Content Pillars:** Analyze the `Sampled Content for Analysis` to identify the main recurring themes or categories of content. For each distinct pillar you identify, provide a "pillar" name and a "description" of what that pillar entails. Examples might include "Educação", "Organização Financeira", "Humor", "Sazonalidade", "Empatia/Motivação", "Produto/Funcionalidade", etc.
3.  **Audience Persona:** Describe the target audience ('Calculover') based on the content's language, tone, and topics.
4.  **Tone of Voice:** Analyze the overall tone. Is it friendly, professional, humorous, educational? Include examples.
5.  **Language & Style:** Detail the specific language used. Note common emojis, colloquialisms, calls-to-action, and sentence structure. Include examples.
6.  **Country & Culture:** Mention any cultural nuances or references.
7.  **Hashtag Strategy:** Summarize the approach to using hashtags. Are they for community building, discoverability, or branding?

**Strict Output Rules:**
- You MUST return a single, valid JSON object that conforms to the `BrandVoiceReport` model.
- Ensure all fields in the model are populated with insightful analysis.
""",
    output_type=BrandVoiceReport,
    model="gpt-4.1-mini"
)


# --- Class Definition ---

class BrandStrategistAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "calcularte_posts"
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
        except:
            print(f"Collection '{self.collection_name}' not found. Please run data ingestion first.")
            self.collection = None

    def get_embedding(self, text: str, model: str = "text-embedding-3-small"):
        """Generates an embedding for the given text."""
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    def query_brand_voice(self, query_text: str, n_results: int = 3):
        """
        Queries the ChromaDB for content semantically similar to the query text.
        Returns the most relevant captions and their metadata.
        """
        if not self.collection:
            return "Brand voice collection not initialized. Please ingest data."

        query_embedding = self.get_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas']
        )

        relevant_content = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                content = {
                    "caption": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                }
                relevant_content.append(content)
        
        return relevant_content

    def propose_content_plan(self, time_frame: str, current_date: date, recent_post_themes: Optional[list] = None) -> ContentPlan:
        """
        Generates a strategic content plan by coordinating with the content_planner_agent.
        """
        if not self.collection:
            return ContentPlan(plan=[])

        seasonal_context = f"Today's date is {current_date.strftime('%Y-%m-%d')}."
        variety_context = f"Avoid these recent themes: {', '.join(recent_post_themes or [])}."
        
        pillar_analysis_query = "Conteúdo sobre organização financeira, dicas de vendas e marketing para artesãs"
        pillar_context_results = self.query_brand_voice(pillar_analysis_query, n_results=5)
        
        pillar_context = "Historically engaging content pillars include: Humor, Educação, Sazonalidade, Dicas de Vendas, Organização Financeira."
        if pillar_context_results and isinstance(pillar_context_results, list):
            extracted_themes = [item['metadata'].get('theme', 'unknown') for item in pillar_context_results]
            pillar_context += f" Recent successful themes were: {', '.join(set(extracted_themes))}."

        user_input = f"""
        Pydantic Schema:
        ```json
        {ContentPlan.model_json_schema()}
        ```

        Context:
        - {seasonal_context}
        - {variety_context}
        - {pillar_context}

        Time Frame: {time_frame}
        Current Date: {current_date.strftime('%Y-%m-%d')}
        """

        try:
            result = Runner.run_sync(content_planner_agent, user_input)
            return result.final_output if result.final_output else ContentPlan(plan=[])
        except Exception as e:
            print(f"Error running content_planner_agent: {e}")
            return ContentPlan(plan=[])

    def generate_brand_voice_report(self) -> BrandVoiceReport:
        """
        Analyzes the brand's voice and generates a report using the brand_reporter_agent.
        """
        if not self.collection:
            return BrandVoiceReport(executive_summary="Brand voice collection not initialized.", key_content_pillars=[], audience_persona_summary="", tone_of_voice_analysis="", language_style_details="", country_culture_details="", hashtag_strategy_summary="")

        try:
            sample_posts = self.collection.get(limit=100, include=['documents', 'metadatas'])
            if not sample_posts or not sample_posts.get('documents'):
                raise ValueError("No documents found in the collection.")
        except Exception as e:
            return BrandVoiceReport(executive_summary=f"Error retrieving data: {e}", key_content_pillars=[], audience_persona_summary="", tone_of_voice_analysis="", language_style_details="", country_culture_details="", hashtag_strategy_summary="")

        sampled_content_str = "\n".join(
            [f"- Caption: {doc}\n  Metadata: {meta}" for doc, meta in zip(sample_posts['documents'], sample_posts['metadatas'])]
        )

        user_input = f"""
        Pydantic Schema:
        ```json
        {BrandVoiceReport.model_json_schema()}
        ```

        Sampled Content for Analysis:
        {sampled_content_str}
        """

        try:
            result = Runner.run_sync(brand_reporter_agent, user_input)
            return result.final_output if result.final_output else BrandVoiceReport(executive_summary="Failed to generate report.", key_content_pillars=[], audience_persona_summary="", tone_of_voice_analysis="", language_style_details="", country_culture_details="", hashtag_strategy_summary="")
        except Exception as e:
            print(f"Error running brand_reporter_agent: {e}")
            return BrandVoiceReport(executive_summary=f"Error generating report: {e}", key_content_pillars=[], audience_persona_summary="", tone_of_voice_analysis="", language_style_details="", country_culture_details="", hashtag_strategy_summary="")


if __name__ == "__main__":
    # Example usage (for testing purposes)
    strategist = BrandStrategistAgent()
    if strategist.collection:
        print("Querying for content about financial organization:")
        results = strategist.query_brand_voice("Como organizar as finanças do meu negócio artesanal?")
        for item in results:
            print(f"Caption: {item['caption']}\nMetadata: {item['metadata']}\n---")
    else:
        print("Cannot run example: ChromaDB collection not available. Run ingest_data.py first.")
