"""
Pantry Recipe Generator – Gemini-powered recipe engine.
"""

from __future__ import annotations

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT


def _configure_client() -> None:
    """Configure the Gemini SDK with the API key."""
    genai.configure(api_key=GEMINI_API_KEY)


def build_user_prompt(
    ingredients: list[str],
    max_time: str | None = None,
    cuisine: str | None = None,
) -> str:
    """Compose the user-facing prompt sent to the model.

    Args:
        ingredients: List of ingredient strings the user has available.
        max_time: Optional time constraint, e.g. "under 30 mins".
        cuisine: Optional cuisine preference, e.g. "Italian".

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

    parts.append("Please give me a recipe I can make right now.")
    return " ".join(parts)


def generate_recipe(
    ingredients: list[str],
    max_time: str | None = None,
    cuisine: str | None = None,
) -> str:
    """Call Gemini and return the generated recipe as Markdown.

    Args:
        ingredients: List of ingredient strings.
        max_time: Optional time constraint.
        cuisine: Optional cuisine preference.

    Returns:
        Generated recipe text in Markdown format.

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

    user_prompt = build_user_prompt(ingredients, max_time, cuisine)

    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return response.text
    except Exception as exc:
        raise RuntimeError(f"Recipe generation failed: {exc}") from exc
