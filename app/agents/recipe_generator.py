"""
Recipe Generator Agent - Creates complete recipes from ingredients.
"""

import re
import logging
from typing import Dict, Any
from langchain.schema import HumanMessage
from app.utils.gemini_llm import GeminiLLM  # ✅ Use Gemini wrapper
from app.utils.prompts import RECIPE_GENERATION_PROMPT

logger = logging.getLogger("recipe_generator")
logger.setLevel(logging.INFO)

class RecipeGeneratorAgent:
    def __init__(self, llm: GeminiLLM):  # ✅ Replace ChatOpenAI
        self.llm = llm
        
    def generate_recipe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete recipe from filtered ingredients.
        """
        ingredients = state.get("filtered_ingredients", [])
        dietary_preferences = state.get("valid_preferences", [])
        max_time = state.get("max_time", 60)

        # Create prompt
        prompt = RECIPE_GENERATION_PROMPT.format(
            ingredients=", ".join(ingredients),
            dietary_preferences=", ".join(dietary_preferences),
            max_time=max_time
        )

        # Get LLM response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info("Raw LLM response:\n%s", response.content)

        # Parse response
        parsed_result = self._parse_recipe_response(response.content)

        # Compute missed ingredients
        user_ingredients = set(i.strip().lower() for i in ingredients)
        missed_ingredients = [
            ing for ing in parsed_result.get("ingredients", [])
            if not any(ui in ing.lower() for ui in user_ingredients)
        ]

        # Update state
        state.update({
            "recipe_title": parsed_result.get("title", "Delicious Recipe"),
            "recipe_ingredients": parsed_result.get("ingredients", []),
            "recipe_instructions": parsed_result.get("instructions", []),
            "missed_ingredients": missed_ingredients,
            "recipe_complete": True
        })

        return state
    
    def _parse_recipe_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response for recipe details.
        """
        result = {}
        
        # Extract title
        title_match = re.search(r"TITLE:\s*(.*)", response)
        result["title"] = title_match.group(1).strip() if title_match else "Delicious Recipe"
        
        # Extract ingredients list
        ingredients = []
        ingredients_match = re.search(r"INGREDIENTS:\s*((?:- .*\n?)+)", response)
        if ingredients_match:
            ingredients_text = ingredients_match.group(1)
            ingredients = [line.strip("- ").strip() for line in ingredients_text.strip().split("\n")]
        result["ingredients"] = ingredients
        
        # Extract instructions list
        instructions = []
        instructions_match = re.search(r"INSTRUCTIONS:\s*((?:\d+\..*\n?)+)", response)
        if instructions_match:
            instructions_text = instructions_match.group(1)
            instructions = [line.strip().split(". ", 1)[1].strip() for line in instructions_text.strip().split("\n") if ". " in line]
        result["instructions"] = instructions

        # Extract additional ingredients needed (optional)
        additional_ingredients = []
        additional_match = re.search(r"ADDITIONAL INGREDIENTS NEEDED:\s*((?:- .*\n?)*)", response, re.IGNORECASE)
        if additional_match:
            additional_text = additional_match.group(1)
            additional_ingredients = [line.strip("- ").strip() for line in additional_text.strip().split("\n") if line.strip()]
        result["additional_ingredients"] = additional_ingredients

        return result
