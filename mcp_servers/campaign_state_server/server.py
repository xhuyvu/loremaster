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


@mcp.tool()
def get_combat_state() -> str:
    """Return the current combat state as JSON, or empty dict if no active combat."""
    data = _load()
    return json.dumps(data.get("combat", {}))


@mcp.tool()
def apply_damage(name: str, amount: int) -> str:
    """Apply damage (positive amount) or healing (negative amount) to a combatant.
    Returns a summary like '{name} takes X damage (HP: Y/Z)' or '{name} heals X (HP: Y/Z)'.
    HP is floored at 0 and capped at max_hp."""
    data = _load()
    combat = data.get("combat", {})
    combatants = combat.get("combatants", [])
    for c in combatants:
        if c["name"] == name:
            old_hp = c["hp"]
            new_hp = old_hp - amount
            new_hp = max(0, min(new_hp, c["max_hp"]))
            c["hp"] = new_hp
            data["combat"] = combat
            _save(data)
            if amount > 0:
                return f"{name} takes {amount} damage (HP: {new_hp}/{c['max_hp']})"
            else:
                return f"{name} heals {-amount} (HP: {new_hp}/{c['max_hp']})"
    return f"Combatant '{name}' not found."


@mcp.tool()
def set_combat_state(value: str) -> str:
    """Replace the entire combat state from a JSON string.
    Expected shape: {"round": 1, "current_turn_index": 0, "combatants": [...]}
    Returns 'Combat state updated.'"""
    data = _load()
    data["combat"] = json.loads(value)
    _save(data)
    return "Combat state updated."


@mcp.tool()
def end_combat() -> str:
    """End the active combat and clear combat state."""
    data = _load()
    data.pop("combat", None)
    _save(data)
    return "Combat ended."


async def demo():
    """Self-check: verify tool registration and basic KV operations."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "get_state" in tools
    assert "set_state" in tools
    assert "get_combat_state" in tools
    assert "apply_damage" in tools
    assert "set_combat_state" in tools
    assert "end_combat" in tools

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

    combat = json.loads(get_combat_state())
    assert combat == {}, f"expected empty dict, got {combat}"

    result = apply_damage("Nobody", 5)
    assert "not found" in result

    set_combat_state(json.dumps({
        "round": 1,
        "current_turn_index": 0,
        "combatants": [
            {"name": "Goblin", "initiative": 15, "hp": 7, "max_hp": 7, "ac": 15, "conditions": [], "is_player": False},
            {"name": "Alice", "initiative": 12, "hp": 20, "max_hp": 20, "ac": 14, "conditions": [], "is_player": True},
        ],
    }))
    combat = json.loads(get_combat_state())
    assert combat["round"] == 1
    assert len(combat["combatants"]) == 2

    result = apply_damage("Goblin", 5)
    assert "takes 5 damage" in result
    assert "(HP: 2/7)" in result

    result = apply_damage("Goblin", 10)
    assert "(HP: 0/7)" in result

    result = apply_damage("Alice", -5)
    assert "heals" in result
    assert "(HP: 20/20)" in result  # ponytail: capped at max_hp

    end_combat()
    combat = json.loads(get_combat_state())
    assert combat == {}, f"expected empty dict after end_combat, got {combat}"

    _DATA_FILE.unlink()
    print("OK — all tools verified")


if __name__ == "__main__":
    asyncio.run(demo())
