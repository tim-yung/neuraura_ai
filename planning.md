# neuraura_planning.md

## Project Vision
Build an open-source, production-ready Streamlit chatbot UI for LightRAG, deployable on Streamlit Community Cloud. The app supports chat history (contextual follow-ups) and developer-customizable system prompts.

## Architecture Overview
- **Frontend:** Streamlit app (Python)
- **Backend:** LightRAG API server (external, not part of this repo)
- **Deployment:** Streamlit Community Cloud (public, cloud-hosted, easy sharing)
- **Data Flow:**
    - User enters message in Streamlit UI
    - UI maintains chat history in session state
    - UI sends full chat history to LightRAG `/api/ollama/chat` endpoint (with `stream=true`)
    - UI streams and displays response as it arrives
    - Developer can set a custom system prompt (prompt injection)

## Tech Stack & Tools
- **Python** (primary language)
- **Streamlit** (UI framework)
- **Requests** (API calls)
- **Pydantic** (data validation)
- **Pytest** (unit testing)
- **Black** (code formatting)
- **GitHub Actions** (CI/CD, optional)

## Key Constraints & Considerations
- **Streamlit Community Cloud Requirements:**
    - Must include `requirements.txt` and `streamlit_app.py` at repo root
    - App must not require local files not present in repo
    - All secrets (e.g., API keys) must be managed via Streamlit secrets or environment variables
    - Resource limits: 1GB RAM, 1 vCPU, 800MB disk (approx.)
    - Use a `requirements.txt` for all Python dependencies (required by Streamlit Community Cloud)
    - Use only `uv` as the package manager, including for creating the virtual environment (do not use pip, poetry, or conda)
- **Chat History:**
    - Managed in Streamlit session state
    - Sent as a list of messages to backend each turn
- **Prompt Customization:**
    - UI exposes a text box for developer/system prompt
    - System prompt is sent in `system` field of API payload
- **Streaming:**
    - Use `requests` with `stream=True` to handle backend streaming
    - UI updates incrementally as data arrives

## Research & Pre-coding Instructions
- **LightRAG API Research:**
    - The LightRAG server is now hosted on Render: https://neuraura-lightrag.onrender.com/docs
    - Use the Tavily MCP tool to study the API endpoints and capabilities before integrating.
### API-Key to access LightRAG Server API
    - LIGHTRAG_API_KEY=neuraura-m2m-2025
    - WHITELIST_PATHS=/health,/api/*
- **Contextual Study:**
    - Use the Context7 MCP server with a 5000-token context window to study both LightRAG and Streamlit documentation before starting any coding tasks.
    - Summarize key API endpoints, expected payloads, and streaming behavior from LightRAG.
    - Review Streamlit best practices for chat UIs and session state management.
- **Package Management:**
    - All dependency management and virtual environment setup should be performed using `uv` only.
    - Document exact `uv` commands for environment setup in the README.

## Milestones
1. **Project Setup**
    - Create repo structure following Streamlit Community Cloud requirements
    - Add `neuraura_planning.md` and reference in onboarding/README
2. **Basic UI**
    - Build Streamlit chat interface (input, display, session state)
    - Implement chat history tracking
3. **API Integration**
    - Connect to LightRAG `/api/ollama/chat` endpoint
    - Support streaming responses
    - Add system prompt customization UI
4. **Testing**
    - Add Pytest unit tests for core logic
    - Edge, failure, and expected cases
5. **Deployment**
    - Add `requirements.txt`, `README.md`, and `Procfile` if needed
    - Deploy to Streamlit Community Cloud, validate streaming and history
6. **Documentation & Polish**
    - Update `README.md` with setup, usage, and deployment guide
    - Add code comments, docstrings, and inline reasoning
    - Ensure all code is PEP8 and Black formatted

## References
- Use the structure and decisions outlined in `PLANNING.md` for all further planning and coding.
- Reference this file at the start of any new conversation or planning session.

---

**Result:**
A robust, cloud-deployed Streamlit chatbot UI for LightRAG, supporting chat history, streaming, and prompt customization, with clean code, tests, and documentation.
