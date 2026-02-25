

# 🌿 PCOS + Insulin Resistance AI Meal Planner & ChatBot

A personal GenAI project designed to support women managing **PCOS (Polycystic Ovary Syndrome)** and **insulin resistance** through structured meal planning and AI-powered guidance.

This application combines:

* Retrieval-Augmented Generation (RAG)
* Constraint-based meal planning
* PCOS-aware LLM prompting
* A custom Streamlit interface

---

## ✨ Features

### 🗓 Weekly Meal Planning

* Calorie-constrained meal plans
* Minimum protein targets
* PCOS-friendly recipes
* Automated macro calculation
* Optional snack support

### 🤖 AI Recipe Q&A

* Ask questions directly under each recipe
* Context-aware answers using recipe text
* Session-based memory (does not lose the plan)

### 🩺 PCOS-Aware AI Assistant

* Built-in PCOS and insulin resistance knowledge
* Blood sugar stability principles
* High-protein guidance
* Educational-only medical guardrails

### 🎨 Custom UI

* Streamlit wide layout
* Custom background
* Responsive columns

---

## 🧠 Tech Stack

* **Python**
* **Streamlit**
* **ChromaDB** (vector database)
* **Sentence Transformers** (`all-MiniLM-L6-v2`)
* **Groq API** (LLaMA 3.1)
* **RAG architecture**

---

## 📂 Project Structure

```
assets/                # Background image
chroma_db/             # Persistent vector database (ignored in Git)
recipes_raw/           # Source recipes
recipes_validated/     # Cleaned/structured recipes
scripts/
    app.py             # Streamlit frontend
    chatbot.py         # Logic, LLM, RAG, meal planner
    ingest.py          # Recipe ingestion pipeline
.env                   # API key (NOT committed)
requirements.txt
```

---

## 🔐 Environment Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/briguszmigusz/pcos-chatbot
cd pcos-chatbot
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add Your API Key

Create a file called:

```
.env
```

Inside:

```
GROQ_API_KEY=your_api_key_here
```

⚠️ Never commit this file.
It is excluded via `.gitignore`.

---

### 5️⃣ Run The App

```bash
streamlit run scripts/app.py
```

---

## ⚙️ How It Works

### 1️⃣ Recipe Ingestion

Recipes are embedded using `SentenceTransformer` and stored in ChromaDB.

### 2️⃣ Meal Planning

A constraint-based selection system:

* Ensures calorie range
* Enforces minimum protein
* Supports leftovers
* Uses metadata-driven filtering

### 3️⃣ PCOS Knowledge Injection

The LLM is given structured PCOS context via a system prompt:

* Insulin resistance focus
* Blood sugar stabilization
* High-protein guidance
* Non-diagnostic safety framing

### 4️⃣ Inline Q&A

Recipe text is passed directly into the LLM for contextual answers without losing the meal plan.

---

## 🛡 Disclaimer

This application was developed as a **personal GenAI learning project**.

The meal plans and nutritional suggestions are generated automatically and are intended for informational purposes only.

This tool does **not** provide medical advice and should not replace consultation with a licensed healthcare professional.

---

## 💛 Importance of this Project

This project was created as a practical exploration of:

* Retrieval-Augmented Generation
* Structured prompt engineering
* Constraint-based planning
* Personalized AI interfaces

It is also personally meaningful, as it focuses on PCOS and insulin resistance management through sustainable nutrition principles.

---

## 🚀 Future Improvements

* Improved meal diversity logic
* Adding more recipes
* Grocery list aggregation
* Cycle-phase awareness
* Macro summary charts
* Public deployment
* User authentication
* PDF export

---

## 📌 License

Personal project. Not intended for medical use.

---
Feel free to reach out or connect with me on [LinkedIn](https://www.linkedin.com/in/brigi-bodi/)!