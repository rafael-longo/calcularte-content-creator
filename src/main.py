import typer
import os
from dotenv import load_dotenv
from typing import Optional
from agents.tracing import add_trace_processor
from scripts.ingest_data import ingest_data
from src.agents_crew.brand_strategist import BrandStrategistAgent
from src.agents_crew.orchestrator import OrchestratorAgent, PostIdea
from src.utils.logging import CustomLoguruProcessor, log

# Load environment variables from .env file
load_dotenv()

# Initialize custom logging
add_trace_processor(CustomLoguruProcessor())
log.info("Custom logging initialized and trace processor added.")

app = typer.Typer()
report_app = typer.Typer()
app.add_typer(report_app, name="report")

orchestrator = OrchestratorAgent() # Initialize OrchestratorAgent once

def check_openai_api_key():
    if not os.getenv("OPENAI_API_KEY"):
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
        typer.echo(f"Querying Brand Strategist with: '{query}'")
        results = strategist.query_brand_voice(query)
        if isinstance(results, str): # Handle error message from agent
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
            typer.echo("No relevant content found.")
    else:
        typer.echo("Brand Strategist Agent not ready. Please run 'ingest' command first.")

@app.command("plan-content")
def plan_content_command(
    time_frame: str = typer.Argument(..., help="The time frame for the content plan (e.g., 'week', 'month').")
):
    """
    Generates a strategic content plan using the Orchestrator Agent.
    """
    check_openai_api_key()
    typer.echo(f"Generating content plan for the next '{time_frame}'...")
    plan = orchestrator.plan_content(time_frame)
    
    if plan and plan.plan:
        typer.echo("\n--- Strategic Content Plan ---")
        for post in plan.plan:
            typer.echo(f"Day/Sequence: {post.day_or_sequence}")
            typer.echo(f"  Pillar: {post.pillar}")
            typer.echo(f"  Reasoning: {post.reasoning}")
            typer.echo("---")
    else:
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
    
    if for_time:
        typer.echo(f"Planning content ideas for the next '{for_time}'...")
        ideas = orchestrator.plan_content_ideas(time_frame=for_time)
    else:
        typer.echo(f"Planning {num} content ideas...")
        ideas = orchestrator.plan_content_ideas(num_ideas=num)

    if ideas:
        typer.echo("\n--- Planned Ideas ---")
        for i, idea in enumerate(ideas):
            typer.echo(f"Idea {i+1}:")
            typer.echo(f"  Title: {idea.title}")
            typer.echo(f"  Content Pillar: {idea.content_pillar}")
            typer.echo(f"  Defense: {idea.defense_of_idea}")
            typer.echo(f"  Expected Results: {idea.expected_results}")
            typer.echo("---")
    else:
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

    if for_time:
        typer.echo(f"Autonomously planning and developing content for the next '{for_time}'...")
        developed_posts = orchestrator.plan_and_develop_content(time_frame=for_time)
    else:
        typer.echo(f"Autonomously planning and developing {num} posts...")
        developed_posts = orchestrator.plan_and_develop_content(num_ideas=num)

    if developed_posts:
        typer.echo("\n--- Autonomously Developed Content Calendar ---")
        for i, post in enumerate(developed_posts):
            typer.echo(f"--- Post {i+1}: {post['idea'].title} ---")
            typer.echo(f"\n**Caption:**\n{post['caption']}")
            typer.echo("\n**Image Prompts:**")
            for j, prompt in enumerate(post['image_prompts']):
                typer.echo(f"  - Prompt {j+1}: {prompt}")
            typer.echo("\n" + "="*40 + "\n")
    else:
        typer.echo("No content was developed.")

@report_app.command("brand-voice")
def report_brand_voice_command():
    """
    Generates a comprehensive, human-readable report on the brand's voice.
    """
    check_openai_api_key()
    typer.echo("Generating brand voice report...")
    report = orchestrator.generate_brand_voice_report()
    
    if report:
        typer.echo("\n--- Brand Voice Report ---")
        typer.echo(report)
        typer.echo("--------------------------")
    else:
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
    typer.echo(f"Generating {num_ideas} ideas for pillar: '{pillar}'...")
    ideas = orchestrator.generate_ideas(pillar, num_ideas)
    if ideas:
        typer.echo("\n--- Generated Ideas ---")
        for i, idea in enumerate(ideas):
            typer.echo(f"Idea {i+1}:")
            typer.echo(f"  Title: {idea.title}")
            typer.echo(f"  Content Pillar: {idea.content_pillar}")
            typer.echo(f"  Defense: {idea.defense_of_idea}")
            typer.echo(f"  Expected Results: {idea.expected_results}")
            typer.echo("---")
    else:
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
    
    idea = PostIdea(
        title=idea_title,
        content_pillar=idea_pillar,
        defense_of_idea=idea_defense,
        expected_results=idea_results
    )
    
    typer.echo(f"Developing full post for idea: '{idea.title}'...")
    full_post = orchestrator.develop_post(idea, num_image_prompts)
    
    if full_post:
        typer.echo("\n--- Developed Post ---")
        typer.echo(f"Caption:\n{full_post['caption']}")
        typer.echo("\nImage Prompts:")
        for i, prompt in enumerate(full_post['image_prompts']):
            typer.echo(f"Prompt {i+1}: {prompt}")
        typer.echo("---")
    else:
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

    # For simplicity, we'll pass a dummy post_context for now.
    # In a real app, this would be a more structured object.
    post_context = {"query_for_context": post_context_query if post_context_query else original_content}

    typer.echo(f"Refining {component_type}...")
    revised_content = orchestrator.refine_content(component_type, original_content, user_feedback, post_context)
    
    if revised_content:
        typer.echo(f"\n--- Revised {component_type.capitalize()} ---")
        typer.echo(revised_content)
        typer.echo("---")
    else:
        typer.echo(f"Failed to refine {component_type}.")

if __name__ == "__main__":
    app()
