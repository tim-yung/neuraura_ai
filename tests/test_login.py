"""
test_login.py
Pytest unit tests for login logic in streamlit_app.py.
"""
import pytest
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Login credentials (should match main app)
LOGIN_ID = "admin"
PASSWORD = "neuraura123"

# Helper function to simulate login logic

def authenticate(username: str, password: str) -> bool:
    """
    Returns True if credentials match, False otherwise.
    """
    return username == LOGIN_ID and password == PASSWORD

def test_login_success():
    assert authenticate("admin", "neuraura123") is True

def test_login_wrong_password():
    assert authenticate("admin", "wrongpass") is False

def test_login_wrong_username():
    assert authenticate("user", "neuraura123") is False

def test_login_empty_fields():
    assert authenticate("", "") is False
    assert authenticate("admin", "") is False
    assert authenticate("", "neuraura123") is False
