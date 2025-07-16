from typing import List
from pydantic import BaseModel, Field
from agents import Agent

class PostIdea(BaseModel):
    title: str = Field(description="A catchy, engaging title for the idea.")
    content_pillar: str = Field(description="The primary strategic category the post fits into.")
    defense_of_idea: str = Field(description="A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience.")
    expected_results: str = Field(description="The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').")

class GeneratedIdeas(BaseModel):
    ideas: List[PostIdea]

# This is now a configured agent instance, not a class.
# The logic from the old `brainstorm_ideas` method is now encapsulated in the agent's instructions.
creative_director_agent = Agent(
    name="Creative Director Agent",
    instructions="""
You are the Creative Director Agent for 'Calcularte'. Your function is to brainstorm new, on-brand post concepts.

Based on the provided content pillar and brand context, generate potential post ideas.

If the brand context includes a 'Strategic Context' section, you MUST use it as the primary guide for your brainstorming. This section provides the high-level strategic reasoning from the Brand Strategist, and your ideas should directly reflect that reasoning.

Each idea must be a clear, structured plan containing four key sections:
- Title: A catchy, engaging title for the idea.
- Content Pillar: The primary strategic category the post fits into. This should match the pillar from the 'Strategic Context' if provided.
- Defense of Idea: A brief justification explaining why this idea is relevant and valuable to the 'Calculover' audience, directly tying back to the reasoning provided in the 'Strategic Context'.
- Expected Results: The desired outcome of the post (e.g., 'High salvamentos', 'Strong emotional engagement', 'Drive conversions for X feature').

Ensure the ideas are creative, relevant to the 'Calculover' audience, and align with the Calcularte brand voice.

The user will provide the content pillar, the number of ideas to generate, and the brand context (which may include strategic context).

Output format must be a single JSON object that conforms to the `GeneratedIdeas` model, with the list of ideas nested under the `ideas` key.
""",
    output_type=GeneratedIdeas,
    model="gpt-4.1-mini"
)
