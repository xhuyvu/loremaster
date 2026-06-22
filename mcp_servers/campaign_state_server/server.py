"""Campaign state MCP server for long-term memory."""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("campaign-state-server")


@mcp.tool()
def get_state(key: str) -> str:
    """Read a value from the campaign state store by key."""
    return f"get_state('{key}'): (stub)"


@mcp.tool()
def set_state(key: str, value: str) -> str:
    """Write a key-value pair to the campaign state store."""
    return f"set_state('{key}', '{value}'): (stub)"




async def demo():
    """Self-check: verify tool registration."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "get_state" in tools, f"get_state not found in {tools}"
    assert "set_state" in tools, f"set_state not found in {tools}"
    print(f"OK — {len(tools)} tool(s) registered: {tools}")


if __name__ == "__main__":
    asyncio.run(demo())
