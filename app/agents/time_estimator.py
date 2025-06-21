"""
Recipe Time Estimator Agent - Estimates total cooking/prep time from recipe instructions.
"""

import re
import logging
from typing import Dict, Any
from langchain.schema import HumanMessage
from app.utils.prompts import RECIPE_TIME_ESTIMATOR_PROMPT
from app.utils.gemini_llm import GeminiLLM  # ✅ Gemini wrapper

logger = logging.getLogger("recipe_time_estimator")
logger.setLevel(logging.INFO)

class RecipeTimeEstimatorAgent:
    def __init__(self, llm: GeminiLLM):  # ✅ Gemini-compatible
        self.llm = llm
    
    def estimate_time(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate total cooking/prep time from recipe instructions.
        """
        instructions = state.get("recipe_instructions", [])
        if not instructions:
            state["estimated_cook_time"] = None
            state["time_estimation_complete"] = True
            return state
        
        prompt = RECIPE_TIME_ESTIMATOR_PROMPT.format(
            instructions="\n".join(f"{i+1}. {step}" for i, step in enumerate(instructions))
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        logger.info("LLM response:\n%s", response.content)
        
        estimated_time = self._parse_time_response(response.content)
        
        state.update({
            "estimated_cook_time": estimated_time,
            "time_estimation_complete": True
        })
        
        return state
    
    def _parse_time_response(self, response: str) -> int:
        """
        Parse the LLM response to extract the estimated time in minutes.
        """
        match = re.search(r'(\d+)\s*minutes?', response, re.IGNORECASE)
        if match:
            return int(match.group(1))
        else:
            return None
