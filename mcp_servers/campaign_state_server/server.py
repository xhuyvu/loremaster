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


@mcp.tool()
def init_campaign(name: str, setting: str, starting_location: str) -> str:
    """Initialize a new campaign with name, setting, and starting location."""
    data = _load()
    data["campaign"] = {
        "name": name,
        "setting": setting,
        "starting_location": starting_location,
    }
    _save(data)
    return f"Campaign '{name}' initialized."


@mcp.tool()
def get_campaign() -> str:
    """Return the current campaign as JSON, or empty string if not set."""
    data = _load()
    return json.dumps(data.get("campaign", ""))


@mcp.tool()
def add_pc(name: str, race: str, char_class: str, level: int = 1) -> str:
    """Add a player character to the party."""
    data = _load()
    party = data.get("party", [])
    party.append({"name": name, "race": race, "class": char_class, "level": level})
    data["party"] = party
    _save(data)
    return f"{name} ({race} {char_class}, lv{level}) added to party."


@mcp.tool()
def get_party() -> str:
    """Return the party as JSON, or empty string if no party."""
    data = _load()
    return json.dumps(data.get("party", []))




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

    assert "initialized" in init_campaign("Test", "A test world", "Town")
    campaign = json.loads(get_campaign())
    assert campaign["name"] == "Test"

    assert "added" in add_pc("Alice", "Elf", "Wizard", 2)
    party = json.loads(get_party())
    assert len(party) == 1
    assert party[0]["name"] == "Alice"

    _DATA_FILE.unlink()
    print("OK — all tools verified")


if __name__ == "__main__":
    asyncio.run(demo())
