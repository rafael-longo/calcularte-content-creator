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
            asyncio.run(session_to_clear.clear_session())
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

    async def stream_maestro():
        final_output = None
        thought_buffer = "" # Buffer to accumulate thought chunks

        # Use run_streamed() which returns a result object, then iterate over stream_events()
        result = Runner.run_streamed(maestro_agent, prompt, session=session, max_turns=20)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, 'delta') and event.data.delta:
                # Accumulate the thought chunks
                thought_buffer += event.data.delta
                # Use typer.secho for direct, unformatted console output
                typer.secho(event.data.delta, nl=False, fg="magenta")
            
            # Log the complete thought when a tool is called (signaling the end of a thought)
            elif event.type == "run_item_stream_event" and hasattr(event.item, 'type') and event.item.type == "tool_call_item":
                if thought_buffer:
                    log.log("THOUGHT", thought_buffer.replace("{", "{{").replace("}", "}}"))
                    thought_buffer = "" # Reset buffer

                # A tool has been called. Print a newline to the console.
                typer.echo()
                # Access the tool call info from the raw_item attribute
                log.info(f"Tool Call: {event.item.raw_item.name} with args: {event.item.raw_item.arguments}")

        # Log any remaining thoughts in the buffer after the loop finishes
        if thought_buffer:
            log.log("THOUGHT", thought_buffer.replace("{", "{{").replace("}", "}}"))

        return result.final_output

    final_output = asyncio.run(stream_maestro())
      
    if final_output:
        log.success("Maestro command finished successfully.")
        typer.echo("\n\n--- Maestro's Final Response ---")
        typer.echo(str(final_output))
        typer.echo("--------------------------------")
    else:
        log.error("Maestro command finished with no output.")
        typer.echo("\nMaestro command finished with no output.")


if __name__ == "__main__":
    app()
