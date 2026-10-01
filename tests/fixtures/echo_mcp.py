"""Tiny stdio MCP server used by tests: one read tool, one write tool."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("echo")


@mcp.tool()
def read_note(topic: str) -> str:
    """Read-only: return a note about a topic."""
    return f"note about {topic}"


@mcp.tool()
def write_note(topic: str, text: str) -> str:
    """Write: pretend to store a note."""
    return f"stored {topic}"


if __name__ == "__main__":
    mcp.run("stdio")
