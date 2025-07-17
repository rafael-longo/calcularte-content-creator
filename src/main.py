import typer
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional
from agents.tracing import add_trace_processor
from agents import SQLiteSession, Runner
from scripts.ingest_data import ingest_data
from src.agents_crew.brand_strategist import BrandStrategistAgent
from src.agents_crew.orchestrator import OrchestratorAgent, PostIdea
from src.agents_crew.maestro import maestro_agent
from src.utils.logging import CustomLoguruProcessor, log
from src.utils.token_counter import get_session_token_count
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize custom logging
add_trace_processor(CustomLoguruProcessor())
log.info("Custom logging initialized and trace processor added.")

app = typer.Typer()
report_app = typer.Typer()
session_app = typer.Typer()
app.add_typer(report_app, name="report")
app.add_typer(session_app, name="session")

orchestrator = OrchestratorAgent() # Initialize OrchestratorAgent once

# --- Session Management Constants from .env ---
SESSION_DB_FILE = os.getenv("SESSION_DB_FILE", "sessions.db")
ACTIVE_SESSION_FILE = os.getenv("ACTIVE_SESSION_FILE", ".active_session")
TOKEN_LIMIT = int(os.getenv("TOKEN_LIMIT", 100000))

# --- New Session Management Helper Functions ---

def _get_active_session_id() -> Optional[str]:
    """Reads the active session ID from the state file."""
    if os.path.exists(ACTIVE_SESSION_FILE):
        with open(ACTIVE_SESSION_FILE, "r") as f:
            return f.read().strip()
    return None

def _set_active_session_id(session_id: str):
    """Writes the active session ID to the state file."""
    with open(ACTIVE_SESSION_FILE, "w") as f:
        f.write(session_id)

def _clear_active_session_id():
    """Removes the active session state file."""
    if os.path.exists(ACTIVE_SESSION_FILE):
        os.remove(ACTIVE_SESSION_FILE)

def _handle_token_limit(session: SQLiteSession):
    """Handles the case where the token limit is exceeded."""
    token_count = get_session_token_count(session)
    log.warning(f"Session '{session.session_id}' exceeds token limit of {TOKEN_LIMIT} with {token_count} tokens.")
    typer.secho(f"Warning: Session '{session.session_id}' has a large history ({token_count} tokens).", fg=typer.colors.YELLOW)
    typer.secho("This may lead to high costs and latency.", fg=typer.colors.YELLOW)
    
    action = typer.prompt(
        "Choose an action:\n"
        "1: Proceed with the command\n"
        "2: Clear session data and proceed\n"
        "3: End current session, start a new one, and proceed\n"
        "4: Quit\n"
        "Enter your choice (1-4)"
    )

    if action == '1':
        log.info("User chose to proceed with the large session.")
        return session
    elif action == '2':
        log.info(f"User chose to clear session '{session.session_id}'.")
        session.clear()
        log.success(f"Session '{session.session_id}' cleared.")
        typer.echo(f"Session '{session.session_id}' history has been cleared.")
        return session
    elif action == '3':
        log.info(f"User chose to end session '{session.session_id}' and start a new one.")
        _clear_active_session_id()
        return _get_active_session() # Recursively call to get a new session
    elif action == '4':
        log.info("User chose to quit.")
        raise typer.Exit()
    else:
        log.error("Invalid choice. Aborting.")
        raise typer.Exit(code=1)

def _get_active_session() -> SQLiteSession:
    """
    Gets the active session, creating one if it doesn't exist.
    Also handles token limit checks.
    """
    session_id = _get_active_session_id()
    if not session_id:
        session_id = f"auto_session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        _set_active_session_id(session_id)
        log.warning(f"No active session found. Started new session: '{session_id}'")
        typer.secho(f"Warning: No active session. Started new session: '{session_id}'", fg=typer.colors.YELLOW)
    
    session = SQLiteSession(session_id=session_id, db_path=SESSION_DB_FILE)
    
    token_count = get_session_token_count(session)
    if token_count > TOKEN_LIMIT:
        session = _handle_token_limit(session)
        
    return session

# --- Refactored Session CLI Commands ---

@session_app.command("start")
def session_start(session_id: str = typer.Argument(..., help="The name for the session.")):
    """Starts or switches to a named session."""
    _set_active_session_id(session_id)
    log.success(f"Session '{session_id}' is now active.")
    typer.echo(f"Session '{session_id}' is now active.")

@session_app.command("status")
def session_status():
    """Checks the currently active session."""
    session_id = _get_active_session_id()
    if session_id:
        session = SQLiteSession(session_id=session_id, db_path=SESSION_DB_FILE)
        token_count = get_session_token_count(session)
        log.info(f"Currently active session: '{session_id}' ({token_count} tokens)")
        typer.echo(f"Active Session: '{session_id}'")
        typer.echo(f"Token Count: {token_count}")
        typer.echo(f"Database: {os.path.abspath(SESSION_DB_FILE)}")
    else:
        log.info("No active session.")
        typer.echo("No active session.")

@session_app.command("end")
def session_end():
    """Ends the current session, deactivating it."""
    active_session_id = _get_active_session_id()
    if active_session_id:
        _clear_active_session_id()
        log.success(f"Session '{active_session_id}' has been ended.")
        typer.echo(f"Session '{active_session_id}' has been ended (history is preserved).")
    else:
        log.warning("No active session to end.")
        typer.echo("No active session to end.")

@session_app.command("inspect")
def session_inspect():
    """Inspects the content of the active session."""
    session_id = _get_active_session_id()
    if not session_id:
        log.warning("No active session to inspect.")
        typer.echo("No active session to inspect.")
        return

    log.info(f"Inspecting session: '{session_id}'")
    typer.echo(f"--- Inspecting Session: {session_id} ---")
    
    try:
        session = SQLiteSession(session_id=session_id, db_path=SESSION_DB_FILE)
        import asyncio
        items = asyncio.run(session.get_items())
        
        if not items:
            typer.echo("Session is empty.")
            return
            
        # Pretty-print the JSON content
        typer.echo(json.dumps(items, indent=2))

    except Exception as e:
        log.error(f"Failed to inspect session '{session_id}': {e}")
        typer.echo(f"Error: Failed to inspect session '{session_id}'.")


@session_app.command("clear")
def session_clear():
    """Permanently clears all history for the currently active session."""
    session_id = _get_active_session_id()
    if not session_id:
        log.warning("No active session to clear.")
        typer.echo("No active session to clear.")
        return

    if typer.confirm(f"Are you sure you want to permanently delete all history for session '{session_id}'?"):
        try:
            session_to_clear = SQLiteSession(session_id=session_id, db_path=SESSION_DB_FILE)
            session_to_clear.clear()
            log.success(f"History for session '{session_id}' has been cleared.")
            typer.echo(f"History for session '{session_id}' has been cleared.")
        except Exception as e:
            log.error(f"Failed to clear session '{session_id}': {e}")
            typer.echo(f"Error: Failed to clear session '{session_id}'.")

def check_openai_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        log.error("OPENAI_API_KEY environment variable not set.")
        typer.echo("Error: OPENAI_API_KEY environment variable not set.")
        typer.echo("Please set it in your .env file or as an environment variable.")
        raise typer.Exit(code=1)

@app.command()
def ingest(
    sample: bool = typer.Option(
        True,
        "--sample/--full",
        help="Use the sample dataset (dataset_sample.jsonl) or the full dataset (dataset_instagram_calcularte_profile.jsonl).",
    )
):
    """
    Ingests data into the ChromaDB vector database.
    """
    check_openai_api_key()
    
    if sample:
        file_path = "dataset_sample.jsonl"
    else:
        file_path = "dataset_instagram_calcularte_profile.jsonl"
    
    ingest_data(file_path)
    log.success("Data ingestion process finished.")
    typer.echo("Data ingestion process finished.")

@app.command("ask-strategist")
def ask_strategist_command(
    query: str = typer.Argument(..., help="The query text for the Brand Strategist Agent.")
):
    """
    Queries the Brand Strategist Agent for relevant brand voice content.
    """
    check_openai_api_key()

    strategist = BrandStrategistAgent()
    if strategist.collection:
        log.info(f"Querying Brand Strategist with: '{query}'")
        typer.echo(f"Querying Brand Strategist with: '{query}'")
        results = strategist.query_brand_voice(query)
        if isinstance(results, str): # Handle error message from agent
            log.error(f"Error from BrandStrategistAgent: {results}")
            typer.echo(results)
        elif results:
            typer.echo("\n--- Relevant Brand Content ---")
            for item in results:
                typer.echo(f"Caption: {item['caption']}")
                typer.echo(f"Hashtags: {item['metadata'].get('hashtags', 'N/A')}")
                typer.echo(f"Likes: {item['metadata'].get('likesCount', 'N/A')}, Comments: {item['metadata'].get('commentsCount', 'N/A')}")
                typer.echo(f"URL: {item['metadata'].get('url', 'N/A')}")
                typer.echo("---")
        else:
            log.info("No relevant content found for query.")
            typer.echo("No relevant content found.")
    else:
        log.warning("Brand Strategist Agent not ready. User advised to run 'ingest' command.")
        typer.echo("Brand Strategist Agent not ready. Please run 'ingest' command first.")

@app.command("plan-content")
def plan_content_command(
    time_frame: str = typer.Argument(..., help="The time frame for the content plan (e.g., 'week', 'month').")
):
    """
    Generates a strategic content plan using the Orchestrator Agent.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")

    log.info(f"Generating content plan for the next '{time_frame}'...")
    typer.echo(f"Generating content plan for the next '{time_frame}'...")
    plan = orchestrator.plan_content(time_frame, session=session)
    
    if plan and plan.plan:
        log.success(f"Successfully generated content plan with {len(plan.plan)} posts.")
        typer.echo("\n--- Strategic Content Plan ---")
        for post in plan.plan:
            typer.echo(f"Day/Sequence: {post.day_or_sequence}")
            typer.echo(f"  Pillar: {post.pillar}")
            typer.echo(f"  Reasoning: {post.reasoning}")
            typer.echo("---")
    else:
        log.error("Failed to generate content plan.")
        typer.echo("Failed to generate content plan.")

def validate_plan_params(for_time: str, num: int):
    if for_time and num:
        raise typer.BadParameter("Only one of --for or --num can be used at a time.")
    if not for_time and not num:
        raise typer.BadParameter("One of --for or --num must be provided.")

@app.command("plan")
def plan_command(
    for_time: Optional[str] = typer.Option(None, "--for", help="The time frame to plan for (e.g., 'week', 'month')."),
    num: Optional[int] = typer.Option(None, "--num", "-n", help="The number of ideas to plan.")
):
    """
    Plans content ideas based on a strategic plan.
    """
    validate_plan_params(for_time, num)
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")
    
    if for_time:
        log.info(f"Planning content ideas for the next '{for_time}'...")
        typer.echo(f"Planning content ideas for the next '{for_time}'...")
        ideas = orchestrator.plan_content_ideas(time_frame=for_time, session=session)
    else:
        log.info(f"Planning {num} content ideas...")
        typer.echo(f"Planning {num} content ideas...")
        ideas = orchestrator.plan_content_ideas(num_ideas=num, session=session)

    if ideas:
        log.success(f"Successfully planned {len(ideas)} ideas.")
        typer.echo("\n--- Planned Ideas ---")
        for i, idea in enumerate(ideas):
            typer.echo(f"Idea {i+1}:")
            typer.echo(f"  Title: {idea.title}")
            typer.echo(f"  Content Pillar: {idea.content_pillar}")
            typer.echo(f"  Defense: {idea.defense_of_idea}")
            typer.echo(f"  Expected Results: {idea.expected_results}")
            typer.echo("---")
    else:
        log.warning("No ideas were planned.")
        typer.echo("No ideas were planned.")

@app.command("plan-and-develop")
def plan_and_develop_command(
    for_time: Optional[str] = typer.Option(None, "--for", help="The time frame to plan and develop for (e.g., 'week', 'month')."),
    num: Optional[int] = typer.Option(None, "--num", "-n", help="The number of posts to plan and develop.")
):
    """
    Autonomously plans and develops a full content calendar.
    """
    validate_plan_params(for_time, num)
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")

    if for_time:
        log.info(f"Starting autonomous plan-and-develop for time frame: '{for_time}'...")
        typer.echo(f"Autonomously planning and developing content for the next '{for_time}'...")
        developed_posts = orchestrator.plan_and_develop_content(time_frame=for_time, session=session)
    else:
        log.info(f"Starting autonomous plan-and-develop for {num} posts...")
        typer.echo(f"Autonomously planning and developing {num} posts...")
        developed_posts = orchestrator.plan_and_develop_content(num_ideas=num, session=session)

    if developed_posts:
        log.success(f"Successfully developed {len(developed_posts)} posts.")
        typer.echo("\n--- Autonomously Developed Content Calendar ---")
        for i, post in enumerate(developed_posts):
            typer.echo(f"--- Post {i+1}: {post['idea'].title} ---")
            typer.echo(f"\n**Caption:**\n{post['caption']}")
            typer.echo("\n**Image Prompts:**")
            for j, prompt in enumerate(post['image_prompts']):
                typer.echo(f"  - Prompt {j+1}: {prompt}")
            typer.echo("\n" + "="*40 + "\n")
    else:
        log.error("No content was developed.")
        typer.echo("No content was developed.")

@report_app.command("brand-voice")
def report_brand_voice_command():
    """
    Generates a comprehensive, human-readable report on the brand's voice.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")

    log.info("Generating brand voice report...")
    typer.echo("Generating brand voice report...")
    report = orchestrator.generate_brand_voice_report(session=session)
    
    if report and "Could not generate" not in report:
        log.success("Successfully generated brand voice report.")
        typer.echo("\n--- Brand Voice Report ---")
        typer.echo(report)
        typer.echo("--------------------------")
    else:
        log.error("Failed to generate brand voice report.")
        typer.echo("Failed to generate brand voice report.")

@app.command("generate-ideas")
def generate_ideas_command(
    pillar: str = typer.Argument(..., help="The content pillar for which to generate ideas."),
    num_ideas: int = typer.Option(3, "--num", "-n", help="Number of ideas to generate.")
):
    """
    Generates new post ideas using the Orchestrator Agent.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")

    log.info(f"Generating {num_ideas} ideas for pillar: '{pillar}'...")
    typer.echo(f"Generating {num_ideas} ideas for pillar: '{pillar}'...")
    ideas = orchestrator.generate_ideas(pillar, num_ideas, session=session)
    if ideas:
        log.success(f"Successfully generated {len(ideas)} ideas.")
        typer.echo("\n--- Generated Ideas ---")
        for i, idea in enumerate(ideas):
            typer.echo(f"Idea {i+1}:")
            typer.echo(f"  Title: {idea.title}")
            typer.echo(f"  Content Pillar: {idea.content_pillar}")
            typer.echo(f"  Defense: {idea.defense_of_idea}")
            typer.echo(f"  Expected Results: {idea.expected_results}")
            typer.echo("---")
    else:
        log.error("No ideas generated.")
        typer.echo("No ideas generated.")

@app.command("develop-post")
def develop_post_command(
    idea_title: str = typer.Argument(..., help="The title of the idea to develop."),
    idea_pillar: str = typer.Argument(..., help="The content pillar of the idea."),
    idea_defense: str = typer.Argument(..., help="The defense/justification of the idea."),
    idea_results: str = typer.Argument(..., help="The expected results of the idea."),
    num_image_prompts: int = typer.Option(3, "--num-images", "-n", help="Number of image prompts to generate (excluding CTA).")
):
    """
    Develops a full post (caption + image prompts) based on a selected idea.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")
    
    idea = PostIdea(
        title=idea_title,
        content_pillar=idea_pillar,
        defense_of_idea=idea_defense,
        expected_results=idea_results
    )
    
    log.info(f"Developing full post for idea: '{idea.title}'...")
    typer.echo(f"Developing full post for idea: '{idea.title}'...")
    full_post = orchestrator.develop_post(idea, num_image_prompts, session=session)
    
    if full_post and full_post.get('caption') and "Error" not in full_post['caption']:
        log.success("Successfully developed post.")
        typer.echo("\n--- Developed Post ---")
        typer.echo(f"Caption:\n{full_post['caption']}")
        typer.echo("\nImage Prompts:")
        for i, prompt in enumerate(full_post['image_prompts']):
            typer.echo(f"Prompt {i+1}: {prompt}")
        typer.echo("---")
    else:
        log.error("Failed to develop post.")
        typer.echo("Failed to develop post.")

@app.command("refine-content")
def refine_content_command(
    component_type: str = typer.Argument(..., help="Type of component to refine (e.g., 'caption', 'prompt')."),
    original_content: str = typer.Argument(..., help="The original content to be refined."),
    user_feedback: str = typer.Argument(..., help="The user feedback for refinement."),
    post_context_query: Optional[str] = typer.Option(None, "--context-query", "-c", help="A query to fetch relevant post context for refinement.")
):
    """
    Refines a specific content component (caption or image prompt) using the Reviewer Agent.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}'")

    # For simplicity, we'll pass a dummy post_context for now.
    # In a real app, this would be a more structured object.
    post_context = {"query_for_context": post_context_query if post_context_query else original_content}

    log.info(f"Refining {component_type}...")
    typer.echo(f"Refining {component_type}...")
    revised_content = orchestrator.refine_content(component_type, original_content, user_feedback, post_context, session=session)
    
    if revised_content and "Error" not in revised_content:
        log.success(f"Successfully refined {component_type}.")
        typer.echo(f"\n--- Revised {component_type.capitalize()} ---")
        typer.echo(revised_content)
        typer.echo("---")
    else:
        log.error(f"Failed to refine {component_type}.")
        typer.echo(f"Failed to refine {component_type}.")

@app.command("maestro")
def maestro_command(
    prompt: str = typer.Argument(..., help="The high-level prompt for the Maestro Agent.")
):
    """
    Interacts with the Maestro Agent for autonomous, conversational content creation.
    """
    check_openai_api_key()
    session = _get_active_session()
    log.info(f"Using active session: '{session.session_id}' for Maestro command.")
    typer.echo(f"Maestro is thinking... (using session: {session.session_id})")

    # The runner is async, so we use asyncio.run
    result = asyncio.run(Runner.run(maestro_agent, prompt, session=session, max_turns=5))
    
    final_output = result.final_output
    
    if final_output:
        log.success("Maestro command finished successfully.")
        # TODO: We could add more structured output parsing here later
        typer.echo("\n--- Maestro's Response ---")
        typer.echo(final_output)
        typer.echo("--------------------------")
    else:
        log.error("Maestro command finished with no output.")
        typer.echo("Maestro command finished with no output.")


if __name__ == "__main__":
    app()
