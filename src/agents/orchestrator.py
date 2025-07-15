from typing import List, Dict, Any
from src.agents.base import BaseAgent
from src.agents.brand_strategist import BrandStrategistAgent
from src.agents.creative_director import CreativeDirectorAgent, PostIdea
from src.agents.copywriter import CopywriterAgent
from src.agents.art_director import ArtDirectorAgent, ImagePrompt
from src.agents.reviewer import ReviewerAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.brand_strategist = BrandStrategistAgent()
        self.creative_director = CreativeDirectorAgent()
        self.copywriter = CopywriterAgent()
        self.art_director = ArtDirectorAgent()
        self.reviewer = ReviewerAgent()

    def _get_brand_context(self, query: str) -> Dict[str, Any]:
        """Fetches relevant brand context using the BrandStrategistAgent."""
        print(f"Orchestrator: Fetching brand context for query: '{query}'...")
        context_results = self.brand_strategist.query_brand_voice(query, n_results=5)
        
        # Process context_results into a more usable dictionary format for other agents
        brand_context = {
            "relevant_posts": [],
            "tone_examples": [],
            "hashtag_examples": [],
            "general_brand_info": "Calcularte helps artisans and confectioners manage finances, pricing, and business organization."
        }

        if isinstance(context_results, str): # Error from BrandStrategistAgent
            print(f"Orchestrator: Error fetching brand context: {context_results}")
            return brand_context # Return empty context

        for item in context_results:
            brand_context["relevant_posts"].append(item['caption'])
            brand_context["tone_examples"].append(item['caption']) # Use captions as tone examples
            if item['metadata'].get('hashtags'):
                brand_context["hashtag_examples"].extend(item['metadata']['hashtags'].split(', ')) # Split string back to list

        # Deduplicate hashtags
        brand_context["hashtag_examples"] = list(set(brand_context["hashtag_examples"]))
        
        print("Orchestrator: Brand context fetched.")
        return brand_context

    def generate_ideas(self, content_pillar: str, num_ideas: int = 3) -> List[PostIdea]:
        """
        Generates new post ideas by coordinating with the CreativeDirectorAgent.
        """
        print(f"Orchestrator: Generating {num_ideas} ideas for content pillar: '{content_pillar}'...")
        brand_context = self._get_brand_context(content_pillar)
        ideas = self.creative_director.brainstorm_ideas(content_pillar, brand_context, num_ideas)
        print("Orchestrator: Ideas generated.")
        return ideas

    def develop_post(self, idea: PostIdea, num_image_prompts: int = 3) -> Dict[str, Any]:
        """
        Develops a full post (caption + image prompts) based on a selected idea.
        """
        print(f"Orchestrator: Developing post for idea: '{idea.title}'...")
        
        # Step 1: Get brand context relevant to the idea
        brand_context = self._get_brand_context(idea.title + " " + idea.defense_of_idea)

        # Step 2: Generate caption using CopywriterAgent
        print("Orchestrator: Writing caption...")
        caption = self.copywriter.write_caption(idea.title, idea.defense_of_idea, brand_context)
        print("Orchestrator: Caption written.")

        # Step 3: Generate image prompts using ArtDirectorAgent
        print("Orchestrator: Generating image prompts...")
        image_prompts = self.art_director.generate_image_prompts(
            post_concept=idea.title,
            caption=caption,
            brand_context=brand_context,
            num_prompts=num_image_prompts # This will be num_content_prompts + 1 CTA prompt
        )
        print("Orchestrator: Image prompts generated.")

        return {
            "idea": idea,
            "caption": caption,
            "image_prompts": [p.prompt for p in image_prompts] if image_prompts else []
        }

    def refine_content(self, component_type: str, original_content: str, user_feedback: str, post_context: Dict[str, Any]) -> str:
        """
        Refines a specific content component using the ReviewerAgent.
        """
        print(f"Orchestrator: Refining {component_type} with user feedback...")
        brand_context = self._get_brand_context(user_feedback) # Get context based on feedback
        
        revised_content = self.reviewer.refine_content(original_content, user_feedback, brand_context)
        print(f"Orchestrator: {component_type} refined.")
        return revised_content

if __name__ == "__main__":
    # Example usage (for testing purposes)
    orchestrator = OrchestratorAgent()

    # Test 1: Generate Ideas
    print("\n--- Testing Idea Generation ---")
    ideas = orchestrator.generate_ideas("Organização Financeira", num_ideas=1)
    if ideas:
        selected_idea = ideas[0]
        print(f"\nSelected Idea: {selected_idea.title}")
        
        # Test 2: Develop Post
        print("\n--- Testing Post Development ---")
        full_post = orchestrator.develop_post(selected_idea, num_image_prompts=2) # 2 content + 1 CTA
        print("\n--- Full Post Developed ---")
        print(f"Caption:\n{full_post['caption']}")
        print("\nImage Prompts:")
        for i, prompt in enumerate(full_post['image_prompts']):
            print(f"Prompt {i+1}: {prompt}")

        # Test 3: Refine Content (example: refine caption)
        print("\n--- Testing Content Refinement ---")
        original_caption = full_post['caption']
        feedback = "Make the call to action more prominent and add an emoji related to saving money."
        revised_caption = orchestrator.refine_content("caption", original_caption, feedback, full_post)
        print(f"\nRevised Caption:\n{revised_caption}")
    else:
        print("No ideas generated, cannot proceed with full post development.")
