from typing import List
from pydantic import BaseModel, Field
from agents import Agent

class PostIdea(BaseModel):
    title: str = Field(description="A catchy, engaging title for the idea.")
    content_pillar: str = Field(description="The primary strategic category the post fits into.")
    defense_of_idea: str = Field(description="A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience.")
    expected_results: str = Field(description="The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').")

# This is now a configured agent instance, not a class.
# The logic from the old `brainstorm_ideas` method is now encapsulated in the agent's instructions.
creative_director_agent = Agent(
    name="Creative Director Agent",
    instructions="""
You are the Creative Director Agent for 'Calcularte'. Your function is to brainstorm new, on-brand post concepts.

Based on the provided content pillar and brand context, generate potential post ideas.

Each idea must be a clear, structured plan containing four key sections:
- Title: A catchy, engaging title for the idea.
- Content Pillar: The primary strategic category the post fits into.
- Defense of Idea: A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience.
- Expected Results: The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').

Ensure the ideas are creative, relevant to the 'Calculover' audience, and align with the Calcularte brand voice.

The user will provide the content pillar, the number of ideas to generate, and the brand context.

Output format must be a JSON array of PostIdea objects.
""",
    output_type=List[PostIdea],
    model="gpt-4.1-mini", # Explicitly set model
    model_settings={"temperature": 0.8}
)
