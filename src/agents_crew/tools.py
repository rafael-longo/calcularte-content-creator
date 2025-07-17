from datetime import date
from typing import Optional, List, Any, Dict

from agents import function_tool, RunContextWrapper
from src.agents_crew.brand_strategist import (
    BrandStrategistAgent, 
    BrandVoiceReport, 
    ContentPlan,
    brand_reporter_agent, 
    content_planner_agent
)
from src.agents_crew.creative_director import creative_director_agent
from src.agents_crew.copywriter import copywriter_agent
from src.agents_crew.art_director import art_director_agent
from src.agents_crew.reviewer import reviewer_agent
from src.agents_crew.session_analyst import session_analyst_agent
from src.utils.logging import log

# --- Instantiate Agents/Classes ---
brand_strategist = BrandStrategistAgent()

# --- Define FunctionTools for BrandStrategistAgent ---

@function_tool(name_override="get_context_for_content_plan")
def get_context_for_content_plan(ctx: RunContextWrapper, time_frame: Optional[str] = None, num_posts: Optional[int] = None) -> str:
    """
    Gathers and formats all necessary context for the Content Planner Agent.
    
    Args:
        time_frame: The time frame for the plan (e.g., 'week', 'month').
        num_posts: The specific number of posts to plan for.
    """
    return brand_strategist.get_context_for_content_plan(
        time_frame=time_frame,
        num_posts=num_posts
    )

@function_tool(name_override="get_samples_for_brand_voice_report")
def get_samples_for_brand_voice_report(ctx: RunContextWrapper) -> str:
    """
    Retrieves and formats a string of sample posts for the Brand Reporter Agent.
    """
    return brand_strategist.get_samples_for_brand_voice_report()

@function_tool(name_override="get_specialized_context")
def get_specialized_context(ctx: RunContextWrapper, context_type: str, query: str, num_samples: int = 3) -> List[str]:
    """
    Retrieves highly focused, topic-specific examples (e.g., captions, post ideas) from the brand's memory to provide context for a creative task.
    
    Args:
        context_type: The type of context to fetch (e.g., 'relevant captions').
        query: The specific topic to get context for.
        num_samples: The number of examples to retrieve.
    """
    return brand_strategist.get_specialized_context(context_type, query, num_samples)

@function_tool(name_override="query_brand_voice")
def query_brand_voice(ctx: RunContextWrapper, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Performs a general semantic search on the brand's memory (vector database) to find relevant historical posts based on a query.
    
    Args:
        query_text: The text to search for.
        n_results: The number of results to return.
    """
    return brand_strategist.query_brand_voice(query_text, n_results)

@function_tool(name_override="propose_wildcard_angle")
def propose_wildcard_angle(ctx: RunContextWrapper, pillar: str) -> str:
    """
    Generates an unconventional, surprising, or metaphorical "wildcard" angle for a given content pillar to spark creativity.
    This tool is great for breaking out of creative ruts.
    
    Args:
        pillar: The content pillar to generate a wildcard angle for.
    """
    # The wildcard tool needs the full brand voice report for context.
    # This is a chained operation: get report samples -> generate report -> generate wildcard.
    log.info(f"Wildcard tool invoked for pillar: '{pillar}'. Starting chained operation.")
    
    log.debug("Step 1: Getting samples for brand voice report.")
    report_samples = brand_strategist.get_samples_for_brand_voice_report()
    
    log.debug("Step 2: Generating brand voice report to use as context.")
    # Correctly call the agent using the Runner
    from agents import Runner
    import asyncio
    result = asyncio.run(Runner.run(brand_reporter_agent, report_samples))
    report: BrandVoiceReport = result.final_output
    
    # Convert the Pydantic model to a string for the next step
    report_str = report.model_dump_json(indent=2)

    log.debug("Step 3: Calling propose_wildcard_angle with the generated report.")
    return brand_strategist.propose_wildcard_angle(pillar=pillar, brand_voice_report=report_str)


# --- Define Agent-as-Tool wrappers ---

brand_reporter_tool = brand_reporter_agent.as_tool(
    tool_name="generate_brand_voice_report",
    tool_description="Analyzes a string of sample posts and generates a comprehensive report on the brand's voice, tone, style, and content pillars.",
)

content_planner_tool = content_planner_agent.as_tool(
    tool_name="propose_content_plan",
    tool_description="Generates a strategic content plan based on provided context.",
)

creative_director_tool = creative_director_agent.as_tool(
    tool_name="generate_creative_ideas",
    tool_description="Brainstorms new, on-brand post ideas based on a content pillar and brand context. Use this to generate initial concepts.",
)

copywriter_tool = copywriter_agent.as_tool(
    tool_name="write_post_caption",
    tool_description="Writes a compelling, empathetic, and valuable Instagram caption for a given post idea.",
)

art_director_tool = art_director_agent.as_tool(
    tool_name="create_image_prompts",
    tool_description="Translates a post concept and caption into a series of detailed, effective prompts for an image generation model.",
)

reviewer_tool = reviewer_agent.as_tool(
    tool_name="refine_creative_content",
    tool_description="Performs precise, targeted revisions on existing creative content (like captions or image prompts) based on specific user feedback.",
)

session_analyst_tool = session_analyst_agent.as_tool(
    tool_name="query_session_history",
    tool_description="Analyzes the current conversation transcript to answer a specific query about what has happened previously. Use this to find content to refine or to understand the history of the conversation.",
)


# --- Compile All Tools for Maestro ---

maestro_tools = [
    get_context_for_content_plan,
    get_samples_for_brand_voice_report,
    get_specialized_context,
    query_brand_voice,
    propose_wildcard_angle,
    brand_reporter_tool,
    content_planner_tool,
    creative_director_tool,
    copywriter_tool,
    art_director_tool,
    reviewer_tool,
    session_analyst_tool,
]

log.info(f"Maestro toolset compiled with {len(maestro_tools)} tools.")
