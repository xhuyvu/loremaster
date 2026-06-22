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
