import pandas as pd
import os
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)

class FeedbackLoggerAgent:
    def __init__(self, log_file_path: str = "data/feedback_logs.csv"):
        self.log_file_path = log_file_path
        self._ensure_log_file_exists()

    def log_feedback(self, state: Dict[str, Any]) -> Dict[str, Any]:
        feedback_type = state.get("feedback_type")  # "thumbs_up" or "thumbs_down"
        recipe_name = state.get("recipe_title", "Unknown")
        ingredients = state.get("filtered_ingredients", [])
        dietary_preferences = state.get("valid_preferences", [])
        total_time = state.get("estimated_cook_time", "")

        if feedback_type not in ["thumbs_up", "thumbs_down"]:
            logging.warning("Invalid feedback_type; skipping feedback log.")
            state.update({
                "feedback_logged": False,
                "feedback_log_success": False
            })
            return state

        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "recipe_name": recipe_name,
            "ingredients": ", ".join(ingredients),
            "dietary_preferences": ", ".join(dietary_preferences),
            "total_time": total_time,
            "feedback_type": feedback_type,
        }

        success = self._append_to_csv(feedback_entry)
        state.update({
            "feedback_logged": success,
            "feedback_log_success": success
        })

        return state

    def _ensure_log_file_exists(self):
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        if not os.path.exists(self.log_file_path):
            df = pd.DataFrame(columns=[
                "timestamp", "recipe_name", "ingredients",
                "dietary_preferences", "total_time","feedback_type",
            ])
            df.to_csv(self.log_file_path, index=False)
            logging.info(f"Created new feedback log file at {self.log_file_path}")

    def _append_to_csv(self, feedback_entry: Dict[str, Any]) -> bool:
        try:
            df = pd.DataFrame([feedback_entry])
            df.to_csv(self.log_file_path, mode='a', header=False, index=False)
            logging.info("Feedback logged successfully.")
            return True
        except Exception as e:
            logging.error(f"Error logging feedback: {e}")
            return False

    def get_feedback_stats(self) -> Dict[str, Any]:
        try:
            df = pd.read_csv(self.log_file_path)
            if df.empty:
                return {"total_feedback": 0, "thumbs_up": 0, "thumbs_down": 0, "satisfaction_rate": 0}

            thumbs_up = len(df[df["feedback_type"] == "thumbs_up"])
            thumbs_down = len(df[df["feedback_type"] == "thumbs_down"])

            return {
                "total_feedback": len(df),
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "satisfaction_rate": round((thumbs_up / len(df)) * 100, 2)
            }
        except Exception as e:
            logging.error(f"Error reading feedback stats: {e}")
            return {"error": str(e)}
