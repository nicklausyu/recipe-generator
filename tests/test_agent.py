"""
Unit tests for the recipe generation agent.
Tests cover prompt construction and validation logic without making real API calls.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from agent import RecipeRequest, build_user_prompt, generate_recipe


class TestRecipeRequest:
    def test_default_optional_fields_are_none(self):
        req = RecipeRequest(ingredients="eggs, butter")
        assert req.max_time_minutes is None
        assert req.cuisine is None

    def test_all_fields_set(self):
        req = RecipeRequest(ingredients="chicken, garlic", max_time_minutes=30, cuisine="Italian")
        assert req.ingredients == "chicken, garlic"
        assert req.max_time_minutes == 30
        assert req.cuisine == "Italian"

    def test_invalid_max_time_raises(self):
        with pytest.raises(ValueError, match="max_time_minutes"):
            RecipeRequest(ingredients="eggs", max_time_minutes=0)

    def test_negative_max_time_raises(self):
        with pytest.raises(ValueError, match="max_time_minutes"):
            RecipeRequest(ingredients="eggs", max_time_minutes=-10)

    def test_max_time_above_limit_raises(self):
        with pytest.raises(ValueError, match="max_time_minutes"):
            RecipeRequest(ingredients="eggs", max_time_minutes=300)


class TestBuildUserPrompt:
    def test_ingredients_only(self):
        req = RecipeRequest(ingredients="spaghetti, miso, butter, garlic")
        prompt = build_user_prompt(req)
        assert "spaghetti, miso, butter, garlic" in prompt
        assert "minutes" not in prompt
        assert "cuisine" not in prompt.lower()

    def test_with_time_constraint(self):
        req = RecipeRequest(ingredients="eggs", max_time_minutes=30)
        prompt = build_user_prompt(req)
        assert "30 minutes" in prompt

    def test_with_cuisine(self):
        req = RecipeRequest(ingredients="rice, chicken", cuisine="Asian")
        prompt = build_user_prompt(req)
        assert "Asian" in prompt

    def test_with_all_constraints(self):
        req = RecipeRequest(ingredients="pasta, tomato", max_time_minutes=15, cuisine="Italian")
        prompt = build_user_prompt(req)
        assert "pasta, tomato" in prompt
        assert "15 minutes" in prompt
        assert "Italian" in prompt


class TestGenerateRecipe:
    def test_raises_value_error_without_api_key(self):
        req = RecipeRequest(ingredients="eggs")
        with patch.dict("os.environ", {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="No OpenAI API key"):
                generate_recipe(req, api_key=None)

    def test_returns_recipe_on_success(self):
        req = RecipeRequest(ingredients="spaghetti, garlic, olive oil")
        mock_recipe = "## Garlic Spaghetti\n\n**Prep Time:** 5 minutes\n**Cook Time:** 15 minutes\n\n### Ingredients\n- 200g spaghetti\n- 4 cloves garlic\n- 2 tbsp olive oil\n- Salt and pepper to taste\n\n### Instructions\n1. Boil pasta.\n2. Sauté garlic in oil.\n3. Combine and serve."

        mock_message = MagicMock()
        mock_message.content = mock_recipe
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = generate_recipe(req, api_key="sk-test-key")

        assert result == mock_recipe
        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "spaghetti, garlic, olive oil" in messages[1]["content"]

    def test_passes_time_and_cuisine_to_prompt(self):
        req = RecipeRequest(ingredients="chicken", max_time_minutes=30, cuisine="Asian")

        mock_message = MagicMock()
        mock_message.content = "## Fast Asian Chicken\n..."
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            generate_recipe(req, api_key="sk-test-key")

        user_content = mock_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        assert "30 minutes" in user_content
        assert "Asian" in user_content

    def test_cannot_generate_response_passed_through(self):
        req = RecipeRequest(ingredients="sand")
        cannot_msg = "CANNOT_GENERATE: These ingredients cannot form a reasonable meal."

        mock_message = MagicMock()
        mock_message.content = cannot_msg
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = generate_recipe(req, api_key="sk-test-key")

        assert result.startswith("CANNOT_GENERATE:")
