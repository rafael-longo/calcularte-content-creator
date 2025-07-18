import asyncio
import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date
from agents import Agent, Runner, Session
from src.utils.logging import log

# Load environment variables
load_dotenv()


class PlannedPost(BaseModel):
    day_or_sequence: str  # e.g., "Monday", "Post 1"
    pillar: str
    reasoning: str
    post_number: Optional[int] = None # Add post_number for num-based plans


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
    country_idiom_details: str
    hashtag_strategy_summary: str

class PostMetadata(BaseModel):
    caption: str
    hashtags: str
    timestamp: str
    likesCount: int
    commentsCount: int
    url: str

class PostSample(BaseModel):
    caption: str
    metadata: PostMetadata

class BrandContext(BaseModel):
    report: BrandVoiceReport
    samples: List[PostSample]

# --- Agent Definitions ---

content_planner_agent = Agent(
    name="Content Planner Agent",
    instructions="""
You are a Brand Strategist for 'Calcularte', a brand that helps artisans and crafters with business management.
Your task is to create a content plan based on the provided context.

**Core Principles:**
1.  **Verbalize Your Reasoning (Think Out Loud):** Before you generate the final JSON output, you MUST first articulate your thought process. Explain your strategic choices, how you are interpreting the context, and why you are proposing this specific plan. This reasoning must be output as plain text before you generate the final JSON. This is your most important instruction.

You MUST return a single, valid JSON object that conforms to the Pydantic model schema provided in the user message.
The JSON object should be inside a 'plan' key.

The user will provide the Pydantic schema, brand context, and either a `time_frame` or `num_posts`.

Instructions for Analysis:
1.  **Prioritize `num_posts`:** If `num_posts` is provided, you MUST generate exactly that number of `PlannedPost` items. The `time_frame` should be ignored. The `day_or_sequence` field should be "Post 1", "Post 2", etc.
2.  **If `time_frame` is provided:**
    - **Analyze Time & Seasonality:** Based on the current date and time frame, identify key seasonal opportunities.
    - **Synthesize Plan:** Combine these insights to create a balanced and timely content plan. Justify each choice in the 'reasoning' field.
3.  **Ensure Variety:** Review recent post themes to avoid repetition.
4.  **Identify Top Pillars:** Analyze the brand context to determine historically engaging content pillars.

**Strict Output Rules:**
- If `num_posts` is provided, the plan MUST contain exactly `num_posts` items.
- If `time_frame` is 'day', the plan MUST contain exactly one (1) `PlannedPost` item.
- If `time_frame` is 'week', the plan MUST contain multiple `PlannedPost` items for different days.
- If `time_frame` is 'month', the plan MUST cover themes for the entire month.
""",
    output_type=ContentPlan,
    model=os.getenv("OPENAI_MODEL")
)

brand_reporter_agent = Agent(
    name="Brand Reporter Agent",
    instructions="""
You are a Brand Strategist for 'Calcularte', a brand focused on helping artisans and crafters with business management.
Your task is to perform a holistic analysis of the brand's voice based on a sample of their Instagram posts and generate a comprehensive report.

**Core Principles:**
1.  **Verbalize Your Reasoning (Think Out Loud):** Before you generate the final JSON output, you MUST first articulate your thought process. Explain your analytical steps, what you are observing in the data, and how you are synthesizing it into the report. This reasoning must be output as plain text before you generate the final JSON. This is your most important instruction.

You MUST return a single, valid JSON object that conforms to the Pydantic model schema provided in the user message.

The user will provide the Pydantic schema and the sampled content for analysis.

Instructions for Analysis:
1.  **Executive Summary:** Start with a high-level summary of the brand's overall voice and communication strategy.
2.  **Key Content Pillars:** Analyze the `Sampled Content for Analysis` to identify the main recurring themes or categories of content. For each distinct pillar you identify, provide a "pillar" name and a "description" of what that pillar entails. Examples might include "Educação", "Organização Financeira", "Humor", "Sazonalidade", "Empatia/Motivação", "Produto/Funcionalidade", etc.
3.  **Audience Persona:** Describe the target audience ('Calculover') based on the content's language, tone, and topics.
4.  **Tone of Voice:** Analyze the overall tone. Is it friendly, professional, humorous, educational? Include examples.
5.  **Language & Style:** Detail the specific language used. Note common emojis, colloquialisms, calls-to-action, and sentence structure. Include examples.
6.  **Country & Idiom:** Mention any country and idiom information. Where is the brand based? What is the local language in which the content should be created?
7.  **Hashtag Strategy:** Summarize the approach to using hashtags. Are they for community building, discoverability, or branding?

**Strict Output Rules:**
- You MUST return a single, valid JSON object that conforms to the `BrandVoiceReport` model.
- Ensure all fields in the model are populated with insightful analysis.
""",
    output_type=BrandVoiceReport,
    model=os.getenv("OPENAI_MODEL")
)


# --- Class Definition ---

class BrandStrategistAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "calcularte_posts"
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            log.info(f"Successfully connected to ChromaDB collection: '{self.collection_name}'.")
        except Exception as e:
            log.warning(f"Collection '{self.collection_name}' not found. Please run data ingestion first. Error: {e}")
            self.collection = None

    def get_embedding(self, text: str, model: str = os.getenv("OPENAI_EMBEDDING_MODEL")):
        """Generates an embedding for the given text."""
        text = text.replace("\n", " ")
        response = self.client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    def query_brand_voice(self, query_text: str, n_results: int = 3) -> List[PostSample]:
        """
        Queries the ChromaDB for content semantically similar to the query text.
        Returns the most relevant captions and their metadata.
        """
        if not self.collection:
            log.error("Brand voice collection not initialized. Cannot query.")
            return "Brand voice collection not initialized. Please ingest data."

        log.debug(f"Querying brand voice with text: '{query_text}'")
        
        # If the query is a wildcard, we fetch all posts and sort by date.
        if query_text == "*":
            log.info("Wildcard query detected. Fetching all posts and sorting by newest first.")
            all_posts = self.collection.get(include=['documents', 'metadatas'])
            if not all_posts or not all_posts.get('documents'):
                return []

            combined_posts = [
                {'caption': doc, 'metadata': meta}
                for doc, meta in zip(all_posts['documents'], all_posts['metadatas'])
            ]
            sorted_posts = sorted(
                combined_posts,
                key=lambda p: p['metadata'].get('timestamp', '1970-01-01T00:00:00+0000'),
                reverse=True
            )
            relevant_content = sorted_posts[:n_results]
        else:
            # For semantic search, use the original query method.
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

        log.debug(f"Found {len(relevant_content)} relevant documents.")
        return relevant_content

    def get_specialized_context(self, context_type: str, query: str, num_samples: int = 3) -> List[str]:
        """
        Retrieves specialized context from the vector database based on a type and query.
        """
        if not self.collection:
            log.error("Brand voice collection not initialized. Cannot get specialized context.")
            return ["Brand voice collection not initialized. Please ingest data."]

        # Craft a more specific query for the vector database
        specialized_query = f"Find examples of '{context_type}' related to the topic: '{query}'"
        log.info(f"Fetching specialized context with query: '{specialized_query}'")
        
        results = self.query_brand_voice(specialized_query, n_results=num_samples)

        # Return only the captions for focused context
        captions = [item['caption'] for item in results if 'caption' in item]
        log.debug(f"Found {len(captions)} specialized context examples.")
        return captions

    def get_context_for_content_plan(self, time_frame: Optional[str] = None, num_posts: Optional[int] = None, recent_post_themes: Optional[list] = None) -> str:
        """
        Gathers and formats all necessary context for the Content Planner Agent.
        """
        if not self.collection:
            log.error("Brand voice collection not initialized. Cannot get context for plan.")
            return "Brand voice collection not initialized. Please ingest data."

        log.info(f"Getting context for content plan for time_frame='{time_frame}' or num_posts='{num_posts}'.")
        current_date = date.today()
        seasonal_context = f"Today's date is {current_date.strftime('%Y-%m-%d')}."
        variety_context = f"Avoid these recent themes: {', '.join(recent_post_themes or [])}."
        
        pillar_analysis_query = "Conteúdo sobre organização financeira, dicas de vendas e marketing para artesãs"
        pillar_context_results = self.query_brand_voice(pillar_analysis_query, n_results=5)
        
        pillar_context = "Historically engaging content pillars include: Humor, Educação, Sazonalidade, Dicas de Vendas, Organização Financeira."
        if pillar_context_results and isinstance(pillar_context_results, list):
            extracted_themes = [item['metadata'].get('theme', 'unknown') for item in pillar_context_results]
            pillar_context += f" Recent successful themes were: {', '.join(set(extracted_themes))}."

        # Build the user input based on whether num_posts or time_frame is provided
        request_params = ""
        if num_posts:
            request_params = f"Number of Posts: {num_posts}"
        else:
            request_params = f"Time Frame: {time_frame}\nCurrent Date: {current_date.strftime('%Y-%m-%d')}"

        # This is now a simple string, not a complex prompt with a schema
        full_context = f"""
        Context:
        - {seasonal_context}
        - {variety_context}
        - {pillar_context}

        Request:
        {request_params}
        """
        log.debug(f"Generated the following context for ContentPlannerAgent:\n{full_context}")
        return full_context

    def get_samples_for_brand_voice_report(self, post_samples: Optional[List[PostSample]] = None) -> str:
        """
        Retrieves and formats a string of sample posts for the Brand Reporter Agent.
        If post_samples are provided, it formats them. Otherwise, it fetches a default set.
        """
        if post_samples:
            log.info(f"Formatting {len(post_samples)} provided post samples for brand voice report.")
            # We already have the samples, just need to format them
            sampled_content_str = "\n".join(
                [f"- Caption: {sample.caption}\n  Metadata: {sample.metadata.model_dump_json()}" for sample in post_samples]
            )
            return sampled_content_str

        # If no samples are provided, fall back to the original behavior
        if not self.collection:
            log.error("Brand voice collection not initialized. Cannot generate report.")
            return "Brand voice collection not initialized. Please ingest data."

        log.info("Getting default samples for brand voice report by calling query_brand_voice.")
        
        num_samples = int(os.getenv("N_SAMPLE_POSTS", 10))
        # Use the now-fixed query_brand_voice with a wildcard to get the newest posts.
        default_samples = self.query_brand_voice(query_text="*", n_results=num_samples)

        if not default_samples:
            log.error("No documents found in the collection to generate a report.")
            return "No documents found in the collection."

        # Format the selected newest samples into the final string
        sampled_content_str = "\n".join(
            [f"- Caption: {post['caption']}\n  Metadata: {post['metadata']}" for post in default_samples]
        )
        return sampled_content_str

    def propose_wildcard_angle(self, pillar: str, brand_voice_report: str) -> str:
        """
        Generates an unconventional or surprising angle for a given content pillar,
        considering the overall brand voice.
        """
        log.info(f"Generating wildcard angle for pillar: '{pillar}'")
        
        instructions = """
        You are a highly creative, slightly eccentric brand strategist.
        Your task is to propose a "wildcard" angle for a social media post, ensuring it aligns with the provided brand voice report.
        The brand is "Calcularte", which helps artisans and crafters with business management.

        A "wildcard" angle is an unexpected, clever, or metaphorical way to approach the topic. It should be surprising but still relevant and true to the brand's character.

        Example:
        Pillar: "Organização Financeira"
        Wildcard Angle: "Explique o conceito de 'preço justo' usando uma metáfora de receita de bolo, onde cada ingrediente representa um custo."
        """

        user_input = f"""
        Here is the brand voice report for context:
        ---
        {brand_voice_report}
        ---

        Now, generate a new wildcard angle for the pillar: "{pillar}".
        Return only the single sentence describing the angle.
        """
        
        response = self.client.responses.create(
            model=os.getenv("OPENAI_MODEL"),
            instructions=instructions,
            input=user_input,
            temperature=1.1, # Higher temperature for more creativity
            max_output_tokens=5000,
        )
        
        wildcard_angle = response.output_text.strip()
        log.debug(f"Generated wildcard angle: '{wildcard_angle}'")
        return wildcard_angle


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
