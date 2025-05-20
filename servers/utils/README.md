# MCP Python Development Tools

This module provides MCP tools for common Python development tasks.

## Available Tools

### File Operations
- `read_file(file_path)`: Read contents of a file
- `write_file(file_path, content, append=False)`: Write or append content to a file

### Virtual Environment Management
- `create_venv(venv_path=".venv")`: Create a Python virtual environment
- `get_venv_activate_command(venv_path=".venv")`: Get the command to activate a virtual environment

### Package Management
- `pip_install(packages, venv_path=None, upgrade=False)`: Install Python packages using pip

### HTTP Requests
- `make_request(url, method="GET", params=None, data=None, headers=None, timeout=30)`: Make HTTP requests

### Shell Command Execution
- `run_command(command, cwd=None, env=None, capture_output=True)`: Run shell commands

## Usage Examples

```python
# Read a file
content = read_file("path/to/file.txt")

# Write to a file
write_file("path/to/new_file.txt", "Hello, world!")

# Create and activate a virtual environment
create_venv("my_venv")
activate_cmd = get_venv_activate_command("my_venv")
# Run the activate_cmd in your terminal

# Install packages
pip_install(["flask", "requests"], venv_path="my_venv")

# Make an HTTP request
response = make_request("https://api.example.com/data", 
                       method="POST", 
                       data={"key": "value"})

# Run a shell command
output = run_command("python -V")
```

## Running the module

To run this module directly:

```bash
python -m mcp.utils.python_dev
``` 