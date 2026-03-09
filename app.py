"""
Pantry Recipe Generator – Streamlit UI
"""

import streamlit as st
from engine import generate_recipes

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pantry Recipe Generator",
    page_icon="🍳",
    layout="wide",
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🍳 Pantry Recipe Generator")
st.markdown(
    "Tell me what's in your kitchen and I'll create a recipe — "
    "**no extra grocery trips required.**"
)
st.divider()

# ── Ingredient input ─────────────────────────────────────────────────────────
ingredients_text = st.text_area(
    "🥕 What ingredients do you have?",
    placeholder="e.g. spaghetti, miso, butter, garlic, parmesan",
    help="Enter ingredients separated by commas.",
    height=100,
)

# ── Constraint toggles ──────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    time_options = [
        "No limit",
        "Under 15 mins",
        "Under 30 mins",
        "Under 45 mins",
        "Under 60 mins",
    ]
    selected_time = st.selectbox("⏱️ Available cooking time", time_options)

with col2:
    cuisine_options = [
        "Any",
        "Italian",
        "Mexican",
        "Chinese",
        "Japanese",
        "Indian",
        "Thai",
        "French",
        "Mediterranean",
        "American",
        "Korean",
    ]
    selected_cuisine = st.selectbox("🌍 Preferred cuisine", cuisine_options)

# ── Generate button ──────────────────────────────────────────────────────────
generate = st.button("🍽️ Generate Recipes", type="primary", use_container_width=True)

if generate:
    # Parse ingredients
    ingredients = [
        i.strip() for i in ingredients_text.split(",") if i.strip()
    ]

    if not ingredients:
        st.error("Please enter at least one ingredient.")
    else:
        max_time = None if selected_time == "No limit" else selected_time
        cuisine = None if selected_cuisine == "Any" else selected_cuisine

        with st.spinner("👨‍🍳 Cooking up some recipes…"):
            try:
                recipes = generate_recipes(
                    ingredients=ingredients,
                    max_time=max_time,
                    cuisine=cuisine,
                )
                st.session_state["recipes"] = recipes
                st.session_state["selected_recipe"] = None
            except ValueError as exc:
                st.error(str(exc))
            except RuntimeError as exc:
                st.error(f"Something went wrong: {exc}")

# ── Display recipes side by side ─────────────────────────────────────────────
if "recipes" in st.session_state and st.session_state["recipes"]:
    recipes = st.session_state["recipes"]
    st.divider()
    st.subheader("Pick a recipe!")

    cols = st.columns(len(recipes))
    for idx, (col, recipe_md) in enumerate(zip(cols, recipes)):
        with col:
            with st.container(border=True, height=600):
                st.markdown(recipe_md)

    # ── Selection row ────────────────────────────────────────────────────────
    st.divider()
    sel_cols = st.columns(len(recipes))
    for idx, col in enumerate(sel_cols):
        with col:
            if st.button(
                f"✅ I'll make Recipe {idx + 1}",
                key=f"select_{idx}",
                use_container_width=True,
            ):
                st.session_state["selected_recipe"] = idx

    if st.session_state.get("selected_recipe") is not None:
        chosen = st.session_state["selected_recipe"]
        st.divider()
        st.success(f"Great choice! Here's your full recipe 👇")
        st.markdown(recipes[chosen])

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Pantry Recipe Generator · Powered by Gemini · "
    "Basic staples (salt, pepper, oil, water) are assumed available."
)
