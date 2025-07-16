from typing import List, Dict, Any, Type
from datetime import date
from agents import Runner, Agent
from pydantic import TypeAdapter, BaseModel
from src.agents_crew.brand_strategist import BrandStrategistAgent, ContentPlan, BrandVoiceReport, PlannedPost
from src.agents_crew.creative_director import creative_director_agent, PostIdea, GeneratedIdeas
from src.agents_crew.copywriter import copywriter_agent
from src.agents_crew.art_director import art_director_agent, ImagePrompt, GeneratedImagePrompts
from src.agents_crew.reviewer import reviewer_agent
from src.agents_crew.evaluator import evaluator_agent, EvaluationResult
from src.utils.logging import log

class OrchestratorAgent:
    def __init__(self):
        self.brand_strategist = BrandStrategistAgent()
        self.creative_director = creative_director_agent
        self.copywriter = copywriter_agent
        self.art_director = art_director_agent
        self.reviewer = reviewer_agent
        self.evaluator = evaluator_agent

    def _get_brand_context(self, query: str) -> Dict[str, Any]:
        """Fetches relevant brand context using the BrandStrategistAgent."""
        log.info(f"Fetching brand context for query: '{query}'...")
        context_results = self.brand_strategist.query_brand_voice(query, n_results=5)
        
        # Process context_results into a more usable dictionary format for other agents
        brand_context = {
            "relevant_posts": [],
            "tone_examples": [],
            "hashtag_examples": [],
            "general_brand_info": "Calcularte helps artisans and confectioners manage finances, pricing, and business organization."
        }

        if isinstance(context_results, str): # Error from BrandStrategistAgent
            log.error(f"Error fetching brand context: {context_results}")
            return brand_context # Return empty context

        for item in context_results:
            brand_context["relevant_posts"].append(item['caption'])
            brand_context["tone_examples"].append(item['caption']) # Use captions as tone examples
            if item['metadata'].get('hashtags'):
                brand_context["hashtag_examples"].extend(item['metadata']['hashtags'].split(', ')) # Split string back to list

        # Deduplicate hashtags
        brand_context["hashtag_examples"] = list(set(brand_context["hashtag_examples"]))
        
        log.info("Brand context fetched.")
        return brand_context

    def plan_content(self, time_frame: str = None, num_posts: int = None) -> ContentPlan:
        """
        Generates a strategic content plan by coordinating with the BrandStrategistAgent.
        """
        if num_posts:
            log.info(f"Generating content plan for {num_posts} posts...")
        else:
            log.info(f"Generating content plan for '{time_frame}'...")
        
        current_date = date.today()
        content_plan = self.brand_strategist.propose_content_plan(
            time_frame=time_frame,
            current_date=current_date,
            recent_post_themes=None,
            num_posts=num_posts
        )
        log.info("Content plan generated.")
        return content_plan

    def generate_brand_voice_report(self) -> str:
        """
        Generates and formats a comprehensive brand voice report.
        """
        log.info("Generating brand voice report...")
        
        # 1. Trigger the report generation from the BrandStrategistAgent
        report_data = self.brand_strategist.generate_brand_voice_report()
        
        if not report_data or not report_data.executive_summary:
            log.error("Could not generate the brand voice report. The data from the strategist was empty.")
            return "Could not generate the brand voice report. The data from the strategist was empty."

        # 2. Format the Pydantic object into a human-readable Markdown report
        log.info("Formatting report into Markdown...")
        
        markdown_report = f"""
# **Calcularte Brand Voice Report**

## **1. Executive Summary**
{report_data.executive_summary}

---

## **2. Key Content Pillars**
"""
        for pillar in report_data.key_content_pillars:
            markdown_report += f"- **{pillar.pillar}:** {pillar.description}\n"

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

## **6. Country & Culture Details**
{report_data.country_culture_details}

---

## **7. Hashtag Strategy Summary**
{report_data.hashtag_strategy_summary}
"""
        log.success("Report formatted successfully.")
        return markdown_report.strip()

    def plan_content_ideas(self, time_frame: str = None, num_ideas: int = None) -> List[PostIdea]:
        """
        Generates a list of post ideas based on a strategic content plan.
        """
        log.info("Planning content ideas...")
        
        # 1. Get the strategic plan from the BrandStrategist
        plan = self.plan_content(time_frame=time_frame, num_posts=num_ideas)
        if not plan or not plan.plan:
            log.error("Could not generate a content plan. Aborting idea generation.")
            return []

        # If num_ideas is specified, truncate the plan, otherwise use the full plan
        planned_posts = plan.plan
        if num_ideas is not None and num_ideas > 0:
            planned_posts = planned_posts[:num_ideas]
            log.info(f"Limiting idea generation to {num_ideas} planned posts.")

        # 2. Iterate through the plan and generate one idea for each point
        all_ideas = []
        for planned_post in planned_posts:
            log.info(f"Generating idea for pillar: '{planned_post.pillar}'...")
            # The generate_ideas method already handles getting brand context.
            # We pass the planned_post object to be used as additional context.
            ideas = self.generate_ideas(
                content_pillar=planned_post.pillar, 
                num_ideas=1,
                planned_post=planned_post # Pass the context here
            )
            if ideas:
                all_ideas.extend(ideas)
        
        log.success(f"Total of {len(all_ideas)} ideas planned.")
        return all_ideas

    def plan_and_develop_content(self, time_frame: str = None, num_ideas: int = None) -> List[Dict[str, Any]]:
        """
        Autonomously plans and develops a full content calendar.
        """
        log.info("Starting autonomous plan-and-develop workflow...")
        
        # 1. Plan all the content ideas first
        ideas_to_develop = self.plan_content_ideas(time_frame=time_frame, num_ideas=num_ideas)
        if not ideas_to_develop:
            log.error("No ideas were generated, cannot develop content.")
            return []

        # 2. Develop each idea into a full post
        developed_posts = []
        for idea in ideas_to_develop:
            full_post = self.develop_post(idea)
            developed_posts.append(full_post)
            
        log.success("Autonomous plan-and-develop workflow complete.")
        return developed_posts

    def generate_ideas(self, content_pillar: str, num_ideas: int = 3, planned_post: PlannedPost = None) -> List[PostIdea]:
        """
        Generates new post ideas by coordinating with the CreativeDirectorAgent.
        Can optionally take a `planned_post` object for more specific context.
        """
        log.info(f"Generating {num_ideas} ideas for content pillar: '{content_pillar}'...")
        brand_context = self._get_brand_context(content_pillar)
        
        # Add planned_post context if available
        if planned_post:
            brand_context['strategic_context'] = planned_post.model_dump()
            log.debug(f"Added strategic context from planned post: {planned_post.pillar}")

        # Construct the input for the agent
        user_input = f"""
        Pydantic Schema for the output:
        ```json
        {GeneratedIdeas.model_json_schema()}
        ```

        Content Pillar: '{content_pillar}'
        Number of Ideas: {num_ideas}

        Brand Context:
        {self._format_context(brand_context)}
        """
        log.debug(f"Passing the following context to CreativeDirectorAgent:\n{user_input}")

        # Run the agent using the Agents SDK Runner
        try:
            result = Runner.run_sync(self.creative_director, user_input)
            ideas_obj = result.final_output
            if ideas_obj and isinstance(ideas_obj, GeneratedIdeas):
                log.success(f"Received {len(ideas_obj.ideas)} ideas from CreativeDirectorAgent.")
                return ideas_obj.ideas
            else:
                log.error("No ideas generated or incorrect format received from CreativeDirectorAgent.")
                return []
        except Exception as e:
            log.error(f"Error running CreativeDirectorAgent: {e}")
            return []

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Helper to format dictionary context into a string for the prompt."""
        formatted_str = ""
        for key, value in context.items():
            if isinstance(value, dict):
                formatted_str += f"- {key.replace('_', ' ').title()}:\n"
                for sub_key, sub_value in value.items():
                    formatted_str += f"  - {sub_key.title()}: {sub_value}\n"
            elif isinstance(value, list):
                formatted_str += f"- {key.replace('_', ' ').title()}:\n"
                for item in value:
                    formatted_str += f"  - {item}\n"
            else:
                formatted_str += f"- {key.replace('_', ' ').title()}: {value}\n"
        return formatted_str.strip()

    def _evaluate_and_refine_content(self, creator_agent: Agent, initial_input: str, content_type: str, max_retries: int = 2) -> Any:
        """
        A generic quality control loop that uses an EvaluatorAgent to refine content.
        It can handle both string and Pydantic model outputs.
        """
        log.info(f"Starting evaluation and refinement loop for {content_type}...")
        current_content = None
        feedback = ""

        for i in range(max_retries):
            log.info(f"Attempt {i+1}/{max_retries} to generate and evaluate {content_type}.")

            revised_input = f"{initial_input}\n\nFeedback for revision: {feedback}" if feedback else initial_input

            try:
                result = Runner.run_sync(creator_agent, revised_input)
                current_content = result.final_output
                if not current_content:
                    raise ValueError("Creator agent returned empty content.")
                log.success(f"{content_type.capitalize()} generated.")
            except Exception as e:
                log.error(f"Error running {creator_agent.name}: {e}")
                return None

            content_to_evaluate_str = ""
            if isinstance(current_content, str):
                content_to_evaluate_str = current_content
            elif isinstance(current_content, BaseModel):
                # Convert Pydantic model to a descriptive string for evaluation
                if hasattr(current_content, 'prompts'): # Specific to GeneratedImagePrompts
                    content_to_evaluate_str = "\n".join([p.prompt for p in current_content.prompts])
                else:
                    content_to_evaluate_str = current_content.model_dump_json(indent=2)
            
            brand_principles = self.generate_brand_voice_report()
            evaluator_input = f"""
            Content to evaluate:
            ---
            {content_to_evaluate_str}
            ---
            Content Type: {content_type}
            Brand Principles:
            ---
            {brand_principles}
            ---
            """
            log.info(f"Evaluating {content_type}...")
            try:
                eval_result = Runner.run_sync(self.evaluator, evaluator_input)
                evaluation: EvaluationResult = eval_result.final_output
                log.info(f"Evaluation result: {evaluation.score}")

                if evaluation.score == "approved":
                    log.success(f"{content_type.capitalize()} approved after {i+1} attempts.")
                    return current_content
                else:
                    feedback = evaluation.feedback
                    log.warning(f"Content needs improvement. Feedback: {feedback}")

            except Exception as e:
                log.error(f"Error running EvaluatorAgent: {e}")
                return current_content

        log.warning(f"Max retries reached for {content_type}. Returning last generated content.")
        return current_content

    def develop_post(self, idea: PostIdea, num_image_prompts: int = 3) -> Dict[str, Any]:
        """
        Develops a full post (caption + image prompts) based on a selected idea,
        including a quality control loop.
        """
        log.info(f"Developing post for idea: '{idea.title}'...")

        # Step 1: Generate and refine caption
        copywriting_context = self.brand_strategist.get_specialized_context(
            context_type="relevant captions for a post",
            query=f"{idea.title} - {idea.defense_of_idea}"
        )
        contextual_examples_str = "\n- ".join(copywriting_context)
        copywriter_initial_input = f"""
        Idea Title: "{idea.title}"
        Idea Defense: "{idea.defense_of_idea}"

        Contextual Examples of Relevant Captions:
        - {contextual_examples_str}
        """
        caption = self._evaluate_and_refine_content(
            creator_agent=self.copywriter,
            initial_input=copywriter_initial_input,
            content_type="caption"
        ) or "Error generating caption."

        # Step 2: Generate and refine image prompts
        brand_context = self._get_brand_context(idea.title + " " + idea.defense_of_idea)
        art_director_initial_input = f"""
        Pydantic Schema for the output:
        ```json
        {GeneratedImagePrompts.model_json_schema()}
        ```

        Post Concept: "{idea.title}"
        Caption: "{caption}"
        Number of Prompts: {num_image_prompts}

        Brand Context:
        {self._format_context(brand_context)}
        """
        image_prompts_obj = self._evaluate_and_refine_content(
            creator_agent=self.art_director,
            initial_input=art_director_initial_input,
            content_type="image_prompts"
        )
        
        image_prompts = image_prompts_obj.prompts if image_prompts_obj else []

        return {
            "idea": idea,
            "caption": caption,
            "image_prompts": [p.prompt for p in image_prompts] if image_prompts else []
        }

    def refine_content(self, component_type: str, original_content: str, user_feedback: str, post_context: Dict[str, Any]) -> str:
        """
        Refines a specific content component using the ReviewerAgent.
        """
        log.info(f"Refining {component_type} with user feedback: '{user_feedback}'...")
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
        log.debug(f"Passing the following context to ReviewerAgent:\n{reviewer_input}")
        
        try:
            result = Runner.run_sync(self.reviewer, reviewer_input)
            revised_content = result.final_output
            log.success(f"{component_type.capitalize()} refined successfully.")
            return revised_content
        except Exception as e:
            log.error(f"Error running ReviewerAgent: {e}")
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
