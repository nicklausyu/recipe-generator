"""
Recipe Generator Agent

Uses the OpenAI API to generate tailored recipes based on user-provided ingredients
and optional constraints (cooking time, cuisine preference).
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """You are a professional chef and recipe creation assistant.
Your task is to generate a single, creative recipe strictly based on the ingredients the user provides.

STRICT RULES:
1. You may ONLY use the ingredients the user has listed.
2. You are allowed to assume the user has basic staples: salt, pepper, and cooking oil (olive oil or vegetable oil).
3. Do NOT add any other ingredients not provided by the user.
4. Do NOT suggest substitutions or additional shopping items.

OUTPUT FORMAT:
You must respond in exactly the following format, with no additional text before or after:

## {Recipe Title}

**Prep Time:** {X minutes}
**Cook Time:** {Y minutes}

### Ingredients
- {quantity} {ingredient}
(list all ingredients with estimated measurements for standard 2-person portions)

### Instructions
1. {Step 1}
2. {Step 2}
(continue numbered steps until complete)

If the provided ingredients cannot form a reasonable meal, respond with exactly:
"CANNOT_GENERATE: {brief reason}"
"""


@dataclass
class RecipeRequest:
    ingredients: str
    max_time_minutes: int | None = None
    cuisine: str | None = None

    def __post_init__(self):
        if self.max_time_minutes is not None and not (1 <= self.max_time_minutes <= 240):
            raise ValueError("max_time_minutes must be between 1 and 240.")


def build_user_prompt(request: RecipeRequest) -> str:
    parts = [f"Ingredients I have: {request.ingredients}"]
    if request.max_time_minutes:
        parts.append(f"Total cooking time must be under {request.max_time_minutes} minutes")
    if request.cuisine:
        parts.append(f"Preferred cuisine: {request.cuisine}")
    return "\n".join(parts)


def generate_recipe(request: RecipeRequest, api_key: str | None = None) -> str:
    """
    Generate a recipe based on the provided ingredients and constraints.

    Args:
        request: RecipeRequest with ingredients and optional constraints.
        api_key: OpenAI API key. Falls back to OPENAI_API_KEY env variable.

    Returns:
        A formatted recipe string, or an error message prefixed with "CANNOT_GENERATE:".

    Raises:
        ValueError: If no API key is provided.
        openai.OpenAIError: If the API call fails.
    """
    resolved_key = api_key or os.getenv("OPENAI_API_KEY")
    if not resolved_key:
        raise ValueError(
            "No OpenAI API key provided. Set the OPENAI_API_KEY environment variable "
            "or pass api_key to generate_recipe()."
        )

    client = OpenAI(api_key=resolved_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request)},
        ],
        temperature=0.7,
        max_tokens=1024,
        timeout=30,
    )

    return response.choices[0].message.content.strip()
