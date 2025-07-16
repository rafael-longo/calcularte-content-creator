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

### 2.2. `plan-content` - Generate a Strategic Content Plan

This command leverages the enhanced `BrandStrategistAgent` to generate a proactive, strategic content plan for a specified time frame. It considers seasonality, historical performance, and content variety.

**Usage:**

```bash
python src/main.py plan-content "<time_frame>"
```

*   `<time_frame>`: The duration for the content plan (e.g., "week", "month", "quarter"). Enclose in quotes if it contains spaces.

**Example:**

```bash
python src/main.py plan-content "week"
```

### 2.3. `report brand-voice` - Generate a Brand Voice Report

This command triggers the `BrandStrategistAgent` to perform a holistic analysis of the brand's voice and generates a comprehensive, human-readable report. This is useful for gaining a deep understanding of the brand's communication style at a glance.

**Usage:**

```bash
python src/main.py report brand-voice
```

**Example:**

```bash
python src/main.py report brand-voice
```

### 2.4. `plan` - Plan Content Ideas

This command provides a flexible way to generate a list of structured `PostIdea` objects based on the high-level strategic plan. It's perfect for when you want to see the creative ideas before committing to full post development.

**Usage:**

```bash
python src/main.py plan [--for "<time_frame>" | --num <number_of_ideas>]
```

*   `--for "<time_frame>"`: The time frame to plan for (e.g., "week", "month"). The command will generate one idea for each strategic point in the plan for that period.
*   `--num <number_of_ideas>`: The specific number of ideas to generate. The command will generate a plan and then create ideas for the first `n` points.
*   **Note:** You must use either `--for` or `--num`, but not both.

**Examples:**

```bash
# Plan ideas for the next week
python src/main.py plan --for "week"

# Plan exactly 2 ideas
python src/main.py plan --num 2
```

### 2.5. `plan-and-develop` - Autonomous Post Generation

This is the most powerful command. It runs the entire content creation workflow autonomously. It first generates the strategic plan, then brainstorms ideas for each point, and finally develops each idea into a full post with a caption and image prompts.

**Usage:**

```bash
python src/main.py plan-and-develop [--for "<time_frame>" | --num <number_of_posts>]
```

*   `--for "<time_frame>"`: The time frame for which to autonomously generate a full content calendar.
*   `--num <number_of_posts>`: The specific number of full posts to generate from start to finish.
*   **Note:** You must use either `--for` or `--num`, but not both.

**Examples:**

```bash
# Autonomously create all content for the next week
python src/main.py plan-and-develop --for "week"

# Autonomously create 3 full posts
python src/main.py plan-and-develop --num 3
```

### 2.6. `ask-strategist` - Query Brand Strategist

This command allows you to query the `BrandStrategistAgent` to retrieve content from the brand's historical data that is semantically similar to your query. This is useful for understanding the brand's tone, style, and relevant topics.

**Usage:**

```bash
python src/main.py ask-strategist "<your_query_text>"
```

*   `<your_query_text>`: The text query you want to use to find relevant brand content. Enclose in quotes if it contains spaces.

**Example:**

```bash
python src/main.py ask-strategist "Como organizar as finanças do meu negócio artesanal?"
```

### 2.7. `generate-ideas` - Generate New Post Ideas

This command uses the `CreativeDirectorAgent` (orchestrated by the `OrchestratorAgent`) to brainstorm new Instagram post concepts based on a specified content pillar.

**Usage:**

```bash
python src/main.py generate-ideas "<content_pillar>" [--num <number_of_ideas>]
```

*   `<content_pillar>`: The main topic or strategic category for the post ideas (e.g., "Organização Financeira", "Precificação", "Marketing para Artesanato"). Enclose in quotes if it contains spaces.
*   `--num <number_of_ideas>`: (Optional) The number of ideas to generate. Defaults to 3.

**Example:**

```bash
python src/main.py generate-ideas "Produtividade para Artesãs" --num 2
```

### 2.8. `develop-post` - Develop a Full Post

This command takes a selected post idea (title, pillar, defense, and expected results) and uses the `OrchestratorAgent` to generate a complete Instagram caption (via `CopywriterAgent`) and a series of detailed image prompts (via `ArtDirectorAgent`).

**Usage:**

```bash
python src/main.py develop-post "<idea_title>" "<idea_pillar>" "<idea_defense>" "<idea_results>" [--num-images <number_of_content_images>]
```

*   `<idea_title>`: The catchy title of the post idea.
*   `<idea_pillar>`: The content pillar of the idea.
*   `<idea_defense>`: A brief justification for the idea.
*   `<idea_results>`: The expected outcomes of the post.
*   `--num-images <number_of_content_images>`: (Optional) The number of content image prompts to generate. The system will automatically add one final CTA slide prompt. Defaults to 3 content image prompts.

**Important:** Ensure you enclose each argument in quotes if it contains spaces.

**Example (using an idea generated from `generate-ideas`):**

```bash
python src/main.py develop-post "Descomplicando a Precificação: Seu Lucro na Ponta do Lápis!" "Precificação" "Este post oferece dicas práticas e mostra como o Calcularte simplifica a precificação para artesãs." "Aumentar o engajamento e direcionar tráfego para o Calcularte." --num-images 2
```

### 2.9. `refine-content` - Refine Content with Feedback

This command allows you to refine a specific piece of generated content (like a caption or an image prompt) using the `ReviewerAgent` (orchestrated by the `OrchestratorAgent`) based on your feedback.

**Usage:**

```bash
python src/main.py refine-content "<component_type>" "<original_content>" "<user_feedback>" [--context-query "<query_for_context>"]
```

*   `<component_type>`: The type of content to refine. Currently supported: `caption` or `prompt`.
*   `<original_content>`: The full text of the content you want to refine. Enclose in quotes.
*   `<user_feedback>`: Your specific feedback or instructions for refinement. Enclose in quotes.
*   `--context-query "<query_for_context>"`: (Optional) A query to help the `ReviewerAgent` fetch additional relevant brand context for the refinement. If not provided, the `original_content` will be used as the context query.

**Example (refining a caption):**

```bash
python src/main.py refine-content caption "Sabe aquela sensação de que o dinheiro escorre pelos dedos? 💸 Com o Calcularte, você vê para onde cada centavo vai! Precificar não precisa ser um bicho de sete cabeças! 💡 A gente te ajuda a dar o preço justo e ter lucro de verdade. **Calcularte** é a ferramenta que te dá clareza e controle. Chega de trabalhar de graça! ✅ O que você mais tem dificuldade na precificação? Conta pra gente nos comentários! 👇 Salve e compartilhe este post com uma amiga empreendedora! 🚀 (Conheça a ferramenta em) calcularte.com.br (link na bio!)" "Make the call to action more direct and add a strong sense of urgency."
```

---

This manual covers all current functionalities of the Calcularte Content Engine CLI. For any issues or further development, please refer to the project's system specifications and agent instruction set documentation.
