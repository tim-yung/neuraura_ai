# TASK.md

Purpose: Tracks current tasks, backlog, and sub-tasks.
Includes: Bullet list of active work, milestones, and anything discovered mid-process.
Prompt to AI: “Update TASK.md to mark XYZ as done and add ABC as a new task.”

---

## Milestones & Major Tasks
- [ ] Project setup for Streamlit Community Cloud (requirements.txt, streamlit_app.py at root, .env for secrets)
- [x] Implement simple login page (all app access requires login; credentials: admin/neuraura123)
    - [x] Pytest unit tests for login logic
- [ ] Integrate LightRAG API (ensure health endpoint is called to revive deployment before chat)
- [x] Chat UI: maintain chat history, support system prompt customization (now with button, logging, and 2-min timeout)
- [x] Streaming: stream chat responses by token (not in large chunks or with 5s delay); parses JSONL chunks for clean output
- [x] Add loading spinner/indicator during server wake-up or API calls (used Streamlit's built-in st.spinner for reliability; lively random phrase spinner was considered and reverted for simplicity)
- [ ] Pytest unit tests for all major features (happy path, edge, failure)
- [ ] Deployment to Streamlit Community Cloud
- [x] Documentation: update README with setup, usage, uv commands, deployment guide, and system prompt/troubleshooting notes

## Backlog / Discovered During Work
- [ ] Add GitHub Actions for CI/CD (optional)
- [ ] Polish UI/UX based on user feedback
- [ ] Investigate why system prompt may be ignored by backend/model (confirmed frontend is correct)
- [x] Study LightRAG /chat endpoint and system prompt handling at code level (see Technical Note below)
- [ ] Add option to customize system prompt for /query endpoint (not currently supported in backend)

## Subtasks
- [x] Use Tavily MCP to study https://neuraura-lightrag.onrender.com/api and /redoc for correct API usage
- [ ] Use Context7 MCP server (5000 tokens) to study LightRAG and Streamlit docs before coding
- [x] Document uv-based virtual environment and dependency setup in README

---

## Technical Note: LightRAG System Prompt Handling (2025-04-24)

- The LightRAG server exposes two main chat endpoints: `/api/chat` and `/api/query` (`/query/stream`).
- The `/api/chat` endpoint supports a `system` parameter for customizing the system prompt, but **this only works when the query mode is `/bypass`** (i.e., pure LLM, no retrieval-augmentation). In this mode, the system prompt is passed as `system_prompt` to the LLM backend.
- For all other modes (RAG modes: hybrid, local, global, etc.), the `system` parameter is ignored; the system prompt is not injected into the LLM prompt.
- The `/api/query` and `/api/query/stream` endpoints **do not support customizing the system prompt**. Their request models do not include a `system` or `system_prompt` field, and there is no code path to inject a custom system prompt into the LLM prompt for RAG queries.
- To enable system prompt customization for RAG, the backend would need to be extended: add a `system` field to the request model, propagate it through the retrieval pipeline, and pass it to the LLM backend.

_Last updated: 2025-04-24_
