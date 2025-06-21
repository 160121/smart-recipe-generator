from langchain.llms.base import LLM
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import Any, List, Optional
from app.config import model, DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS


class GeminiLLM(LLM):
    """Custom LLM wrapper for Google Gemini API."""

    model_name: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = MAX_TOKENS

    @property
    def _llm_type(self) -> str:
        return "google_gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Gemini API."""
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                    # Gemini API currently does not support `stop` sequences directly
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"❌ Error calling Gemini API: {str(e)}")

    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """Invoke method for LangChain compatibility."""
        if isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], HumanMessage):
                prompt = messages[0].content
            else:
                prompt = str(messages[0])
        else:
            prompt = str(messages)

        response_content = self._call(prompt)
        return AIMessage(content=response_content)
