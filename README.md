# 🍳 Pantry Recipe Generator

🔗 **Live App:** [nicklausdachef.streamlit.app](https://nicklausdachef.streamlit.app/)

An AI-powered recipe generator that eliminates mealtime decision fatigue and reduces food waste. Tell it what's in your pantry, and it generates **up to 3 unique recipe options** displayed side by side — each using only the ingredients you actually have. Pick the one that sounds best and start cooking.

## Features

- **Multi-Recipe Generation** — Get up to 3 distinct recipes at once, displayed side by side for easy comparison
- **Ingredient-Flexible** — Each recipe uses a smart subset of your ingredients; no need to use everything
- **Configurable Servings** — Scale recipes from 1 to 12 servings
- **Time Constraints** — Filter by available cooking time (15 / 30 / 45 / 60 mins)
- **Cuisine Preference** — Choose from 10+ cuisine styles or leave it open
- **Strict Adherence** — The agent never hallucinates ingredients you didn't provide (basic staples like salt, pepper, oil, and water are assumed)
- **Formatted Output** — Every recipe includes title, prep/cook time, ingredient list with measurements, step-by-step instructions, and a chef's tip

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.5 Flash |
| Backend | Python + `google-generativeai` SDK |
| Frontend | Streamlit |
| Config | python-dotenv |

## Quick Start

### 1. Clone & branch

```bash
git clone https://github.com/nicklausyu/recipe-generator.git
cd recipe-generator
git checkout feature/pantry-recipe-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

```bash
cp .env.example .env
# Edit .env and replace the placeholder with your Gemini API key
```

> Get a free Gemini API key at https://aistudio.google.com/apikey

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
recipe-generator/
├── app.py              # Streamlit UI
├── engine.py           # Gemini recipe generation engine
├── config.py           # Configuration, system prompt, constants
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── .gitignore
└── README.md
```

## How It Works

1. The user enters ingredients, cooking time, cuisine preference, and serving size in the Streamlit UI.
2. `engine.py` constructs a user prompt and sends it to **Gemini 2.5 Flash** with a strict system prompt defined in `config.py`.
3. The system prompt enforces ingredient adherence — the model may only use listed ingredients plus basic staples (salt, pepper, oil, water).
4. The model returns up to 3 distinct recipes (fewer if the ingredients can't support 3 reasonable options), each using a different subset of the provided ingredients.
5. Recipes are displayed side by side in the browser so the user can compare and pick their favourite.
