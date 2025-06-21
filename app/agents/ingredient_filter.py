"""
Ingredient Filter Agent - Applies dietary restrictions to ingredients.
"""

import re
import logging
from typing import Dict, Any
from langchain.schema import HumanMessage
from app.utils.gemini_llm import GeminiLLM 
from app.utils.prompts import INGREDIENT_FILTER_PROMPT

logger = logging.getLogger("ingredient_filter")
logger.setLevel(logging.INFO)

class IngredientFilterAgent:
    def __init__(self, llm: GeminiLLM):
        self.llm = llm
        
    def filter_ingredients(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter ingredients based on dietary preferences.
        """
        ingredients = state.get("cleaned_ingredients", [])
        dietary_preferences = state.get("valid_preferences", [])
        
        logger.info("Filtering ingredients: %s with dietary prefs: %s", ingredients, dietary_preferences)
        
        if not dietary_preferences:
            # No filtering needed
            state.update({
                "filtered_ingredients": ingredients,
                "removed_ingredients": [],
                "suggested_alternatives": [],
                "filtering_complete": True
            })
            logger.info("No dietary preferences provided, skipping filtering.")
            return state
        
        # Create prompt
        prompt = INGREDIENT_FILTER_PROMPT.format(
            ingredients=", ".join(ingredients),
            dietary_preferences=", ".join(dietary_preferences)
        )
        
        # Get LLM response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info("Raw LLM response:\n%s", response.content)
        
        # Parse response
        parsed_result = self._parse_filter_response(response.content)
        
        # Update state
        state.update({
            "filtered_ingredients": parsed_result.get("filtered_ingredients", ingredients),
            "removed_ingredients": parsed_result.get("removed_ingredients", []),
            "suggested_alternatives": parsed_result.get("suggested_alternatives", []),
            "filtering_complete": True
        })
        
        return state
    
    def _parse_filter_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response for filtering results.
        """
        result = {}

        def extract_list(label: str):
            pattern = rf'{label}:\s*\n?(\[.*?\]|.*?)(?:\n|$)'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content.startswith('[') and content.endswith(']'):
                    content = content[1:-1]
                return [item.strip().strip('"\'') for item in content.split(',') if item.strip()]
            return []

        result["filtered_ingredients"] = extract_list("FILTERED_INGREDIENTS")
        result["removed_ingredients"] = extract_list("REMOVED_INGREDIENTS")
        result["suggested_alternatives"] = extract_list("SUGGESTED_ALTERNATIVES")
        
        return result
