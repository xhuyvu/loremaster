"""Tests for MCP server modules."""

import pytest


@pytest.mark.asyncio
async def test_dice_server_demo():
    from mcp_servers.dice_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "roll_dice" in tools


@pytest.mark.asyncio
async def test_srd_server_demo():
    from mcp_servers.srd_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "query_srd" in tools


@pytest.mark.asyncio
async def test_campaign_state_server_demo():
    from mcp_servers.campaign_state_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "get_state" in tools
    assert "set_state" in tools


class TestCampaignState:
    def test_set_and_get(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("hp", "42")
        assert get_state("hp") == "42"
        _DATA_FILE.unlink(missing_ok=True)

    def test_missing_key(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        assert get_state("nonexistent") == ""
        _DATA_FILE.unlink(missing_ok=True)

    def test_overwrite(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("gold", "100")
        set_state("gold", "200")
        assert get_state("gold") == "200"
        _DATA_FILE.unlink(missing_ok=True)

    def test_persistence(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("quest", "save the village")
        v1 = get_state("quest")
        v2 = get_state("quest")
        assert v1 == v2 == "save the village"
        _DATA_FILE.unlink(missing_ok=True)
