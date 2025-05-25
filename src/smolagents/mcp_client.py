from __future__ import annotations
from types import TracebackType
from typing import TYPE_CHECKING, Any
from smolagents.tools import Tool
__all__ = ["MCPClient"]
if TYPE_CHECKING:
    from mcpadapt.core import StdioServerParameters
class MCPClient:
    """Manages the connection to an MCP server and make its tools available to SmolAgents.
    Note: tools can only be accessed after the connection has been started with the
        `connect()` method, done during the init. If you don't use the context manager
        we strongly encourage to use "try ... finally" to ensure the connection is cleaned up.
    Args:
        server_parameters (StdioServerParameters | dict[str, Any] | list[StdioServerParameters | dict[str, Any]]):
            MCP server parameters (stdio or sse). Can be a list if you want to connect multiple MCPs at once.
    Example:
        ```python
        with MCPClient(...) as tools:
        with MCPClient({"url": "http://localhost:8000/sse"}) as tools:
        try:
            mcp_client = MCPClient(...)
            tools = mcp_client.get_tools()
        finally:
            mcp_client.stop()
        ```
    """
    def __init__(self, server_parameters: "StdioServerParameters" | dict[str, Any] | list["StdioServerParameters" | dict[str, Any]],):
        try:
            from mcpadapt.core import MCPAdapt
            from mcpadapt.smolagents_adapter import SmolAgentsAdapter
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Please install 'mcp' extra to use MCPClient: `pip install 'smolagents[mcp]'`")
        self._adapter = MCPAdapt(server_parameters, SmolAgentsAdapter())
        self._tools: list[Tool] | None = None
        self.connect()
    def connect(self):
        """Connect to the MCP server and initialize the tools."""
        self._tools: list[Tool] = self._adapter.__enter__()
    def disconnect(self, exc_type: type[BaseException] | None = None, exc_value: BaseException | None = None, exc_traceback: TracebackType | None = None,):
        """Disconnect from the MCP server"""
        self._adapter.__exit__(exc_type, exc_value, exc_traceback)
    def get_tools(self) -> list[Tool]:
        """The SmolAgents tools available from the MCP server.
        Note: for now, this always returns the tools available at the creation of the session,
        but it will in a future release return also new tools available from the MCP server if
        any at call time.
        Raises:
            ValueError: If the MCP server tools is None (usually assuming the server is not started).
        Returns:
            list[Tool]: The SmolAgents tools available from the MCP server.
        """
        if self._tools is None:
            raise ValueError("Couldn't retrieve tools from MCP server, run `mcp_client.connect()` first before accessing `tools`")
        return self._tools
    def __enter__(self) -> list[Tool]:
        """Connect to the MCP server and return the tools directly. Note that because of the `.connect` in the init, the mcp_client is already connected at this point."""
        return self._tools
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_traceback: TracebackType | None,):
        """Disconnect from the MCP server."""
        self.disconnect(exc_type, exc_value, exc_traceback)
