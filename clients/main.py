import os
import asyncio
import json
from typing import Optional, Any, Dict, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: Dict[str, Any]) -> None:
        self.name: str = name
        self.config: Dict[str, Any] = config
        self.stdio_transport: Any = None
        self.session: Optional[ClientSession] = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection."""
        command = self.config["command"]

        server_params = StdioServerParameters(
            command=command, args=self.config["args"], env=self.config.get("env")
        )

        try:
            self.stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = self.stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            print(
                f"\nConnected to server {self.name} with tools:",
                [tool.name for tool in tools],
            )

        except Exception as e:
            print(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        try:
            await self.exit_stack.aclose()
            self.session = None
            self.stdio_transport = None
        except Exception as e:
            print(f"Error during cleanup of server {self.name}: {e}")


class MCPClient:
    def __init__(
        self,
        output_dir: str,
        model: str,
        max_tokens: int,
        max_iterations: int,
        system_prompt_path: str,
    ):
        # Initialize session and client objects
        self.servers: Dict[str, Server] = {}
        # default to os.getenv("ANTHROPIC_API_KEY")
        self.anthropic = Anthropic()

        # Configuration parameters
        self.model = model
        self.max_tokens = max_tokens
        self.max_iterations = max_iterations

        # Create output directory
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Created output directory: {self.output_dir}")

        # Load and modify system prompt
        with open(system_prompt_path, "r") as file:
            self.system_prompt = file.read()

        # Append directory instruction to system prompt
        self.system_prompt += f"\n\nAll created files you create should be saved under the directory: {self.output_dir}. The directory has already been created for you."

    def load_server_config(self, config_path: str) -> Dict[str, Any]:
        """Load server configuration from JSON file."""
        with open(config_path, "r") as f:
            return json.load(f)

    async def initialize_servers(self, config_path: str) -> None:
        """Initialize all servers from the config file."""
        config = self.load_server_config(config_path)

        for name, server_config in config["mcpServers"].items():
            server = Server(name, server_config)
            await server.initialize()
            self.servers[name] = server

    async def loop(self, query: str) -> List[Dict[str, Any]]:
        """Process a query using Claude and available tools"""
        messages = [{"role": "user", "content": query}]

        # Collect all available tools from all servers
        available_tools = []
        for server_name, server in self.servers.items():
            if server.session:
                response = await server.session.list_tools()
                for tool in response.tools:
                    available_tools.append(
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema,
                        }
                    )

        # Main agent loop (with iteration limit to prevent runaway API costs)
        iterations = 0
        while True and iterations < self.max_iterations:
            iterations += 1
            # Set up optional thinking parameter (for Claude 3.7 Sonnet)
            thinking = None

            # Call the Claude API
            response = self.anthropic.messages.create(
                model=self.model,
                system=self.system_prompt,
                max_tokens=self.max_tokens,
                messages=messages,
                tools=available_tools,
            )

            # Add Claude's response to the conversation history
            response_content = response.content
            messages.append({"role": "assistant", "content": response_content})

            print(f"Claude's response: {response_content}")

            # Check if Claude used any tools
            tool_results = []
            for block in response_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # Find the server that has this tool
                    tool_result = None
                    for server_name, server in self.servers.items():
                        if server.session:
                            response = await server.session.list_tools()
                            if any(tool.name == tool_name for tool in response.tools):
                                # Execute tool call
                                result = await server.session.call_tool(
                                    tool_name, tool_args
                                )
                                tool_result = result
                                break

                    if tool_result:
                        # Format the result for Claude
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": tool_result.content,
                            }
                        )
                    else:
                        # If no server has the tool, return an error
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error: Tool {tool_name} not found in any server",
                            }
                        )

            # If no tools were used, Claude is done - return the final messages
            if not tool_results:
                return messages

            # Add tool results to messages for the next iteration with Claude
            messages.append({"role": "user", "content": tool_results})

    async def chat(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.loop(query)
                print("\n" + str(response))

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        for server_name, server in self.servers.items():
            await server.cleanup()


async def run_client(
    server_config_path: str,
    output_dir: str,
    model: str,
    max_tokens: int,
    max_iterations: int,
    system_prompt_path: str,
):
    """Run the MCP client with specified parameters"""
    client = MCPClient(
        output_dir=output_dir,
        model=model,
        max_tokens=max_tokens,
        max_iterations=max_iterations,
        system_prompt_path=system_prompt_path,
    )
    try:
        # Initialize servers from config file
        await client.initialize_servers(server_config_path)
        await client.chat()
    finally:
        await client.cleanup()


async def main():
    # Default entry point when running the script directly
    await run_client()


if __name__ == "__main__":
    asyncio.run(main())
