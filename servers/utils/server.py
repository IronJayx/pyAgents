from mcp.server.fastmcp import FastMCP
import os
import requests

mcp = FastMCP("utils")


@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read.

    Returns:
        The contents of the file as a string.
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write to.
        content: Content to write to the file.
        append: If True, append to the file; otherwise, overwrite.

    Returns:
        Success message or error message.
    """
    mode = "a" if append else "w"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, mode) as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


# @mcp.tool()
# def create_venv(venv_path: str = ".venv") -> str:
#     """
#     Create a Python virtual environment.

#     Args:
#         venv_path: Path where the virtual environment should be created.

#     Returns:
#         Success message or error message.
#     """
#     try:
#         venv.create(venv_path, with_pip=True)
#         return f"Virtual environment created at {venv_path}"
#     except Exception as e:
#         return f"Error creating virtual environment: {str(e)}"


# @mcp.tool()
# def get_venv_activate_command(venv_path: str = ".venv") -> str:
#     """
#     Get the command to activate a virtual environment.

#     Args:
#         venv_path: Path to the virtual environment.

#     Returns:
#         Command to activate the virtual environment.
#     """
#     if sys.platform == "win32":
#         return f"{venv_path}\\Scripts\\activate"
#     else:
#         return f"source {venv_path}/bin/activate"


# @mcp.tool()
# def pip_install(packages: list, venv_path: str = None, upgrade: bool = False) -> str:
#     """
#     Install Python packages using pip.

#     Args:
#         packages: List of packages to install.
#         venv_path: Optional path to a virtual environment.
#         upgrade: If True, upgrade the packages if already installed.

#     Returns:
#         Output of the pip install command.
#     """
#     try:
#         if venv_path:
#             # Use the pip from the specified virtual environment
#             if sys.platform == "win32":
#                 pip_path = os.path.join(venv_path, "Scripts", "pip")
#             else:
#                 pip_path = os.path.join(venv_path, "bin", "pip")
#         else:
#             # Use the current Python's pip
#             pip_path = "pip"

#         cmd = [pip_path, "install"]
#         if upgrade:
#             cmd.append("--upgrade")
#         cmd.extend(packages)

#         result = subprocess.run(cmd, capture_output=True, text=True)
#         if result.returncode != 0:
#             return f"Error: {result.stderr}"
#         return result.stdout
#     except Exception as e:
#         return f"Error installing packages: {str(e)}"


@mcp.tool()
def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    data: dict = None,
    headers: dict = None,
    timeout: int = 30,
) -> str:
    """
    Make an HTTP request using the requests library.

    Args:
        url: URL to call.
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        params: Optional query parameters.
        data: Optional data for the request body.
        headers: Optional headers for the request.
        timeout: Request timeout in seconds.

    Returns:
        Response content or error message.
    """
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        # Try to return JSON if possible
        try:
            return response.json()
        except:
            return response.text
    except Exception as e:
        return f"Error making request: {str(e)}"


# @mcp.tool()
# def run_command(
#     command: str, cwd: str = None, env: dict = None, capture_output: bool = True
# ) -> str:
#     """
#     Run a shell command.

#     Args:
#         command: Command to run.
#         cwd: Current working directory for the command.
#         env: Environment variables for the command.
#         capture_output: Whether to capture and return command output.

#     Returns:
#         Command output or error message.
#     """
#     try:
#         # Prepare environment variables
#         environment = os.environ.copy()
#         if env:
#             environment.update(env)

#         if capture_output:
#             result = subprocess.run(
#                 command,
#                 shell=True,
#                 cwd=cwd,
#                 env=environment,
#                 capture_output=True,
#                 text=True,
#             )
#             if result.returncode != 0:
#                 return f"Command failed with exit code {result.returncode}.\nOutput: {result.stdout}\nError: {result.stderr}"
#             return result.stdout
#         else:
#             # Run without capturing output (output goes directly to terminal)
#             subprocess.run(command, shell=True, cwd=cwd, env=environment)
#             return "Command executed (output not captured)"
#     except Exception as e:
#         return f"Error executing command: {str(e)}"


if __name__ == "__main__":
    mcp.run()
