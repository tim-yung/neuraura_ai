# Neuraura Streamlit Chatbot UI

**Login Required:** The app requires login for all access.
- Username: 
- Password: 
(Please reach out to the owner)

This app is a production-ready Streamlit chatbot UI for LightRAG, deployable on Streamlit Community Cloud.

## Features
- Chat UI with history and system prompt customization
- Streams responses from LightRAG API (hosted on Render)
- No user API key required (server API key managed via secrets)
- Loading spinner/indicator during server/API calls: uses Streamlit's st.spinner; lively/random phrase spinner was considered and reverted for simplicity

## Setup & Deployment

### 1. Configure Secrets
Create a `.streamlit/secrets.toml` file at the project root (or configure secrets in Streamlit Community Cloud UI) with:

```toml
LIGHTRAG_API_URL = "https://neuraura-lightrag.onrender.com/api/chat"
LIGHTRAG_API_KEY = "YOUR_API_KEY"
HEALTH_URL = "https://neuraura-lightrag.onrender.com/health"
HEALTH_PING_TIMEOUT_SEC = 180  # 3 minutes
STREAM_RESPONSE_TIMEOUT_SEC = 120  # 2 minutes
```

### 2. Install dependencies (locally)
```sh
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Run locally
```sh
streamlit run streamlit_app.py
```

When you open the app, you will be prompted to log in before accessing any features. Use the credentials above.

### 4. Streamlit Community Cloud
- Place `requirements.txt` and `streamlit_app.py` at repo root.
- Add the above secrets in the Community Cloud UI under "App secrets".

### 5. Run tests
- Unit tests for login logic are in `tests/test_login.py`.
- Unit tests for API revive and chat streaming logic are in `tests/test_streamlit_app.py`.
- To run all tests in both files:
  ```bash
  pytest tests/
  ```
  Or, to run them individually:
  ```bash
  pytest tests/test_login.py
  pytest tests/test_streamlit_app.py
  ```

### Real API Integration Test

- The chat logic test file (`tests/test_streamlit_app.py`) includes a real API integration test.
- By default, this test is **skipped**.
- To run the real API test, use the `--realapi` flag:
  ```bash
  pytest tests/test_streamlit_app.py --realapi
  ```
- This test requires a valid `.streamlit/secrets.toml` and internet access. It will send a real request to the LightRAG backend and verify the response.

### 6. System Prompt & Timeout

- You can set a custom system prompt in the sidebar and must click **"Update System Prompt"** for it to take effect.
- The current system prompt is logged for every API request (see `streamlit_app.log`).
- The chat API timeout is set to **2 minutes** to support long responses.
- The system prompt is sent in the `system` field of the API payload, as per the [LightRAG API docs](https://neuraura-lightrag.onrender.com/redoc). If the model ignores the prompt, this is a backend/model issue.

### Troubleshooting
- If your system prompt is ignored, check the backend or LLM configuration.
- All logs (including system prompt and timing) are saved in `streamlit_app.log` for debugging.
- Health check: `GET /health`

## Project Structure
```
.
├── requirements.txt
├── streamlit_app.py
├── tests/
│   └── test_streamlit_app.py
│   └── test_login.py
└── README.md
```
