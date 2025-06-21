# app/agents/input_validator.py

import re
import logging
from typing import Dict, Any
from langchain.schema import HumanMessage
from app.utils.gemini_llm import GeminiLLM  # ✅ Use your Gemini wrapper
from app.utils.prompts import INPUT_VALIDATOR_PROMPT

logger = logging.getLogger("input_validator")
logger.setLevel(logging.INFO)

class InputValidatorAgent:
    def __init__(self, llm: GeminiLLM):  # ✅ Type updated
        self.llm = llm
        
    def validate_inputs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean user inputs.
        """
        logger.info("Validating inputs with state: %s", state)
        ingredients = state.get("ingredients", "")
        dietary_preferences = state.get("dietary_preferences", [])
        max_time = state.get("max_time", 60)
        
        # Create prompt
        prompt = INPUT_VALIDATOR_PROMPT.format(
            ingredients=ingredients,
            dietary_preferences=", ".join(dietary_preferences),
            max_time=max_time
        )
        
        # Get LLM response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info("Raw LLM response:\n%s", response.content)
        
        # Parse response
        parsed_result = self._parse_validation_response(response.content)
        
        # Update state
        state.update({
            "cleaned_ingredients": parsed_result.get("cleaned_ingredients", []),
            "valid_preferences": parsed_result.get("valid_preferences", []),
            "validation_issues": parsed_result.get("issues", "None"),
            "validation_complete": True
        })
        
        return state

    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response for validation results.
        """
        result = {}

        # Cleaned Ingredients
        ingredients_match = re.search(r'CLEANED_INGREDIENTS:\s*\n?(\[.*?\]|.*?)(?:\n|$)', response, re.DOTALL)
        if ingredients_match:
            ingredients_str = ingredients_match.group(1).strip()
            if ingredients_str.startswith('[') and ingredients_str.endswith(']'):
                ingredients_str = ingredients_str[1:-1]
            result["cleaned_ingredients"] = [
                item.strip().strip('"\'') for item in ingredients_str.split(',') if item.strip()
            ]

        # Valid Preferences
        prefs_match = re.search(r'VALID_PREFERENCES:\s*\n?(\[.*?\]|.*?)(?:\n|$)', response, re.DOTALL)
        if prefs_match:
            prefs_str = prefs_match.group(1).strip()
            if prefs_str.startswith('[') and prefs_str.endswith(']'):
                prefs_str = prefs_str[1:-1]
            result["valid_preferences"] = [
                item.strip().strip('"\'') for item in prefs_str.split(',') if item.strip()
            ]

        # Issues
        issues_match = re.search(r'ISSUES:\s*(.*?)(?:\n|$)', response)
        if issues_match:
            result["issues"] = issues_match.group(1).strip()

        return result
