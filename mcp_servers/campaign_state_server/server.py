"""Campaign state MCP server for long-term memory."""

import asyncio
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("campaign-state-server")

_DATA_FILE = Path(__file__).parent / "campaign_state.json"


def _load() -> dict:
    if _DATA_FILE.exists():
        return json.loads(_DATA_FILE.read_text())
    return {}


def _save(data: dict) -> None:
    _DATA_FILE.write_text(json.dumps(data, indent=2))


@mcp.tool()
def get_state(key: str) -> str:
    """Read a value from the campaign state store by key."""
    data = _load()
    return data.get(key, "")


@mcp.tool()
def set_state(key: str, value: str) -> str:
    """Write a key-value pair to the campaign state store."""
    data = _load()
    data[key] = value
    _save(data)
    return f"set_state('{key}', '{value}'): OK"




async def demo():
    """Self-check: verify tool registration and basic KV operations."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "get_state" in tools
    assert "set_state" in tools

    if _DATA_FILE.exists():
        _DATA_FILE.unlink()

    result = set_state("test_key", "test_value")
    assert "OK" in result, f"unexpected: {result}"

    value = get_state("test_key")
    assert value == "test_value", f"expected test_value, got {value}"

    missing = get_state("nonexistent")
    assert missing == "", f"expected empty string, got {missing}"

    _DATA_FILE.unlink()
    print("OK — get_state/set_state verified")


if __name__ == "__main__":
    asyncio.run(demo())
