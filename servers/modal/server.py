from mcp.server.fastmcp import FastMCP


mcp = FastMCP("modal")


import subprocess


@mcp.tool()
async def deploy(
    app_file_path: str,
    name: str = None,
    env: str = None,
) -> dict:
    """
    Deploy a Modal application and persist it to the cloud.

    Args:
        app_file_path: Absolute path to a Python file with an app to deploy.
        name: Optional name of the deployment.
        env: Optional environment to interact with.
    """

    command = ["modal", "deploy", app_file_path]
    if name:
        command.extend(["--name", name])
    if env:
        command.extend(["-e", env])

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(command),
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "command": " ".join(command),
        }


@mcp.tool()
async def create_secret(
    secret_name: str, keyvalues: dict, env: str = None, force: bool = False
) -> dict:
    """
    Create a new secret in Modal. Use this if the user passes secrets, keys that needs to be stored like API keys, passwords, and other secrets that the Modal app needs.

    Arguments:
        secret_name: Name of the secret to create. [required]
        keyvalues: Dictionary of key-value pairs to store in the secret. [required]

    Options:
        -e, --env TEXT: Environment to interact with. Default is 'default'.
        --force: Overwrite the secret if it already exists.
    """

    command = ["modal", "secret", "create", secret_name]

    for key, value in keyvalues.items():
        command.append(f"{key}={value}")

    if env:
        command.extend(["-e", env])

    if force:
        command.append("--force")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(command),
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "command": " ".join(command),
        }


# @mcp.tool()
# async def serve(
#     app_ref: str,
#     env: str = None,
#     timeout: float = 30.0,
# ) -> dict:
#     """
#     Serve a Modal application and enable hot-reloading of code. Use this for development and iteration.

#     Arguments:
#         app_ref: Path to a Python file with an app. [required]

#     Options:
#         --timeout FLOAT: Timeout for the operation. Default is 30.0 seconds.
#         -e, --env TEXT: Environment to interact with. Default is 'default'.
#     """

#     command = ["modal", "serve", app_ref]

#     if env:
#         command.extend(["-e", env])

#     if timeout:
#         command.extend(["--timeout", str(timeout)])

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def set_token(
#     token_id: str = None,
#     token_secret: str = None,
#     profile: str = None,
#     activate: bool = True,
#     verify: bool = True,
# ) -> dict:
#     """
#     Set account credentials for connecting to Modal. Use this to connect to modal with user modal credentials.

#     Options:
#         token_id: Account token ID.
#         token_secret: Account token secret.
#         profile: Modal profile to set credentials for. Uses workspace name if unspecified.
#         activate: Activate the profile containing this token after creation. Default is True.
#         verify: Make a test request to verify the new credentials. Default is True.
#     """
#     command = ["modal", "token", "set"]

#     if token_id:
#         command.extend(["--token-id", token_id])

#     if token_secret:
#         command.extend(["--token-secret", token_secret])

#     if profile:
#         command.extend(["--profile", profile])

#     if not activate:
#         command.append("--no-activate")

#     if not verify:
#         command.append("--no-verify")

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def list_environments() -> dict:
#     """
#     List all environments in the current workspace.
#     """
#     command = ["modal", "environment", "list"]

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def create_environment(name: str) -> dict:
#     """
#     Create a new environment in the current workspace.

#     Arguments:
#         name: Name of the new environment. Must be unique and case-sensitive.
#     """
#     command = ["modal", "environment", "create", name]

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def activate_profile(profile: str) -> dict:
#     """
#     Change the active Modal profile. Use this to switch between workspaces.

#     Arguments:
#         profile: Modal profile to activate.
#     """
#     command = ["modal", "profile", "activate", profile]

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def current_profile() -> dict:
#     """
#     Print the currently active Modal profile.
#     """
#     command = ["modal", "profile", "current"]

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


# @mcp.tool()
# async def list_profiles(json_output: bool = False) -> dict:
#     """
#     Show all Modal profiles and highlight the active one.

#     Options:
#         json_output: Whether to output as JSON.
#     """
#     command = ["modal", "profile", "list"]

#     if json_output:
#         command.append("--json")

#     try:
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "command": " ".join(command),
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "error": str(e),
#             "stdout": e.stdout,
#             "stderr": e.stderr,
#             "command": " ".join(command),
#         }


if __name__ == "__main__":
    mcp.run()
