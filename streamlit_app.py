"""
streamlit_app.py
Main entrypoint for Streamlit Community Cloud chatbot UI for LightRAG.
"""

import os
import streamlit as st
import httpx
import logging
from typing import List, Dict, Any
from pydantic import BaseModel

# Set Streamlit page config FIRST (must be before any other Streamlit command)
st.set_page_config(page_title="Ask Betsy! - Neuraura", page_icon="🤖")

# Configure logger
logger = logging.getLogger("neuraura_streamlit")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
# Also log to file for debugging
file_handler = logging.FileHandler("streamlit_app.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(file_handler)

# Reference: https://docs.streamlit.io/develop/api-reference/connections/secrets
LIGHTRAG_API_URL = st.secrets.get("LIGHTRAG_API_URL", None)
LIGHTRAG_API_KEY = st.secrets.get("LIGHTRAG_API_KEY", None)
HEALTH_URL = st.secrets.get(
    "HEALTH_URL", "https://neuraura-lightrag.onrender.com/health"
)
HEALTH_PING_TIMEOUT_SEC = int(
    st.secrets.get("HEALTH_PING_TIMEOUT_SEC", 180)
)  # 3 minutes default
STREAM_RESPONSE_TIMEOUT_SEC = int(
    st.secrets.get("STREAM_RESPONSE_TIMEOUT_SEC", 120)
)  # 2 minutes default

if not LIGHTRAG_API_URL or not LIGHTRAG_API_KEY:
    st.error(
        "Missing required secrets: LIGHTRAG_API_URL and/or LIGHTRAG_API_KEY. Please configure them in Streamlit secrets."
    )
    st.stop()


class Message(BaseModel):
    role: str
    content: str
    images: list[str] = []


class OllamaChatRequest(BaseModel):
    model: str = "lightrag:latest"
    messages: List[Dict[str, Any]]
    system: str = ""
    stream: bool = True
    options: dict = {}


def revive_lightrag_server():
    """
    Ping the health endpoint to revive the Render server.

    Uses HEALTH_PING_TIMEOUT_SEC from secrets (default 180s).
    """
    logger.info("Pinging LightRAG health endpoint: %s", HEALTH_URL)
    try:
        with httpx.Client(timeout=HEALTH_PING_TIMEOUT_SEC) as client:
            resp = client.get(HEALTH_URL)
            logger.debug("Health endpoint response: %s %s", resp.status_code, resp.text)
            return resp.status_code == 200
    except Exception as e:
        logger.error("Exception during health check: %s", e)
        return False


def stream_lightrag_response(messages: List[Dict[str, str]], system_prompt: str) -> str:
    """
    Stream response from LightRAG API, yielding parsed content chunks only.
    Logs request duration and uses STREAM_RESPONSE_TIMEOUT_SEC from secrets (default 120s).
    Logs the system prompt used for each request.
    """
    import json
    import time

    headers = (
        {"Authorization": f"Bearer {LIGHTRAG_API_KEY}"} if LIGHTRAG_API_KEY else {}
    )
    payload = OllamaChatRequest(
        model="lightrag:latest",
        messages=messages,
        system=system_prompt,
        stream=True,
        options={},
    ).model_dump()
    logger.info("Sending chat request to LightRAG API: %s", LIGHTRAG_API_URL)
    logger.debug("Payload: %s", payload)
    response_text = ""
    start = time.time()
    try:
        with httpx.Client(timeout=STREAM_RESPONSE_TIMEOUT_SEC) as client:
            with client.stream(
                "POST", LIGHTRAG_API_URL, json=payload, headers=headers
            ) as resp:
                logger.info("API response status: %s", resp.status_code)
                buffer = ""
                for chunk in resp.iter_text():
                    if chunk:
                        logger.debug("Received chunk: %s", chunk)
                        buffer += chunk
                        # Try to parse as many JSON objects as possible from buffer
                        while True:
                            buffer = buffer.lstrip()
                            if not buffer:
                                break
                            try:
                                obj, idx = json.JSONDecoder().raw_decode(buffer)
                                buffer = buffer[idx:]
                                # Only yield assistant content chunks
                                if (
                                    isinstance(obj, dict)
                                    and "message" in obj
                                    and obj["message"]
                                    and "content" in obj["message"]
                                ):
                                    content = obj["message"]["content"]
                                    if content:
                                        response_text += content
                                        yield content
                                # If done:true, break
                                if obj.get("done"):
                                    logger.info(
                                        "Streaming done after %.2fs",
                                        time.time() - start,
                                    )
                                    break
                            except json.JSONDecodeError:
                                # Wait for more data
                                break
        logger.info("Streaming completed in %.2fs", time.time() - start)
    except Exception as e:
        logger.error(
            "Exception during streaming after %.2fs: %s", time.time() - start, e
        )
        yield f"[Error: {e}]"


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "system_prompt" not in st.session_state:
        st.session_state[
            "system_prompt"
        ] = """You are Betsy the Beaver, a compassionate assistant in a PCOS community app developed by Neuraura, 
              supporting users by bridging clinical terms and everyday language with evidence-based insights 
              from Neuraura’s curated articles (latest PCOS research up to May 2025) on symptoms, treatments, lifestyle, 
              and emotional well-being. Use a warm, cheeky, empathetic tone like a concerned aunt, 
              with varied endearments like “love,” “sweetie,” or “superstar,” simple language, and a touch of humor. 
              Translate complex terms (e.g., “insulin resistance” to “struggling with sugar energy”). 
              Keep responses short (1-2 sentences advice, 1-2 sentences explanation), validate feelings, 
              and ask follow-ups (e.g., “How’s that been feeling?”).
              Be direct, supportive, fun, and smart, prioritizing emotional support for PCOS’s sensitive nature. 
              Never diagnose or treat; suggest consulting a healthcare professional if unsure, for urgent cases (e.g., crises),
              or if info’s unavailable (e.g., “I don’t have that, sweetie—ask your doctor?”). 
              Personalize with user details (e.g., pets).
        """
    if "server_awake" not in st.session_state:
        st.session_state["server_awake"] = False


def main():
    """
    Main entrypoint for the Ask Betsy! Streamlit chat UI.

    - Initializes session state and sidebar controls.
    - Handles chat history and user input.
    - Streams responses from the LightRAG backend, updating UI incrementally.
    - Displays a medical disclaimer in the sidebar.
    - Ensures the backend is awake before sending chat requests.

    Returns:
        None
    """
    # --- LOGIN PAGE ---
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        st.title("Login")
        with st.form(key="login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login")
        if submit:
            if username == "admin" and password == "neuraura123":
                st.session_state["logged_in"] = True
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.warning("Incorrect username or password.")
        return
    # --- END LOGIN PAGE ---

    st.title("Ask Betsy!")
    st.markdown("_Developed by M2M Tech for Neuraura_")

    init_session_state()

    with st.sidebar:
        st.header("System Prompt")
        system_prompt = st.text_area(
            "Set system prompt", st.session_state["system_prompt"]
        )
        # Allow developer/system prompt customization
        if st.button("Update System Prompt"):
            st.session_state["system_prompt"] = system_prompt
            st.success("System prompt updated!")
        st.markdown("---")
        st.info(
            """**Disclaimer**\n\nThe information provided by Ask Betsy! is intended for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read in this content. If you are experiencing a medical emergency, call your doctor or emergency services immediately."""
        )

    # Display chat history from session state
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Accept user input and handle chat logic
    if prompt := st.chat_input("Type your message and press Enter..."):
        # Ensure Render API is awake before sending chat request
        max_retries = 4
        for attempt in range(max_retries):
            with st.spinner(
                f"Waking up Ask Betsy! from inactive state... (attempt {attempt+1})"
            ):
                if revive_lightrag_server():
                    break
                elif attempt == max_retries - 1:
                    st.error(
                        "Failed to reach Ask Betsy! after multiple attempts. Try again later."
                    )
                    st.stop()
        # Add user message to chat history
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Stream assistant response with a loading spinner
        with st.chat_message("assistant"):
            with st.spinner("Ask Betsy! is thinking..."):
                response = ""
                # Stream response from LightRAG API, updating UI as chunks arrive
                resp_gen = stream_lightrag_response(
                    st.session_state["messages"], st.session_state["system_prompt"]
                )
                resp_container = st.empty()
                for chunk in resp_gen:
                    response += chunk
                    resp_container.markdown(response)
                # Save assistant response to chat history
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    main()
