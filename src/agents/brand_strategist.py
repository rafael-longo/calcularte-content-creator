import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Load environment variables
load_dotenv()

class PlannedPost(BaseModel):
    day_or_sequence: str # e.g., "Monday", "Post 1"
    pillar: str
    reasoning: str

class ContentPlan(BaseModel):
    plan: List[PlannedPost]

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
        Generates a strategic content plan based on seasonality, historical data, and recent posts.
        """
        if not self.collection:
            # Fallback or error handling if the collection isn't ready
            return ContentPlan(plan=[])

        # 1. Analyze Time & Seasonality (Simplified for this example)
        # In a real scenario, this would involve a more complex logic to map dates to events.
        seasonal_context = f"Today's date is {current_date.strftime('%Y-%m-%d')}. The requested plan is for the next '{time_frame}'."
        
        # 2. Ensure Variety
        variety_context = ""
        if recent_post_themes:
            themes = ", ".join(recent_post_themes)
            variety_context = f"To ensure variety, avoid topics similar to these recent posts: {themes}."

        # 3. Identify Top Pillars (using a simple query for demonstration)
        # This could be made more sophisticated by analyzing engagement metrics over time.
        pillar_analysis_query = "Conteúdo sobre organização financeira, dicas de vendas e marketing para artesãs"
        pillar_context_results = self.query_brand_voice(pillar_analysis_query, n_results=5)
        
        pillar_context = "Historically engaging content pillars include: Humor, Educação, Sazonalidade, Dicas de Vendas, Organização Financeira."
        if pillar_context_results and isinstance(pillar_context_results, list):
            extracted_themes = [item['metadata'].get('theme', 'unknown') for item in pillar_context_results]
            pillar_context += f" Recent successful themes were: {', '.join(set(extracted_themes))}."

        # 4. Synthesize Plan using LLM
        system_prompt = f"""
        You are a Brand Strategist for 'Calcularte', a brand that helps artisans and crafters with business management.
        Your task is to create a content plan based on the provided context.
        Return a JSON object that follows this Pydantic model, inside a 'plan' key:
        class PlannedPost(BaseModel):
            day_or_sequence: str # e.g., "Monday", "Post 1"
            pillar: str
            reasoning: str

        class ContentPlan(BaseModel):
            plan: List[PlannedPost]

        Context:
        - {seasonal_context}
        - {variety_context}
        - {pillar_context}

        Instructions:
        1.  **Analyze Time & Seasonality:** Based on the current date and time frame, identify key seasonal opportunities.
        2.  **Ensure Variety:** Review recent post themes to avoid repetition.
        3.  **Identify Top Pillars:** Analyze the brand context to determine historically engaging content pillars.
        4.  **Synthesize Plan:** Combine these insights to create a balanced and timely content plan. Justify each choice in the 'reasoning' field.

        **Strict Output Rules:**
        - If the requested `time_frame` is 'day', you MUST generate a plan containing exactly one (1) `PlannedPost` item. The `day_or_sequence` field for this item MUST be the day of the week corresponding to the provided `current_date`.
        - If the requested `time_frame` is 'week', you MUST generate a plan containing multiple `PlannedPost` items, typically for days of the week, including the weekend (e.g., Monday, Wednesday, Friday, Sunday).
        - If the requested `time_frame` is 'month', you MUST generate a plan that covers the main themes and events for the entire month, sequenced logically.        
        """

        user_prompt = f"Generate a content plan for the next {time_frame}."

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Manually parse the JSON response into the Pydantic model
        try:
            response_json = response.choices[0].message.content
            content_plan = ContentPlan.model_validate_json(response_json)
            return content_plan
        except Exception as e:
            print(f"Error parsing content plan from LLM response: {e}")
            return ContentPlan(plan=[])

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
