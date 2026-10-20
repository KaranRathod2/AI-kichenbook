import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-3.5-flash"


def generate_recipe(
    ingredients: list[str], cuisine: str, diet: str, servings: int, extra: str
) -> str:
    """Generate a practical recipe with the requested ingredients and preferences."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "No Gemini API key was found. Add GEMINI_API_KEY=your_key to a .env file."
        )

    client = genai.Client(api_key=api_key)
    prompt = f"""
Create one clear, delicious recipe using these ingredients: {", ".join(ingredients)}.
Cuisine or style: {cuisine or "Any"}.
Dietary requirements: {diet or "None"}.
Servings: {servings}.
Additional requests: {extra or "None"}.

Use this structure: recipe title, brief description, prep/cook/total time,
ingredients with quantities, numbered cooking instructions, and helpful tips.
Respect the dietary requirements. Do not claim an ingredient is safe for an
allergy unless that can be guaranteed; include a cross-contamination reminder
when relevant.
""".strip()

    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    if not response.text:
        raise RuntimeError("Gemini returned an empty recipe. Please try again.")
    return response.text


st.set_page_config(page_title="AI Recipe Studio", page_icon="🍲", layout="centered")
st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(160deg, #fffaf2 0%, #f4f8f1 100%);
            color: #263326; }
        h1, h2, h3, p, label, [data-testid="stWidgetLabel"] {
            color: #263326 !important;
        }
    .block-container { max-width: 850px; padding-top: 2.5rem; }
    [data-testid="stForm"] { background: rgba(255,255,255,.82); padding: 1.3rem;
      border: 1px solid #e8eadf; border-radius: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍲 AI Recipe Studio")
st.write("Tell us what you have, and Gemini will turn it into a recipe.")

with st.form("recipe_form"):
    ingredients_text = st.text_input(
        "Ingredients *",
        placeholder="e.g. chicken, rice, broccoli, garlic",
        help="Separate ingredients with commas.",
    )
    col1, col2 = st.columns(2)
    with col1:
        cuisine = st.text_input("Cuisine or style", placeholder="e.g. Italian")
    with col2:
        diet = st.text_input(
            "Dietary needs", placeholder="e.g. vegetarian, gluten-free"
        )
    col3, col4 = st.columns(2)
    with col3:
        servings = st.number_input("Servings", min_value=1, max_value=20, value=2)
    with col4:
        extra = st.text_input("Anything else?", placeholder="e.g. ready in 30 minutes")
    submitted = st.form_submit_button(
        "✨ Generate my recipe", type="primary", use_container_width=True
    )

if submitted:
    ingredients = [item.strip() for item in ingredients_text.split(",") if item.strip()]
    if not ingredients:
        st.warning("Enter at least one ingredient to get started.")
    else:
        try:
            with st.spinner("Creating your recipe..."):

                recipe = generate_recipe(ingredients, cuisine, diet, int(servings), extra)
            st.success("Your recipe is ready!")
            st.markdown(recipe)
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Could not generate the recipe: {error}")
