# **Enhancement Plan 6: Implement Persistent Session Memory for CLI**

* **Objective:** To make the CLI stateful by leveraging the OpenAI Agents SDK's built-in `SQLiteSession` feature, allowing the system to "remember" context between commands for a fluid, conversational user experience.
* **Key System Modifications:**
  * **Adopt `SQLiteSession`:** Instead of creating a custom session manager, the system will directly use the `agents.SQLiteSession` class provided by the SDK. This class natively handles the creation, loading, saving, and clearing of conversational history in a local SQLite database file.
  * **`main.py` Logic:**
    * The main CLI application will be the primary manager of the session object.
    * When a session is started or loaded, a `SQLiteSession` instance will be created (e.g., `session = SQLiteSession(session_id="my_campaign")`).
    * This session object will then be passed directly to the `Runner.run()` method for all relevant agent commands, as shown in the SDK documentation. The SDK will handle the rest of the state management automatically.
* **File System Changes:**
  * **No new agent files needed.** The logic will be centralized in `src/main.py`.
  * **No `sessions/` directory needed.** The `SQLiteSession` will manage its own database file (e.g., `sessions.db`), which should be added to `.gitignore`.
  * **Modified:** `src/main.py` (to manage session commands and pass the session object to the Runner).
* **CLI Command Updates:**
  * **New Command Group:** `session`.
    * `python src/main.py session start <name>`: Informs the user that a new session with the given name is now active.
    * `python src/main.py session status`: Shows the name of the currently active session.
    * `python src/main.py session end`: Clears the currently active session name.
    * `python src/main.py session clear <name>`: Calls the `.clear_session()` method on the specified session to wipe its history.
  * **Modified Commands:** All commands that need context (like `plan`, `develop-post`, `refine-content`) will be updated to check for an active session and pass the corresponding `SQLiteSession` object to the `Runner.run()` call.
