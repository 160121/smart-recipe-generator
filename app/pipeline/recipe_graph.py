# app/pipeline/recipe_graph.py
from langgraph.graph import StateGraph
from app.utils.gemini_llm import GeminiLLM
from app.agents.input_validator import InputValidatorAgent
from app.agents.ingredient_filter import IngredientFilterAgent
from app.agents.recipe_generator import RecipeGeneratorAgent
from app.agents.time_estimator import RecipeTimeEstimatorAgent
from app.agents.health_tips import HealthTipsAgent
from app.agents.feedback_logger import FeedbackLoggerAgent
from app.agents.alternate_recipe import AlternateRecipeAgent
import logging

logger = logging.getLogger("Recipe_pipeline")

class RecipeGraph:
    def __init__(self):
        self.llm = GeminiLLM() 
        # Initialize agents
        self.validator = InputValidatorAgent(self.llm)
        self.filter_agent = IngredientFilterAgent(self.llm)
        self.generator = RecipeGeneratorAgent(self.llm)
        self.time_estimator = RecipeTimeEstimatorAgent(self.llm)
        self.tips_agent = HealthTipsAgent(self.llm)
        self.feedback_logger = FeedbackLoggerAgent()
        self.alternate_agent = AlternateRecipeAgent(self.llm)
        # Define LangGraph-compatible node functions
        def validate_node(state: dict) -> dict:
            logger.info("✅ Running InputValidationAgent...")
            return self.validator.validate_inputs(state)

        def filter_node(state: dict) -> dict:
            logger.info("🔍 Running PreferenceFilterAgent...")
            return self.filter_agent.filter_ingredients(state)

        def generate_node(state: dict) -> dict:
            logger.info("🍳 Running RecipeGenerationAgent...")
            return self.generator.generate_recipe(state)

        def estimate_time_node(state: dict) -> dict:
            logger.info("⏱️ Running TimeEstimatorAgent...")
            return self.time_estimator.estimate_time(state)

        def tips_node(state: dict) -> dict:
            logger.info("💡 Running TipsAgent...")
            return self.tips_agent.generate_health_tips(state)

        def alternate_node(state: dict) -> dict:
            logger.info("🔄 Running AlternateRecipeAgent...")
            return self.alternate_agent.generate_alternate(state)
        def feedback_node(state: dict) -> dict:
            logger.info("📝 Logging user feedback...")
            return self.feedback_logger.log_feedback(state)

        # Build LangGraph state machine
        self.graph = StateGraph(dict)

        # Add nodes to the graph
        self.graph.add_node("validate", validate_node)
        self.graph.add_node("filter", filter_node)
        self.graph.add_node("generate", generate_node)
        self.graph.add_node("estimate_time", estimate_time_node)
        self.graph.add_node("tips", tips_node)
        self.graph.add_node("alternate", alternate_node)
        self.graph.add_node("feedback", feedback_node)

        # Define flow
        self.graph.set_entry_point("validate")
        self.graph.add_edge("validate", "filter")
        self.graph.add_edge("filter", "generate")
        self.graph.add_edge("generate", "estimate_time")
        self.graph.add_edge("estimate_time", "tips")
        def should_generate_alternate(state: dict) -> bool:
            return state.get("generate_alternate", False)

        self.graph.add_conditional_edges("tips", {
            "alternate": should_generate_alternate,
            "feedback": lambda state: not should_generate_alternate(state)
        })
        self.graph.add_edge("alternate", "feedback")
        self.graph.set_finish_point("feedback")

        # Compile graph
        self.recipe_chain = self.graph.compile()

    def generate_recipe(self, **kwargs) -> dict:
        """
        Wrapper to prepare input state and invoke the LangGraph pipeline.
        """
        state = {
            "ingredients": kwargs.get("ingredients", ""),
            "dietary_preferences": kwargs.get("dietary_preferences", []),
            "max_time": kwargs.get("max_time", 60),
            "uploaded_image": kwargs.get("uploaded_image", None),
            "generate_alternate": kwargs.get("generate_alternate", False),  # <-- Pass this flag to control alternate
            "generate_shopping_list": kwargs.get("generate_shopping_list", False)  # <-- Pass this flag to control shopping list
        }
        logger.info("🚀 Starting recipe generation pipeline...")
        try:
            result = self.recipe_chain.invoke(state)
            result["status"] = "success"
            logger.info("✅ Recipe generation pipeline completed.")
            return result
        except Exception as e:
            logger.exception("❗ Recipe pipeline failed.")
            return {
                "status": "error",
                "error": str(e),
                "trace": "Exception in recipe generation pipeline"
            }

    def get_feedback_statistics(self) -> dict:
        return self.feedback_logger.get_feedback_stats()