"""Connects to the domain's MCP server over stdio and converts its tools into
the function-calling schema the LLM expects. Works with any MCP server."""
import sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from sentinel import domain
from sentinel.config import ROOT


class MCPTools:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or domain.current()
        self.stack = AsyncExitStack()
        self.session: ClientSession | None = None
        self.tools: list[dict] = []

    async def __aenter__(self):
        params = StdioServerParameters(command=sys.executable,
                                       args=["-m", self.cfg["mcp_server"]], cwd=str(ROOT))
        read, write = await self.stack.enter_async_context(stdio_client(params))
        self.session = await self.stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        listed = await self.session.list_tools()
        self.tools = [{"type": "function", "function": {
            "name": t.name, "description": t.description or "",
            "parameters": t.inputSchema}} for t in listed.tools]
        return self

    async def __aexit__(self, *exc):
        await self.stack.aclose()

    async def call(self, name: str, args: dict) -> str:
        result = await self.session.call_tool(name, args)
        return "\n".join(getattr(c, "text", "") for c in result.content)
