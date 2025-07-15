# Technical Context: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. Technology Stack

*   **Language:** Python 3.11.8 (Managed by `pyenv`)
*   **Backend Framework:** FastAPI (Planned for next phase)
*   **Agent/LLM Framework:** OpenAI's Agents SDK (Core logic implemented)
*   **Vector Database:** ChromaDB (Implemented and functional)
*   **Embedding Model:** OpenAI's `text-embedding-3-small`
*   **Core LLM:** `gpt-4.1-mini` (via OpenAI API)
*   **CLI Framework:** Typer (Implemented and functional)
*   **Frontend (Future):** React, Tailwind CSS, DaisyUI
*   **Development Environment:** Ubuntu on WSL (Windows Subsystem for Linux)

## 2. Development Setup

*   **Dependencies:** Project dependencies are managed using `requirements.txt` and a Python virtual environment (`venv-calcularte-content-creator`).
*   **API Keys:** The OpenAI API key is managed via the `.env` file and accessed using `python-dotenv`.
*   **Data:** The raw data for the Brand Voice Core is located in the root directory (`dataset_instagram_calcularte_profile.jsonl` and `dataset_sample.jsonl`). The ChromaDB instance is persisted locally in `./chroma_db`.

## 3. Technical Constraints

*   **Local First:** The current version of the system runs entirely on a local machine, including the vector database.
*   **CLI-Driven:** The primary interface for the current phase is a command-line interface, with all core functionalities accessible through CLI commands.
*   **OpenAI Reliance:** The system's core intelligence relies on the OpenAI API for both embeddings and language model capabilities.

## 4. Tool Usage

*   **`gh` CLI:** Used for interacting with GitHub.
*   **`git`:** Used for version control.
*   **`pyenv`:** Used for managing Python versions and virtual environments.
*   **`python` / `pip`:** Used for running the application and managing dependencies.
*   **`typer`:** Used for building the command-line interface.
