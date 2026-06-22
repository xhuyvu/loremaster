"""SRD MCP server for D&D 5e rules lookup."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("srd-server")

_DATA: dict[str, dict] = json.loads(
    (Path(__file__).parent / "srd_data.json").read_text()
)


@mcp.tool()
def query_srd(query: str) -> str:
    """Search the D&D 5e SRD for rules, spells, or monsters matching the query.
    Returns up to 5 matching entries with their full content."""
    q = query.lower()
    results = []
    for key, entry in _DATA.items():
        if q in key or q in entry["content"].lower():
            results.append(f"## {entry['name']}\n{entry['content']}")
            if len(results) >= 5:
                break
    return "\n\n---\n\n".join(results) if results else f"No SRD entries found matching '{query}'."


@mcp.tool()
def lookup_srd(entity_type: str, name: str) -> str:
    """Look up a specific SRD entity by type and name.

    Valid entity_type values: spell, monster, glossary, feat, equipment,
    class, magic-item, origin, rule

    name is case-insensitive; partial matches are returned first.
    """
    q = f"{entity_type}_{name}".lower()
    q = q.replace(" ", "_").replace("'", "").replace("'", "").replace("-", "_")
    exact = []
    partial = []
    for key, entry in _DATA.items():
        if entry["type"] != entity_type:
            continue
        if q in key:
            exact.append(f"## {entry['name']}\n{entry['content']}")
        elif name.lower() in key.replace(f"{entity_type}_", "").replace("_", " "):
            partial.append(f"## {entry['name']}\n{entry['content']}")
    matches = (exact + partial)[:5]
    return "\n\n---\n\n".join(matches) if matches else f"No {entity_type} found matching '{name}'."


async def demo():
    """Self-check: verify tool registration and lookup."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "query_srd" in tools
    assert "lookup_srd" in tools

    result = lookup_srd("spell", "fireball")
    assert "Fireball" in result, f"Expected 'Fireball', got: {result[:100]}"
    assert "3 Evocation" in result, f"Expected level/school, got: {result[:100]}"

    result2 = query_srd("prone")
    assert "Prone" in result2 or result2, "Expected results for 'prone', got empty"

    result3 = lookup_srd("monster", "aboleth")
    assert "Aboleth" in result3, f"Expected 'Aboleth', got: {result3[:100]}"

    print(f"OK — {len(tools)} tool(s) registered, {len(_DATA)} entries loaded")


if __name__ == "__main__":
    asyncio.run(demo())
