# Calcularte Content Engine: CLI User Manual

This manual provides instructions for using the Command-Line Interface (CLI) of the Calcularte Content Engine. This tool allows you to generate and refine Instagram post content using an AI-powered multi-agent system.

---

## 1. Setup and Installation

Before using the CLI, ensure you have Python 3.11.8 and `pyenv` installed.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rafael-longo/calcularte-content-creator.git
    cd calcularte-content-creator
    ```

2.  **Set up Python Environment (using pyenv):**
    ```bash
    pyenv virtualenv 3.11.8 venv-calcularte-content-creator
    pyenv local venv-calcularte-content-creator
    ```
    This will create a `.python-version` file in your project directory, ensuring the virtual environment is automatically activated when you navigate into this folder.

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set OpenAI API Key:**
    Create a file named `.env` in the root of the project directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE
    ```
    Replace `sk-YOUR_OPENAI_API_KEY_HERE` with your actual OpenAI API key.

---

## 2. Core CLI Commands

All commands are executed using `python src/main.py <command>`.

### 2.1. `session` - Manage Persistent Sessions

These commands allow you to manage conversational sessions, enabling the CLI to remember context across multiple commands.

**Usage:**

```bash
python src/main.py session <subcommand> [arguments]
```

#### `session start <name>` - Start or Switch Session

Starts a new session or switches to an existing one. All subsequent commands that support sessions will use this context.

**Usage:**

```bash
python src/main.py session start <session_name>
```

*   `<session_name>`: A unique name for your session (e.g., "my_campaign", "product_launch_v2").

**Example:**

```bash
python src/main.py session start my_new_campaign
```

#### `session status` - Check Active Session

Displays the name of the currently active session.

**Usage:**

```bash
python src/main.py session status
```

**Example:**

```bash
python src/main.py session status
```

#### `session end` - End Current Session

Ends the currently active session, clearing the local session state. This does not delete the session's history from the database.

**Usage:**

```bash
python src/main.py session end
```

**Example:**

```bash
python src/main.py session end
```

#### `session clear <name>` - Clear Session History

Permanently deletes all conversation history for a specific session from the database.

**Usage:**

```bash
python src/main.py session clear <session_name>
```

*   `<session_name>`: The name of the session whose history you want to clear.

**Example:**

```bash
python src/main.py session clear old_campaign_data
```

### 2.2. `ingest` - Ingest Brand Data

This command loads historical Instagram post data into the ChromaDB vector database, which the `BrandStrategistAgent` uses to understand the Calcularte brand voice.

**Usage:**

```bash
python src/main.py ingest [--sample | --full]
```

*   `--sample`: (Default) Ingests data from `dataset_sample.jsonl`. This is recommended for quick testing and development.
*   `--full`: Ingests data from `dataset_instagram_calcularte_profile.jsonl`. This contains the full dataset and may take longer.

**Example:**

```bash
python src/main.py ingest --sample
```

### 2.3. `maestro` - Autonomous Content Creation

This is the primary command for interacting with the system. The `MaestroAgent` will interpret your high-level prompts and use its toolset of other specialized agents to accomplish the task.

**Usage:**

```bash
python src/main.py maestro "<your_prompt>"
```

*   `<your_prompt>`: A high-level, conversational prompt describing what you want to achieve.

**Examples:**

```bash
# Generate a few ideas for a post about pricing
python src/main.py maestro "Gere 3 ideias de post sobre precificação para artesãs."

# Develop a full post from an idea
python src/main.py maestro "Desenvolva a ideia 'Descomplicando a Precificação' em um post completo, com legenda e 3 imagens."

# Ask for a brand report
python src/main.py maestro "Gere um relatório de voz da marca."
```

---

This manual covers all current functionalities of the Calcularte Content Engine CLI. For any issues or further development, please refer to the project's system specifications and agent instruction set documentation.
