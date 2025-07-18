import asyncio
import typer
from datetime import date
from typing import Optional, List, Any, Dict

from agents import function_tool, RunContextWrapper, Runner
from src.agents_crew.brand_strategist import (
    BrandStrategistAgent,
    BrandVoiceReport,
    ContentPlan,
    PostSample,
    BrandContext,
    brand_reporter_agent,
    content_planner_agent
)
from src.agents_crew.creative_director import creative_director_agent, GeneratedIdeas
from src.agents_crew.copywriter import copywriter_agent
from src.agents_crew.art_director import art_director_agent, GeneratedImagePrompts
from src.agents_crew.reviewer import reviewer_agent
from src.agents_crew.session_analyst import session_analyst_agent
from src.utils.logging import log

# --- Instantiate Agents/Classes ---
brand_strategist = BrandStrategistAgent()

# --- Helper function for streaming sub-agents ---
async def _run_agent_as_streaming_tool(agent, prompt, ctx):
    """Helper to run an agent and stream its thoughts to the log."""
    log.info(f"Maestro is calling a sub-agent: {agent.name}")
    typer.echo(f"\n\n--- Calling {agent.name}... ---")
    
    # The session is implicitly managed by the Runner when a tool is called.
    # We don't need to (and cannot) pass it explicitly here.
    result = Runner.run_streamed(agent, prompt)
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta') and event.data.delta:
            # Use typer.secho for direct, unformatted console output
            typer.secho(event.data.delta, nl=False, fg="cyan")
            # Log the same data to the file, escaping braces for safety
            log.log("THOUGHT", event.data.delta.replace("{", "{{").replace("}", "}}"))

    typer.echo(f"\n--- {agent.name} finished. ---")
    return result.final_output

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
def query_brand_voice(ctx: RunContextWrapper, query_text: str, n_results: int = 3) -> List[PostSample]:
    """
    Performs a general semantic search on the brand's memory (vector database) to find relevant historical posts based on a query.
    
    Args:
        query_text: The text to search for.
        n_results: The number of results to return.
    """
    return brand_strategist.query_brand_voice(query_text, n_results)

@function_tool(name_override="propose_wildcard_angle")
async def propose_wildcard_angle(ctx: RunContextWrapper, pillar: str) -> str:
    """
    Generates an unconventional, surprising, or metaphorical "wildcard" angle for a given content pillar to spark creativity.
    This tool is great for breaking out of creative ruts.
    
    Args:
        pillar: The content pillar to generate a wildcard angle for.
    """
    log.info(f"Wildcard tool invoked for pillar: '{pillar}'. Starting chained operation.")
    
    log.debug("Step 1: Getting samples for brand voice report.")
    report_samples = brand_strategist.get_samples_for_brand_voice_report(post_samples=None)
    
    log.debug("Step 2: Generating brand voice report to use as context.")
    report: BrandVoiceReport = await _run_agent_as_streaming_tool(brand_reporter_agent, report_samples, ctx)
    
    report_str = report.model_dump_json(indent=2)

    log.debug("Step 3: Calling propose_wildcard_angle with the generated report.")
    return brand_strategist.propose_wildcard_angle(pillar=pillar, brand_voice_report=report_str)


# --- New Agent-as-Tool Implementations ---

@function_tool(name_override="generate_brand_voice_report")
async def generate_brand_voice_report(ctx: RunContextWrapper, post_samples: List[PostSample]) -> BrandVoiceReport:
    """
    Analyzes a list of sample posts and generates a comprehensive report on the brand's voice, tone, style, and content pillars.
    """
    # The agent expects a string, so we serialize the list of Pydantic models into a JSON string.
    analysis_input = f"Here are the post samples to analyze:\n{ [sample.model_dump_json() for sample in post_samples] }"
    return await _run_agent_as_streaming_tool(brand_reporter_agent, analysis_input, ctx)

@function_tool(name_override="propose_content_plan")
async def propose_content_plan(ctx: RunContextWrapper, plan_input: str) -> ContentPlan:
    """
    Generates a strategic content plan based on provided context.
    """
    return await _run_agent_as_streaming_tool(content_planner_agent, plan_input, ctx)

@function_tool(name_override="generate_creative_ideas")
async def generate_creative_ideas(ctx: RunContextWrapper, ideas_input: str, brand_context: Optional[BrandContext] = None) -> GeneratedIdeas:
    """
    Brainstorms new, on-brand post ideas based on a content pillar and brand context. Use this to generate initial concepts.
    """
    context_str = ""
    if brand_context:
        context_str = f"\n\n--- Brand Context ---\n{brand_context.model_dump_json(indent=2)}\n--- End Context ---"
    prompt = f"{ideas_input}{context_str}"
    return await _run_agent_as_streaming_tool(creative_director_agent, prompt, ctx)

@function_tool(name_override="write_post_caption")
async def write_post_caption(ctx: RunContextWrapper, caption_input: str, brand_context: Optional[BrandContext] = None) -> str:
    """
    Writes a compelling, empathetic, and valuable Instagram caption for a given post idea.
    """
    context_str = ""
    if brand_context:
        context_str = f"\n\n--- Brand Context ---\n{brand_context.model_dump_json(indent=2)}\n--- End Context ---"
    prompt = f"{caption_input}{context_str}"
    return await _run_agent_as_streaming_tool(copywriter_agent, prompt, ctx)

@function_tool(name_override="create_image_prompts")
async def create_image_prompts(ctx: RunContextWrapper, prompts_input: str, brand_context: Optional[BrandContext] = None) -> GeneratedImagePrompts:
    """
    Translates a post concept and caption into a series of detailed, effective prompts for an image generation model.
    """
    context_str = ""
    if brand_context:
        context_str = f"\n\n--- Brand Context ---\n{brand_context.model_dump_json(indent=2)}\n--- End Context ---"
    prompt = f"{prompts_input}{context_str}"
    return await _run_agent_as_streaming_tool(art_director_agent, prompt, ctx)

@function_tool(name_override="refine_creative_content")
async def refine_creative_content(ctx: RunContextWrapper, revision_input: str) -> str:
    """
    Performs precise, targeted revisions on existing creative content (like captions or image prompts) based on specific user feedback.
    """
    return await _run_agent_as_streaming_tool(reviewer_agent, revision_input, ctx)

@function_tool(name_override="query_session_history")
async def query_session_history(ctx: RunContextWrapper, query_input: str) -> str:
    """

    Analyzes the current conversation transcript to answer a specific query about what has happened previously. Use this to find content to refine or to understand the history of the conversation.
    """
    return await _run_agent_as_streaming_tool(session_analyst_agent, query_input, ctx)


# --- Compile All Tools for Maestro ---

maestro_tools = [
    get_context_for_content_plan,
    get_specialized_context,
    query_brand_voice,
    propose_wildcard_angle,
    generate_brand_voice_report,
    propose_content_plan,
    generate_creative_ideas,
    write_post_caption,
    create_image_prompts,
    refine_creative_content,
    query_session_history,
]

log.info(f"Maestro toolset compiled with {len(maestro_tools)} tools.")
