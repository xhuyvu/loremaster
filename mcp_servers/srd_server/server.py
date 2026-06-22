"""SRD MCP server for D&D 5e rules lookup."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("srd-server")


@mcp.tool()
def query_srd(query: str) -> str:
    """Search the D&D 5e SRD for rules, spells, or monsters matching the query."""
    return f"SRD lookup for '{query}': (stub)"


import asyncio


async def demo():
    """Self-check: verify tool registration."""
    tools = [t.name for t in await mcp.list_tools()]
    assert "query_srd" in tools, f"query_srd not found in {tools}"
    print(f"OK — {len(tools)} tool(s) registered: {tools}")


if __name__ == "__main__":
    asyncio.run(demo())
