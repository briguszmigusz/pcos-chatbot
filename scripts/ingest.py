import yaml
import chromadb
from chromadb.config import Settings
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create persistent Chroma client
client = chromadb.Client(
    Settings(
        persist_directory="../chroma_db",
        is_persistent=True
    )
)

collection = client.get_or_create_collection("recipes")

def load_recipe(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    yaml_block = content.split("---")[1]
    body = content.split("---")[2]

    metadata = yaml.safe_load(yaml_block)

    return body.strip(), metadata

def ingest():
    folder = Path("../recipes_raw")

    files = list(folder.glob("*.md"))

    if not files:
        print(" No recipes found in recipes_validated folder!")
        return

    for i, file in enumerate(files):
        text, metadata = load_recipe(file)

        embedding = model.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(i)]
        )

        print(f"Added: {metadata['title']}")

    print("\n All recipes ingested!")
    print("Total stored in DB:", collection.count())

if __name__ == "__main__":
    ingest()