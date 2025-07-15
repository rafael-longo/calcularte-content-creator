# Project Brief: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. Project Overview

The "Calcularte Content Engine" is a multi-agent AI system designed to automate the creation of high-quality, on-brand Instagram posts for the "Calcularte" brand. The system aims to replicate a collaborative creative workflow, from brand analysis to final content generation, to consistently produce creative ideas, captions, and image prompts aligned with Calcularte's brand voice.

## 2. Core Objectives

*   **Automate Content Creation:** Streamline the process of generating Instagram post ideas, captions, and image prompts.
*   **Ensure Brand Consistency:** Leverage a vector database of historical posts to maintain a consistent brand voice, tone, and style.
*   **Command-Line Interface (CLI) First:** Develop a robust backend and command-line interface (CLI) as the initial version for full post generation. (Completed)
*   **Modular Architecture:** Build a scalable and maintainable system with a clear separation of concerns between the backend, the multi-agent system, and the brand data.

## 3. Scope

*   **Initial Phase (CLI):** (Completed)
    *   Developed the core multi-agent system in Python.
    *   Implemented the Brand Voice Core using a local vector database (ChromaDB).
    *   Created a CLI to interact with the system for generating and refining content.
*   **Current Phase (FastAPI Backend):**
    *   Implement the API server to expose the agent functionalities via HTTP endpoints.
*   **Future Phase (Web UI):**
    *   Develop a React-based frontend with Tailwind CSS and DaisyUI.
    *   Integrate the frontend with the backend via a FastAPI server.

## 4. Target Audience

The primary user of this system is the project owner, who will use it to generate content for the Calcularte Instagram profile.
