from typing import List
from pydantic import BaseModel, Field
from src.agents.base import BaseAgent

class PostIdea(BaseModel):
    title: str = Field(description="A catchy, engaging title for the idea.")
    content_pillar: str = Field(description="The primary strategic category the post fits into.")
    defense_of_idea: str = Field(description="A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience.")
    expected_results: str = Field(description="The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').")

class CreativeDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def brainstorm_ideas(self, content_pillar: str, brand_context: dict, num_ideas: int = 3) -> List[PostIdea]:
        """
        Brainstorms new, on-brand post concepts based on a given content pillar and brand context.
        """
        formatted_context = self._format_context(brand_context)
        
        system_prompt = f"""
        You are the Creative Director Agent for 'Calcularte'. Your function is to brainstorm new, on-brand post concepts.
        
        Based on the provided content pillar and brand context, generate {num_ideas} potential post ideas.
        
        Each idea must be a clear, structured plan containing four key sections:
        - Title: A catchy, engaging title for the idea.
        - Content Pillar: The primary strategic category the post fits into.
        - Defense of Idea: A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience.
        - Expected Results: The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').

        Ensure the ideas are creative, relevant to the 'Calculover' audience, and align with the Calcularte brand voice.
        
        {formatted_context}

        Output format must be a JSON array of PostIdea objects.
        """

        user_message = f"Brainstorm {num_ideas} post ideas for the content pillar: '{content_pillar}'."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Use structured output by defining response_model
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8, # Higher temperature for creativity
                response_model=List[PostIdea] # This tells the LLM to output a list of PostIdea objects
            )
            return response
        except Exception as e:
            print(f"Error generating ideas: {e}")
            return []

if __name__ == "__main__":
    # Example usage (for testing purposes)
    creative_director = CreativeDirectorAgent()
    
    # Dummy brand context for testing
    dummy_context = {
        "tone_voice": "empathetic, didactic, inspirador",
        "target_audience": "artesãs e confeiteiras, empreendedoras, buscam organização financeira e precificação justa",
        "content_pillars": ["Precificação", "Organização Financeira", "Marketing para Artesanato"],
        "successful_patterns": ["dicas práticas", "histórias de sucesso", "perguntas e respostas"]
    }

    print("Brainstorming ideas for 'Organização Financeira':")
    ideas = creative_director.brainstorm_ideas("Organização Financeira", dummy_context, num_ideas=2)
    
    if ideas:
        for i, idea in enumerate(ideas):
            print(f"\n--- Idea {i+1} ---")
            print(f"Title: {idea.title}")
            print(f"Content Pillar: {idea.content_pillar}")
            print(f"Defense: {idea.defense_of_idea}")
            print(f"Expected Results: {idea.expected_results}")
    else:
        print("No ideas generated.")
