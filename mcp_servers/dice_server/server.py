"""Dice MCP server for verifiable dice rolls."""

import asyncio

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dice-server")


@mcp.tool()
def roll_dice(count: int = 1, sides: int = 20) -> str:
    """Roll dice in NdS format. Returns individual results and sum."""
    # ponytail: uses `random` once real logic is added
    return f"Rolled {count}d{sides}: (stub)"




async def demo():
    """Self-check: verify tool registration."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "roll_dice" in tools, f"roll_dice not found in {tools}"
    print(f"OK — {len(tools)} tool(s) registered: {tools}")


if __name__ == "__main__":
    asyncio.run(demo())
