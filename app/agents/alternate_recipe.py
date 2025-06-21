"""
Alternate Recipe Agent - Generates alternative recipes using similar ingredients.
"""

from langchain.schema import HumanMessage
from app.utils.gemini_llm import GeminiLLM  # ✅ Updated import
from app.utils.prompts import ALTERNATE_RECIPE_PROMPT
import re
from typing import Dict, Any
import logging

logger = logging.getLogger("AlternateRecipeAgent")


def _join_multiline_items(lines, bullet_pattern):
    items = []
    current = ""
    for line in lines:
        if re.match(bullet_pattern, line.strip()):
            if current:
                items.append(current.strip())
            current = re.sub(bullet_pattern, '', line.strip(), count=1).strip()
        else:
            current += " " + line.strip()
    if current:
        items.append(current.strip())
    return items


class AlternateRecipeAgent:
    def __init__(self, llm: GeminiLLM):  # ✅ Updated LLM class
        self.llm = llm

    def generate_alternate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an alternate recipe using similar ingredients.
        """
        original_recipe = state.get("recipe_name", "")
        ingredients = state.get("filtered_ingredients", [])
        dietary_preferences = state.get("valid_preferences", [])

        prompt = ALTERNATE_RECIPE_PROMPT.format(
            original_recipe=original_recipe,
            ingredients=", ".join(ingredients),
            dietary_preferences=", ".join(dietary_preferences)
        )

        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info(f"LLM Response: {response.content}")

        parsed_result = self._parse_alternate_response(response.content)

        state.update({
            "alternate_recipe_name": parsed_result.get("alternate_recipe_name", "Alternative Recipe"),
            "alternate_cuisine_style": parsed_result.get("cuisine_style", "Fusion"),
            "alternate_ingredients": parsed_result.get("ingredients_needed", []),
            "alternate_instructions": parsed_result.get("instructions", []),
            "alternate_difficulty": parsed_result.get("difficulty", "Medium"),
            "alternate_servings": parsed_result.get("servings", "4"),
            "alternate_flavor_profile": parsed_result.get("flavor_profile", ""),
            "alternate_recipe_complete": True
        })

        return state

    def _parse_alternate_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response for alternate recipe details."""
        result = {}

        name_match = re.search(r'ALTERNATE_RECIPE_NAME:\s*(.*?)(?:\n|$)', response)
        if name_match:
            result["alternate_recipe_name"] = name_match.group(1).strip()

        style_match = re.search(r'CUISINE_STYLE:\s*(.*?)(?:\n|$)', response)
        if style_match:
            result["cuisine_style"] = style_match.group(1).strip()

        ingredients_match = re.search(r'INGREDIENTS_NEEDED:\s*(.*?)(?=\n[A-Z_]+:|\Z)', response, re.DOTALL)
        if ingredients_match:
            ingredients_str = ingredients_match.group(1).strip()
            if ingredients_str.startswith('[') and ingredients_str.endswith(']'):
                ingredients_str = ingredients_str[1:-1]
                result["ingredients_needed"] = [
                    item.strip().strip('"\'') for item in ingredients_str.split(',') if item.strip()
                ]
            else:
                raw_lines = [item for item in ingredients_str.split('\n') if item.strip()]
                result["ingredients_needed"] = _join_multiline_items(raw_lines, bullet_pattern=r"^[-]")
        else:
            result["ingredients_needed"] = ["Default ingredients: Chicken, Eggs, Tomatoes, Onions"]

        instructions_match = re.search(r'INSTRUCTIONS:\s*(.*?)(?=\n[A-Z_]+:|\Z)', response, re.DOTALL)
        if instructions_match:
            instructions_str = instructions_match.group(1).strip()
            if instructions_str.startswith('[') and instructions_str.endswith(']'):
                instructions_str = instructions_str[1:-1]
                result["instructions"] = [
                    item.strip().strip('"\'') for item in instructions_str.split(',') if item.strip()
                ]
            else:
                raw_lines = [item for item in instructions_str.split('\n') if item.strip()]
                result["instructions"] = _join_multiline_items(raw_lines, bullet_pattern=r"^\d+\.")
        else:
            result["instructions"] = [
                "Cook chicken until browned and cooked through.",
                "Scramble eggs, sauté onions, and mix with tomatoes."
            ]

        difficulty_match = re.search(r'DIFFICULTY:\s*(.*?)(?:\n|$)', response)
        if difficulty_match:
            result["difficulty"] = difficulty_match.group(1).strip()

        servings_match = re.search(r'SERVINGS:\s*(.*?)(?:\n|$)', response)
        if servings_match:
            result["servings"] = servings_match.group(1).strip()

        flavor_match = re.search(r'FLAVOR_PROFILE:\s*(.*?)(?:\n|$)', response, re.DOTALL)
        if flavor_match:
            result["flavor_profile"] = flavor_match.group(1).strip()

        return result
