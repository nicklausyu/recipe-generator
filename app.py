"""
Pantry Recipe Generator — Streamlit Web App

A conversational UI that lets users enter their available ingredients and
optional constraints (cooking time, cuisine) and get a tailored recipe.
"""

import streamlit as st

from agent import RecipeRequest, generate_recipe

st.set_page_config(
    page_title="Pantry Recipe Generator",
    page_icon="🍳",
    layout="centered",
)

st.title("🍳 Pantry Recipe Generator")
st.markdown(
    "Enter the ingredients you have on hand and get a tailored recipe — "
    "no extra shopping required!"
)

with st.form("recipe_form"):
    ingredients = st.text_area(
        "🥕 What ingredients do you have?",
        placeholder="e.g. spaghetti, miso, butter, garlic, eggs",
        height=100,
    )

    st.markdown("##### Optional constraints")
    col1, col2 = st.columns(2)

    with col1:
        time_options = {
            "Any": None,
            "Under 15 mins": 15,
            "Under 30 mins": 30,
            "Under 60 mins": 60,
        }
        time_label = st.selectbox("⏱️ Cooking time", options=list(time_options.keys()))
        max_time = time_options[time_label]

    with col2:
        cuisine_options = [
            "",
            "Italian",
            "Asian",
            "Mexican",
            "Mediterranean",
            "American",
            "French",
            "Indian",
        ]
        cuisine = st.selectbox("🌍 Cuisine preference", options=cuisine_options)

    api_key = st.text_input(
        "🔑 OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Your key is used only for this request and is never stored.",
    )

    submitted = st.form_submit_button("Generate Recipe 🚀", use_container_width=True)

if submitted:
    if not ingredients.strip():
        st.warning("Please enter at least one ingredient.")
    elif not api_key.strip():
        st.warning("Please enter your OpenAI API key.")
    else:
        with st.spinner("Generating your recipe…"):
            try:
                request = RecipeRequest(
                    ingredients=ingredients.strip(),
                    max_time_minutes=max_time,
                    cuisine=cuisine.strip() or None,
                )
                result = generate_recipe(request, api_key=api_key.strip())

                if result.startswith("CANNOT_GENERATE:"):
                    reason = result.replace("CANNOT_GENERATE:", "").strip()
                    st.error(
                        f"⚠️ Unable to generate a recipe with those ingredients: {reason}"
                    )
                else:
                    st.success("Here's your recipe!")
                    st.markdown(result)

            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"An error occurred while generating the recipe: {exc}")
