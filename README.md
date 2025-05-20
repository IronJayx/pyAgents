# MCP Client with Config-based Server Loading

This project demonstrates how to use the Model-Controller-Presenter (MCP) pattern with a configurable server loading approach.

## Setup

1. Ensure you have Python installed.
2. Install dependencies using install script:
    ```
   ./install.sh
   ```
3. Create a `.env` file in the client directory with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
4. Check everything works using the hello_world agent.
   ```
   source .venv/bin/activate
   python main.py
   ```

Ask the agent to write a simple file and check the response.
It should output a file at ./agents/hello_world/example_output

## Create your own agents

Create config files
```
mkdir agents/<your-agent>
touch agents/<your-agent>/server_config.json
touch agents/<your-agent>/system_prompt.md
```

Specify agents behavior in system_prompt.md and list mcp servers in server_config.json

Then you can just replace the config paths in main.py with your own agent's.

```
python main.py
```

This will start the interactive chat client that connects to all configured servers.

## Adding New Servers

1. Create your server implementation under the `servers/` directory (see examples in `servers/modal` and `servers/utils`).
2. Add an entry to your agent's `server_config.json` with the appropriate configuration. 