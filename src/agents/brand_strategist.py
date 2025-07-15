import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
