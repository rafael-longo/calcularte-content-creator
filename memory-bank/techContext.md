# Technical Context: Calcularte Content Engine

**Version:** 1.0
**Date:** July 12, 2025

## 1. Technology Stack

*   **Language:** Python 3.10+
*   **Backend Framework:** FastAPI
*   **Agent/LLM Framework:** OpenAI's Agents SDK
*   **Vector Database:** ChromaDB
*   **Embedding Model:** OpenAI's `text-embedding-3-small`
*   **Core LLM:** `gpt-4.1-mini` (via OpenAI API)
*   **Frontend (Future):** React, Tailwind CSS, DaisyUI
*   **Development Environment:** Ubuntu on WSL (Windows Subsystem for Linux)

## 2. Development Setup

*   **Dependencies:** Project dependencies will be managed using a `requirements.txt` file and a Python virtual environment.
*   **API Keys:** The OpenAI API key will be managed using environment variables to avoid hardcoding secrets.
*   **Data:** The raw data for the Brand Voice Core is located in the root directory (`dataset_instagram_calcularte_profile.jsonl` and `dataset_sample.jsonl`).

## 3. Technical Constraints

*   **Local First:** The initial version of the system is designed to run entirely on a local machine, including the vector database. This simplifies setup and reduces reliance on cloud services.
*   **CLI-Driven:** The primary interface for the initial phase will be a command-line interface. All core functionalities must be accessible through CLI commands.
*   **OpenAI Reliance:** The system's core intelligence relies on the OpenAI API for both embeddings and language model capabilities.

## 4. Tool Usage

*   **`gh` CLI:** Used for interacting with GitHub, including repository creation and management.
*   **`git`:** Used for version control.
*   **`python` / `pip`:** Used for running the application and managing dependencies.
