"""Tests for bot module."""


def test_bot_imports():
    from bot.discord_client import client, demo

    assert client is not None
    assert callable(demo)
