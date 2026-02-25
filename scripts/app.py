import streamlit as st
from chatbot import build_week_plan, search_recipes, ask_llm
import base64
import os

# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="PCOS AI Meal Planner",
    layout="wide"
)

# ==============================
# Load Background Image
# ==============================
def load_bg_image():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_path = os.path.join(base_dir, "assets", "background.jpg")
    with open(bg_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = load_bg_image()

# ==============================
# CSS Styling (UNCHANGED)
# ==============================
st.markdown(f"""
<style>

/* Background */
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* Soft overlay */
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(255,255,255,0.65);
    z-index: 0;
}}

/* Content above overlay */
.block-container {{
    position: relative;
    z-index: 1;
    padding-top: 40px;
    padding-bottom: 40px;
}}

/* 🌿 Glass cards */
section.main > div > div > div > div[data-testid="stVerticalBlock"] {{
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}}

/* Title */
.main-title {{
    text-align: center;
    font-size: 40px;
    font-weight: 700;
    color: #2F4F4F;
    margin-bottom: 30px;
}}

.meal-title {{
    font-size: 20px;
    font-weight: 600;
    color: #355E5E;
    margin-bottom: 8px;
}}

.section-title {{
    font-size: 18px;
    font-weight: 600;
    color: #4F6F6F;
    margin-bottom: 12px;
}}

div[data-testid="stMetricValue"] {{
    font-size: 22px !important;
    color: #355E5E !important;
}}

div[data-testid="stMetricLabel"] {{
    font-size: 14px !important;
    color: #6B8E8E !important;
}}

section[data-testid="stSidebar"] {{
    background-color: rgba(233, 242, 238, 0.95);
}}

</style>
""", unsafe_allow_html=True)

# ==============================
# Title
# ==============================
st.markdown(
    '<div class="main-title">🌿 PCOS + Insulin Resistance AI Meal Planner</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; font-size: 14px; opacity: 0.8;">
        Personal GenAI project • PCOS-focused meal planning prototype
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================
# Sidebar
# ==============================
mode = st.sidebar.selectbox(
    "Mode",
    ["Weekly Meal Plan", "Ask About PCOS"]
)

# ==============================
# WEEKLY MODE
# ==============================
if mode == "Weekly Meal Plan":

    st.sidebar.markdown("### Constraints")

    max_cal = st.sidebar.number_input("Max Calories", 1300, 1800, 1500)
    min_cal = st.sidebar.number_input("Min Calories", 900, 1500, 1200)
    min_protein = st.sidebar.number_input("Min Protein (g)", 60, 150, 100)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        generate = st.button("✨Generate Weekly Plan✨", use_container_width=True)

    if generate:
        st.session_state.week_plan = build_week_plan(
            max_cal, min_cal, min_protein
        )

    if "week_plan" in st.session_state:

        for day in st.session_state.week_plan:

            st.markdown(f"### Day {day['day']}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="section-title">Meals</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="meal-title">🍳 Breakfast: {day["breakfast"]["metadata"]["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-title">🥗 Lunch: {day["lunch"]["metadata"]["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meal-title">🍲 Dinner: {day["dinner"]["metadata"]["title"]}</div>', unsafe_allow_html=True)

                if day.get("snack"):
                    st.markdown(f'<div class="meal-title">🍪 Snack: {day["snack"]["metadata"]["title"]}</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="section-title">Macros</div>', unsafe_allow_html=True)
                st.metric("Calories", f"{day['calories']} kcal")
                st.metric("Protein", f"{day['protein']} g")
                st.metric("Carbs", f"{day['carbs']} g")
                st.metric("Fat", f"{day['fat']} g")

            # ==============================
            # INLINE RECIPE Q&A
            # ==============================

            def recipe_block(title, meal_key):
                meal = day[meal_key]

                with st.expander(f"{title} Recipe"):
                    st.markdown(meal["text"])

                    q_key = f"{meal_key}_q_{day['day']}"
                    a_key = f"{meal_key}_a_{day['day']}"

                    question = st.text_input(
                        f"Ask about {meal['metadata']['title']}",
                        key=q_key
                    )

                    if st.button(
                        f"Ask about this {meal_key}",
                        key=f"{meal_key}_btn_{day['day']}"
                    ):
                        if question:
                            answer = ask_llm(question, [meal["text"]])
                            st.session_state[a_key] = answer

                    if a_key in st.session_state:
                        st.markdown("**Answer:**")
                        st.write(st.session_state[a_key])

            recipe_block("🍳 Breakfast", "breakfast")
            recipe_block("🥗 Lunch", "lunch")
            recipe_block("🍲 Dinner", "dinner")

            if day.get("snack"):
                recipe_block("🍪 Snack", "snack")

# ==============================
# ASK MODE (UNCHANGED)
# ==============================
elif mode == "Ask About PCOS":

    question = st.text_input("Ask something about PCOS:")

    if st.button("Ask") and question:
        docs = search_recipes(question)
        answer = ask_llm(question, docs)
        st.write(answer)

# ==============================
# Disclaimer
# ==============================
st.markdown("---")

st.markdown(
    """
    <div style="text-align: center; font-size: 13px; opacity: 0.85; max-width: 900px; margin: auto;">
        This application was developed as a personal GenAI learning project. 
        The meal plans and nutritional suggestions are generated automatically 
        and are intended for informational purposes only. 
        This tool does not provide medical advice and should not replace consultation 
        with a licensed healthcare professional.
    </div>
    """,
    unsafe_allow_html=True
)