"""Entry point for the Dice MCP server."""

from mcp_servers.dice_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
