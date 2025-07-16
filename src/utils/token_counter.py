import tiktoken
from agents import SQLiteSession

def get_session_token_count(session: SQLiteSession) -> int:
    """
    Calculates the total token count of a session's history.

    Args:
        session: The SQLiteSession object.

    Returns:
        The total number of tokens in the session's history.
    """
    if not session:
        return 0

    encoding = tiktoken.get_encoding("cl100k_base")
    
    try:
        # This is a synchronous workaround to call an async method.
        # In a real async application, you would `await session.get_items()`.
        import asyncio
        items = asyncio.run(session.get_items())
    except RuntimeError:
        # If an event loop is already running, use it.
        items = asyncio.get_event_loop().run_until_complete(session.get_items())

    token_count = 0
    for item in items:
        if content := item.get("content"):
            if isinstance(content, str):
                token_count += len(encoding.encode(content))
    return token_count
