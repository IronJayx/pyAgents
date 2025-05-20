import asyncio
from clients.main import run_client
from dotenv import load_dotenv

load_dotenv()


async def modalEngine():
    await run_client(
        server_config_path="agents/modal_engine/server_config.json",
        model="claude-3-7-sonnet-20250219",
        max_tokens=4096,
        max_iterations=10,
        output_dir="./agents/modal_engine/output",
        system_prompt_path="./agents/modal_engine/system_prompt.md",
    )


async def helloWorld():
    await run_client(
        server_config_path="agents/hello_world/server_config.json",
        model="claude-3-7-sonnet-20250219",
        max_tokens=4096,
        max_iterations=10,
        output_dir="./agents/hello_world/example_output",
        system_prompt_path="./agents/hello_world/system_prompt.md",
    )


# Run one of the examples
if __name__ == "__main__":
    asyncio.run(helloWorld())
