"""Entry point for the SRD MCP server."""

from mcp_servers.srd_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
