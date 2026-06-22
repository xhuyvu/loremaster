"""Entry point for the Campaign State MCP server."""

from mcp_servers.campaign_state_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
