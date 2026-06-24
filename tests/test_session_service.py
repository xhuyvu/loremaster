"""Tests for FileSessionService."""

import os
import tempfile

import pytest


@pytest.mark.asyncio
async def test_create_and_reload():
    from agents.session_service import FileSessionService
    from google.adk.sessions import Session

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    try:
        svc = FileSessionService(path)
        s = await svc.create_session(app_name="test", user_id="u1", session_id="s1")
        assert isinstance(s, Session)
        assert s.id == "s1"

        svc2 = FileSessionService(path)
        s2 = await svc2.get_session(app_name="test", user_id="u1", session_id="s1")
        assert s2 is not None
        assert s2.id == "s1"
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_persists_state():
    from agents.session_service import FileSessionService

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    try:
        svc = FileSessionService(path)
        await svc.create_session(
            app_name="test", user_id="u1", session_id="s1", state={"hp": "42"}
        )
        svc2 = FileSessionService(path)
        s2 = await svc2.get_session(app_name="test", user_id="u1", session_id="s1")
        assert s2.state.get("hp") == "42"
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_empty_file():
    from agents.session_service import FileSessionService

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    try:
        svc2 = FileSessionService(path)
        assert svc2 is not None
    finally:
        os.unlink(path)
