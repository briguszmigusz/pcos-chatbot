import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from groq import Groq
from pathlib import Path
import random
from dotenv import load_dotenv
import os

# ==========================
# INSERT YOUR API KEY
# ==========================
load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================
# DB PATH
# ==========================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "chroma_db"

# ==========================
# INIT
# ==========================
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client(
    Settings(
        persist_directory=str(DB_PATH),
        is_persistent=True
    )
)

try:
    collection = client.get_collection("recipes")

    if collection.count() == 0:
        raise Exception("Empty collection")

except Exception as e:
    print("Collection missing or empty. Running ingestion...")
    from ingest import ingest_recipes
    ingest_recipes()
    collection = client.get_collection("recipes")

# ==========================
# UTILITIES
# ==========================
def safe_get(meta, key):
    return meta.get(key, 0)

def per_serving(meta, key):
    total = safe_get(meta, key)
    servings = safe_get(meta, "servings")
    if servings == 0:
        return 0
    return total / servings

def get_all_recipes():
    data = collection.get()
    recipes = []
    for doc, meta in zip(data["documents"], data["metadatas"]):
        recipes.append({"text": doc, "metadata": meta})
    return recipes

# ==========================
# RAG
# ==========================
def search_recipes(query):
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    return results["documents"][0]

def ask_llm(question, docs=None):

    PCOS_CONTEXT = """
You are a nutrition assistant specialized in PCOS (Polycystic Ovary Syndrome)
and insulin resistance.
Respond in a supportive, respectful, non-judgmental tone.
Avoid shame-based language about weight or body image.

Core medical context:

PCOS is a hormonal condition often associated with:
- Insulin resistance
- Elevated androgens
- Irregular cycles
- Fatigue
- Weight gain difficulty
- Inflammation

Important nutrition principles for PCOS:

1. Blood sugar stability is critical.
2. High-protein meals improve satiety and glucose control.
3. High-fiber carbohydrates are preferred over refined carbs.
4. Healthy fats support hormonal balance.
5. Large glucose spikes may worsen symptoms.
6. Sustainable calorie control may support weight management when appropriate.
7. Strength training and movement improve insulin sensitivity.

Guidelines for answering:
- Provide educational guidance only.
- Do NOT diagnose or prescribe medication.
- Encourage consultation with healthcare professionals.
- Be supportive and empathetic in tone.
- Focus on practical lifestyle advice.

This assistant supports women managing PCOS and insulin resistance.
"""

    recipe_context = ""
    if docs:
        recipe_context = "\n\nRelevant recipe information:\n" + "\n\n".join(docs)

    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": PCOS_CONTEXT},
            {"role": "user", "content": recipe_context + "\n\nUser question:\n" + question}
        ],
    )

    return response.choices[0].message.content

# ==========================
# SMART WEEK PLANNER
# ==========================
def build_week_plan(max_cal=1500, min_cal=1200, min_protein=100):

    recipes = get_all_recipes()

    breakfasts = [r for r in recipes if r["metadata"]["meal_type"] == "breakfast"]
    lunches = [r for r in recipes if r["metadata"]["meal_type"] == "lunch"]
    dinners = [r for r in recipes if r["metadata"]["meal_type"] == "dinner"]
    snacks = [r for r in recipes if r["metadata"]["meal_type"] == "snack"]

    week_plan = []
    used_combos = set()
    day = 1

    for block in range(4):

        random.shuffle(breakfasts)
        random.shuffle(lunches)
        random.shuffle(dinners)

        valid_found = False

        for lunch in lunches:
            for dinner in dinners:

                combo_key = (
                    lunch["metadata"]["title"],
                    dinner["metadata"]["title"]
                )

                if combo_key in used_combos:
                    continue

                for breakfast in breakfasts:

                    base_cal = (
                        safe_get(breakfast["metadata"], "calories_per_serving") +
                        safe_get(lunch["metadata"], "calories_per_serving") +
                        safe_get(dinner["metadata"], "calories_per_serving")
                    )

                    base_protein = (
                        per_serving(breakfast["metadata"], "protein_g") +
                        per_serving(lunch["metadata"], "protein_g") +
                        per_serving(dinner["metadata"], "protein_g")
                    )

                    base_carbs = (
                        per_serving(breakfast["metadata"], "carbs_g") +
                        per_serving(lunch["metadata"], "carbs_g") +
                        per_serving(dinner["metadata"], "carbs_g")
                    )

                    base_fat = (
                        per_serving(breakfast["metadata"], "fat_g") +
                        per_serving(lunch["metadata"], "fat_g") +
                        per_serving(dinner["metadata"], "fat_g")
                    )

                    final_cal = base_cal
                    final_protein = base_protein
                    final_carbs = base_carbs
                    final_fat = base_fat
                    chosen_snack = None

                    if base_cal < min_cal or base_protein < min_protein:

                        snacks_sorted = sorted(
                            snacks,
                            key=lambda s: per_serving(s["metadata"], "protein_g"),
                            reverse=True
                        )

                        for snack in snacks_sorted:

                            snack_cal = safe_get(snack["metadata"], "calories_per_serving")
                            snack_protein = per_serving(snack["metadata"], "protein_g")
                            snack_carbs = per_serving(snack["metadata"], "carbs_g")
                            snack_fat = per_serving(snack["metadata"], "fat_g")

                            new_cal = base_cal + snack_cal
                            new_protein = base_protein + snack_protein

                            if (
                                new_cal <= max_cal and
                                new_cal >= min_cal and
                                new_protein >= min_protein
                            ):
                                final_cal = new_cal
                                final_protein = new_protein
                                final_carbs += snack_carbs
                                final_fat += snack_fat
                                chosen_snack = snack
                                break

                    if (
                        min_cal <= final_cal <= max_cal and
                        final_protein >= min_protein
                    ):

                        used_combos.add(combo_key)

                        for repeat in range(2):
                            if day > 7:
                                break

                            week_plan.append({
                                "day": day,
                                "breakfast": breakfast,
                                "lunch": lunch,
                                "dinner": dinner,
                                "snack": chosen_snack,
                                "calories": round(final_cal, 1),
                                "protein": round(final_protein, 1),
                                "carbs": round(final_carbs, 1),
                                "fat": round(final_fat, 1)
                            })
                            day += 1

                        valid_found = True
                        break

                if valid_found:
                    break
            if valid_found:
                break

    return week_plan

# ==========================
# CLI
# ==========================
def chat():
    print("\n🥗 PCOS Meal Planning Chatbot Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask: ")

        if question.lower() == "exit":
            break

        if "week" in question.lower():
            week_plan = build_week_plan()
            for day in week_plan:
                print(f"\nDay {day['day']}")
                print("Breakfast:", day["breakfast"]["metadata"]["title"])
                print("Lunch:", day["lunch"]["metadata"]["title"])
                print("Dinner:", day["dinner"]["metadata"]["title"])
                if day.get("snack"):
                    print("Snack:", day["snack"]["metadata"]["title"])
                print("Calories:", day["calories"])
                print("Protein:", day["protein"])
            continue

        docs = search_recipes(question)
        answer = ask_llm(question, docs)
        print("\n" + answer + "\n")

if __name__ == "__main__":
    chat()