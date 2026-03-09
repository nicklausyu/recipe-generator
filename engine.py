"""
Pantry Recipe Generator – Gemini-powered recipe engine.
"""

from __future__ import annotations

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, RECIPE_SEPARATOR


def _configure_client() -> None:
    """Configure the Gemini SDK with the API key."""
    genai.configure(api_key=GEMINI_API_KEY)


def build_user_prompt(
    ingredients: list[str],
    max_time: str | None = None,
    cuisine: str | None = None,
    servings: int = 2,
) -> str:
    """Compose the user-facing prompt sent to the model.

    Args:
        ingredients: List of ingredient strings the user has available.
        max_time: Optional time constraint, e.g. "under 30 mins".
        cuisine: Optional cuisine preference, e.g. "Italian".
        servings: Number of servings to scale the recipe to.

    Returns:
        A formatted prompt string.
    """
    parts: list[str] = [
        "I have the following ingredients: "
        + ", ".join(i.strip() for i in ingredients if i.strip())
        + "."
    ]

    if max_time:
        parts.append(f"Time constraint: {max_time}.")
    if cuisine:
        parts.append(f"Preferred cuisine: {cuisine}.")

    parts.append(f"Servings: {servings}.")
    parts.append("Please give me 3 different recipe options I can make right now.")
    return " ".join(parts)


def _parse_recipes(raw_text: str) -> list[str]:
    """Split the raw model output into individual recipe strings.

    Falls back to returning the full text as a single recipe if the
    separator is not found.
    """
    recipes = [r.strip() for r in raw_text.split(RECIPE_SEPARATOR) if r.strip()]
    return recipes


def generate_recipes(
    ingredients: list[str],
    max_time: str | None = None,
    cuisine: str | None = None,
    servings: int = 2,
) -> list[str]:
    """Call Gemini and return a list of generated recipes as Markdown strings.

    Args:
        ingredients: List of ingredient strings.
        max_time: Optional time constraint.
        cuisine: Optional cuisine preference.
        servings: Number of servings to scale the recipe to.

    Returns:
        List of generated recipe texts in Markdown format.

    Raises:
        ValueError: If no ingredients are provided or API key is missing.
        RuntimeError: If the Gemini API call fails.
    """
    if not ingredients or all(i.strip() == "" for i in ingredients):
        raise ValueError("Please provide at least one ingredient.")

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it to a .env file or export it as an environment variable."
        )

    _configure_client()

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
    )

    user_prompt = build_user_prompt(ingredients, max_time, cuisine, servings)

    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                max_output_tokens=4096,
            ),
        )
        return _parse_recipes(response.text)
    except Exception as exc:
        raise RuntimeError(f"Recipe generation failed: {exc}") from exc
