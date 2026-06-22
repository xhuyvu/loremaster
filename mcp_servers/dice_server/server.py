"""Dice MCP server for verifiable dice rolls."""

import asyncio
from random import randint

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dice-server")

_MAX_COUNT = 100


@mcp.tool()
def roll_dice(count: int = 1, sides: int = 20) -> str:
    """Roll dice in NdS format. Returns individual results and sum."""
    if count < 1:
        raise ValueError(f"count must be >= 1, got {count}")
    if sides < 2:
        raise ValueError(f"sides must be >= 2, got {sides}")
    if count > _MAX_COUNT:
        raise ValueError(f"count must be <= {_MAX_COUNT}, got {count}")
    results = [randint(1, sides) for _ in range(count)]
    total = sum(results)
    return f"Rolled {count}d{sides}: {results} (total: {total})"


async def demo():
    """Self-check: verify tool registration and basic rolling."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "roll_dice" in tools, f"roll_dice not found in {tools}"

    result = roll_dice(2, 6)
    assert "total:" in result, f"unexpected format: {result}"
    print(f"OK — {tools}, sample: {result}")

    try:
        roll_dice(0, 6)
        assert False, "expected ValueError for count=0"
    except ValueError:
        pass

    try:
        roll_dice(1, 1)
        assert False, "expected ValueError for sides=1"
    except ValueError:
        pass

    print("OK — all edge cases handled")


if __name__ == "__main__":
    asyncio.run(demo())
