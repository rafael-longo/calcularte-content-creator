from typing import List, Dict, Any
from datetime import date
from agents import Runner
from src.agents_crew.brand_strategist import BrandStrategistAgent, ContentPlan, BrandVoiceReport
from src.agents_crew.creative_director import creative_director_agent, PostIdea
from src.agents_crew.copywriter import copywriter_agent
from src.agents_crew.art_director import art_director_agent, ImagePrompt
from src.agents_crew.reviewer import reviewer_agent

class OrchestratorAgent:
    def __init__(self):
        self.brand_strategist = BrandStrategistAgent()
        self.creative_director = creative_director_agent
        self.copywriter = copywriter_agent
        self.art_director = art_director_agent
        self.reviewer = reviewer_agent

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

    def plan_content(self, time_frame: str) -> ContentPlan:
        """
        Generates a strategic content plan by coordinating with the BrandStrategistAgent.
        """
        print(f"Orchestrator: Generating content plan for '{time_frame}'...")
        # In a real application, you might fetch recent post themes from a database.
        # For this example, we'll pass None.
        current_date = date.today()
        content_plan = self.brand_strategist.propose_content_plan(
            time_frame=time_frame,
            current_date=current_date,
            recent_post_themes=None 
        )
        print("Orchestrator: Content plan generated.")
        return content_plan

    def generate_brand_voice_report(self) -> str:
        """
        Generates and formats a comprehensive brand voice report.
        """
        print("Orchestrator: Generating brand voice report...")
        
        # 1. Trigger the report generation from the BrandStrategistAgent
        report_data = self.brand_strategist.generate_brand_voice_report()
        
        if not report_data or not report_data.executive_summary:
            return "Could not generate the brand voice report. The data from the strategist was empty."

        # 2. Format the Pydantic object into a human-readable Markdown report
        print("Orchestrator: Formatting report into Markdown...")
        
        markdown_report = f"""
# **Calcularte Brand Voice Report**

## **1. Executive Summary**
{report_data.executive_summary}

---

## **2. Key Content Pillars**
"""
        for pillar in report_data.key_content_pillars:
            markdown_report += f"- **{pillar.get('pillar', 'N/A')}:** {pillar.get('description', 'No description provided.')}\n"

        markdown_report += f"""
---

## **3. Audience Persona: 'The Calculover'**
{report_data.audience_persona_summary}

---

## **4. Tone of Voice Analysis**
{report_data.tone_of_voice_analysis}

---

## **5. Language & Style Details**
{report_data.language_style_details}

---

## **6. Hashtag Strategy Summary**
{report_data.hashtag_strategy_summary}
"""
        print("Orchestrator: Report formatted.")
        return markdown_report.strip()

    def generate_ideas(self, content_pillar: str, num_ideas: int = 3) -> List[PostIdea]:
        """
        Generates new post ideas by coordinating with the CreativeDirectorAgent.
        """
        print(f"Orchestrator: Generating {num_ideas} ideas for content pillar: '{content_pillar}'...")
        brand_context = self._get_brand_context(content_pillar)
        
        # Construct the input for the agent
        user_input = f"""
        Content Pillar: '{content_pillar}'
        Number of Ideas: {num_ideas}

        Brand Context:
        {self._format_context(brand_context)}
        """

        # Run the agent using the Agents SDK Runner
        try:
            result = Runner.run_sync(self.creative_director, user_input)
            ideas = result.final_output
            print("Orchestrator: Ideas generated.")
            return ideas if ideas else []
        except Exception as e:
            print(f"Orchestrator: Error running CreativeDirectorAgent: {e}")
            return []

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Helper to format dictionary context into a string for the prompt."""
        formatted_str = ""
        for key, value in context.items():
            if isinstance(value, list):
                formatted_str += f"- {key.replace('_', ' ').title()}:\n"
                for item in value:
                    formatted_str += f"  - {item}\n"
            else:
                formatted_str += f"- {key.replace('_', ' ').title()}: {value}\n"
        return formatted_str.strip()

    def develop_post(self, idea: PostIdea, num_image_prompts: int = 3) -> Dict[str, Any]:
        """
        Develops a full post (caption + image prompts) based on a selected idea.
        """
        print(f"Orchestrator: Developing post for idea: '{idea.title}'...")
        
        # Step 1: Get brand context relevant to the idea
        brand_context = self._get_brand_context(idea.title + " " + idea.defense_of_idea)

        # Step 2: Generate caption using CopywriterAgent
        print("Orchestrator: Writing caption...")
        copywriter_input = f"""
        Idea Title: "{idea.title}"
        Idea Defense: "{idea.defense_of_idea}"

        Brand Context:
        {self._format_context(brand_context)}
        """
        try:
            result = Runner.run_sync(self.copywriter, copywriter_input)
            caption = result.final_output
            print("Orchestrator: Caption written.")
        except Exception as e:
            print(f"Orchestrator: Error running CopywriterAgent: {e}")
            caption = "Error generating caption."

        # Step 3: Generate image prompts using ArtDirectorAgent
        print("Orchestrator: Generating image prompts...")
        art_director_input = f"""
        Post Concept: "{idea.title}"
        Caption: "{caption}"
        Number of Prompts: {num_image_prompts}

        Brand Context:
        {self._format_context(brand_context)}
        """
        try:
            result = Runner.run_sync(self.art_director, art_director_input)
            image_prompts = result.final_output
            print("Orchestrator: Image prompts generated.")
        except Exception as e:
            print(f"Orchestrator: Error running ArtDirectorAgent: {e}")
            image_prompts = []

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
        
        reviewer_input = f"""
        Original Content to revise:
        ---
        {original_content}
        ---

        User Feedback:
        ---
        {user_feedback}
        ---

        Brand Context:
        ---
        {self._format_context(brand_context)}
        ---

        Please provide the revised content.
        """
        
        try:
            result = Runner.run_sync(self.reviewer, reviewer_input)
            revised_content = result.final_output
            print(f"Orchestrator: {component_type} refined.")
            return revised_content
        except Exception as e:
            print(f"Orchestrator: Error running ReviewerAgent: {e}")
            return "Error refining content."

if __name__ == "__main__":
    # Example usage (for testing purposes)
    orchestrator = OrchestratorAgent()

    # Test 1: Generate Brand Voice Report
    print("\n--- Testing Brand Voice Report Generation ---")
    report = orchestrator.generate_brand_voice_report()
    print("\n--- Brand Voice Report ---")
    print(report)
    print("\n---------------------------------")


    # Test 2: Plan Content
    print("\n--- Testing Content Planning ---")
    plan = orchestrator.plan_content("week")
    if plan and plan.plan:
        print("\n--- Content Plan Received ---")
        for post in plan.plan:
            print(f"- Day/Seq: {post.day_or_sequence}, Pillar: {post.pillar}, Reasoning: {post.reasoning}")
    else:
        print("Could not generate a content plan.")


    # Test 3: Generate Ideas
    print("\n--- Testing Idea Generation ---")
    ideas = orchestrator.generate_ideas("Organização Financeira", num_ideas=1)
    if ideas:
        selected_idea = ideas[0]
        print(f"\nSelected Idea: {selected_idea.title}")
        
        # Test 4: Develop Post
        print("\n--- Testing Post Development ---")
        full_post = orchestrator.develop_post(selected_idea, num_image_prompts=2) # 2 content + 1 CTA
        print("\n--- Full Post Developed ---")
        print(f"Caption:\n{full_post['caption']}")
        print("\nImage Prompts:")
        for i, prompt in enumerate(full_post['image_prompts']):
            print(f"Prompt {i+1}: {prompt}")

        # Test 5: Refine Content (example: refine caption)
        print("\n--- Testing Content Refinement ---")
        original_caption = full_post['caption']
        feedback = "Make the call to action more prominent and add an emoji related to saving money."
        revised_caption = orchestrator.refine_content("caption", original_caption, feedback, full_post)
        print(f"\nRevised Caption:\n{revised_caption}")
    else:
        print("No ideas generated, cannot proceed with full post development.")
