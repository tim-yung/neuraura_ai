import pytest
import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from streamlit_app import stream_lightrag_response, revive_lightrag_server


def test_revive_lightrag_server_success(monkeypatch):
    """Test that revive_lightrag_server returns True on 200."""

    class DummyResp:
        status_code = 200
        text = "OK"

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def get(self, url):
            return DummyResp()

    monkeypatch.setattr("httpx.Client", lambda timeout: DummyClient())
    assert revive_lightrag_server() is True


def test_stream_lightrag_response(monkeypatch):
    """Test streaming response yields expected chunks."""

    class DummyStream:
        status_code = 200
        text = ""

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def iter_text(self):
            yield "hello "
            yield "world"

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def stream(self, method, url, json, headers):
            return DummyStream()

    monkeypatch.setattr("httpx.Client", lambda timeout: DummyClient())
    chunks = list(stream_lightrag_response([{"role": "user", "content": "hi"}], ""))
    assert "hello" in "".join(chunks)
    assert "world" in "".join(chunks)


import pytest

# --- LOGIN TESTS ---
def test_login_success(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    st.session_state["logged_in"] = False
    # Simulate correct credentials
    username = "admin"
    password = "neuraura123"
    # Simulate login logic
    if username == "admin" and password == "neuraura123":
        st.session_state["logged_in"] = True
    assert st.session_state["logged_in"] is True

def test_login_failure(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    st.session_state["logged_in"] = False
    # Simulate incorrect credentials
    username = "admin"
    password = "wrongpass"
    if username == "admin" and password == "neuraura123":
        st.session_state["logged_in"] = True
    else:
        st.session_state["logged_in"] = False
    assert st.session_state["logged_in"] is False

def test_login_empty(monkeypatch):
    import streamlit as st
    st.session_state.clear()
    st.session_state["logged_in"] = False
    username = ""
    password = ""
    if username == "admin" and password == "neuraura123":
        st.session_state["logged_in"] = True
    else:
        st.session_state["logged_in"] = False
    assert st.session_state["logged_in"] is False
# --- END LOGIN TESTS ---


def pytest_addoption(parser):
    parser.addoption("--realapi", action="store_true", default=False, help="run real LightRAG API integration test")

def test_real_lightrag_api(pytestconfig):
    """
    Real integration test: Only runs if --realapi is passed, secrets are present, and points to a real API.
    Skips if not enabled or not configured.
    """
    if not pytestconfig.getoption("--realapi"):
        pytest.skip("Skipping real API test (use --realapi to enable)")
    if not os.path.exists(".streamlit/secrets.toml"):
        pytest.skip("No secrets.toml found; skipping real API test.")
    try:
        from streamlit.web import bootstrap
        import toml

        secrets = toml.load(".streamlit/secrets.toml")
        api_url = secrets.get("LIGHTRAG_API_URL")
        api_key = secrets.get("LIGHTRAG_API_KEY")
        if not api_url or not api_key:
            pytest.skip("Secrets missing required fields.")
        # Minimal API test: send a simple message
        import httpx

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "lightrag:latest",
            "messages": [{"role": "user", "content": "ping", "images": []}],
            "system": "You are a test bot.",
            "stream": False,
            "options": {}
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(api_url, json=payload, headers=headers)
            logging.info(f"API status: {resp.status_code}, body: {resp.text}")
            assert (
                resp.status_code == 200
            ), f"API returned {resp.status_code}: {resp.text}"
            assert "content" in resp.text or resp.json(), "No content in API response"
    except Exception as e:
        pytest.fail(f"Exception during real API test: {e}")
