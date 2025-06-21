"""
Health Tips Agent - Provides nutritional insights and health tips.
"""

from langchain.schema import HumanMessage
from app.utils.gemini_llm import GeminiLLM  # ✅ Updated import
from app.utils.prompts import HEALTH_TIPS_PROMPT
import re
from typing import Dict, Any


class HealthTipsAgent:
    def __init__(self, llm: GeminiLLM):  # ✅ Updated class type
        self.llm = llm
        
    def generate_health_tips(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate health tips and nutritional insights for the recipe.
        """
        recipe_name = state.get("recipe_name", "")
        ingredients = state.get("filtered_ingredients", [])
        dietary_preferences = state.get("valid_preferences", [])
        
        # Create prompt
        prompt = HEALTH_TIPS_PROMPT.format(
            recipe_name=recipe_name,
            ingredients=", ".join(ingredients),
            dietary_preferences=", ".join(dietary_preferences)
        )
        
        # Get LLM response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse response
        parsed_result = self._parse_health_response(response.content)
        
        # Update state
        state.update({
            "nutritional_benefits": parsed_result.get("nutritional_benefits", ""),
            "health_tips": parsed_result.get("health_tips", ""),
            "healthier_suggestions": parsed_result.get("healthier_suggestions", ""),
            "health_warnings": parsed_result.get("warnings", "None"),
            "health_tips_complete": True
        })
        
        return state
    
    def _parse_health_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response for health information.
        """
        result = {}
        
        # Extract nutritional benefits
        benefits_match = re.search(r'NUTRITIONAL_BENEFITS:\s*(.*?)(?=HEALTH_TIPS:|$)', response, re.DOTALL)
        if benefits_match:
            result["nutritional_benefits"] = benefits_match.group(1).strip()
        
        # Extract health tips
        tips_match = re.search(r'HEALTH_TIPS:\s*(.*?)(?=HEALTHIER_SUGGESTIONS:|$)', response, re.DOTALL)
        if tips_match:
            result["health_tips"] = tips_match.group(1).strip()
        
        # Extract healthier suggestions
        suggestions_match = re.search(r'HEALTHIER_SUGGESTIONS:\s*(.*?)(?=WARNINGS:|$)', response, re.DOTALL)
        if suggestions_match:
            result["healthier_suggestions"] = suggestions_match.group(1).strip()
        
        # Extract warnings
        warnings_match = re.search(r'WARNINGS:\s*(.*?)(?:\n|$)', response)
        if warnings_match:
            result["warnings"] = warnings_match.group(1).strip()
        
        return result
