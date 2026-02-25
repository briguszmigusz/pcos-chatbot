import yaml
import chromadb
from chromadb.config import Settings
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ==========================
# Paths (CLOUD SAFE)
# ==========================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

DB_PATH = ROOT_DIR / "chroma_db"
RECIPES_PATH = ROOT_DIR / "recipes_raw"

# ==========================
# Embedding Model
# ==========================
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==========================
# Chroma Client
# ==========================
client = chromadb.Client(
    Settings(
        persist_directory=str(DB_PATH),
        is_persistent=True
    )
)

collection = client.get_or_create_collection("recipes")


def load_recipe(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---")

    if len(parts) < 3:
        return None, None

    yaml_block = parts[1]
    body = parts[2]

    metadata = yaml.safe_load(yaml_block)

    return body.strip(), metadata


def ingest_recipes():
    files = list(RECIPES_PATH.glob("*.md"))

    if not files:
        print("No recipes found in recipes_raw folder!")
        return

    # Avoid duplicate ingestion
    if collection.count() > 0:
        print("Collection already contains data. Skipping ingestion.")
        return

    for i, file in enumerate(files):
        text, metadata = load_recipe(file)

        if not text:
            continue

        embedding = model.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[file.stem]  # unique per recipe
        )

        print(f"Added: {metadata.get('title', file.stem)}")

    print("\nAll recipes ingested!")
    print("Total stored in DB:", collection.count())


if __name__ == "__main__":
    ingest_recipes()