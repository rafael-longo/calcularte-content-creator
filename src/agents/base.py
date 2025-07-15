import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAgent:
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def _call_llm(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000):
        """
        Helper method to call the OpenAI LLM.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {e}"

    def _format_context(self, context: dict) -> str:
        """
        Helper method to format brand context for LLM prompts.
        """
        formatted_context = "Brand Context:\n"
        if context:
            for key, value in context.items():
                if isinstance(value, list):
                    formatted_context += f"- {key.replace('_', ' ').title()}: {', '.join(value)}\n"
                elif isinstance(value, dict):
                    formatted_context += f"- {key.replace('_', ' ').title()}:\n"
                    for sub_key, sub_value in value.items():
                        formatted_context += f"  - {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                else:
                    formatted_context += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            formatted_context += "No specific brand context provided.\n"
        return formatted_context
