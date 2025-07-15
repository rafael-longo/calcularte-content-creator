import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB client
# This will create a local ChromaDB instance in the current directory
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Get or create a collection
collection_name = "calcularte_posts"
try:
    collection = chroma_client.get_collection(name=collection_name)
except:
    collection = chroma_client.create_collection(name=collection_name)

def get_embedding(text: str, model: str = "text-embedding-3-small"):
    """Generates an embedding for the given text using OpenAI's API."""
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def ingest_data(file_path: str):
    """
    Loads data from a JSONL file, generates embeddings, and stores them in ChromaDB.
    """
    print(f"Ingesting data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            caption = data.get("caption", "")
            post_id = data.get("id", f"post_{i}") # Use 'id' field or generate a unique one

            if caption:
                embedding = get_embedding(caption)
                # Store the original caption and other metadata
                metadata = {
                    "caption": caption,
                    "hashtags": ", ".join(data.get("hashtags", [])), # Convert list to string
                    "timestamp": data.get("timestamp"),
                    "likesCount": data.get("likesCount"),
                    "commentsCount": data.get("commentsCount"),
                    "url": data.get("url")
                }
                collection.add(
                    embeddings=[embedding],
                    documents=[caption], # Storing the caption as the document
                    metadatas=[metadata],
                    ids=[post_id]
                )
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1} posts.")
    print(f"Data ingestion complete from {file_path}.")

if __name__ == "__main__":
    # Use the sample dataset for development
    sample_dataset_path = "dataset_sample.jsonl"
    ingest_data(sample_dataset_path)
