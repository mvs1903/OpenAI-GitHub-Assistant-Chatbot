"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import requests
import os
from typing import Optional, Dict, List, Any


# Create an MCP server
mcp = FastMCP("Demo")

# GitHub API configuration
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN="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"

# OpenAI API configuration
OPENAI_API_KEY = ""  # Add your OpenAI API key here
OPENAI_API_BASE = "https://api.openai.com/v1"

def get_github_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests"""
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is required for GitHub operations")
    
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MCP-GitHub-Tool"
    }

def get_openai_headers() -> Dict[str, str]:
    """Get headers for OpenAI API requests"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required for OpenAI operations")
    
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }


# GitHub Repository Tools
@mcp.tool()
def get_repository_details(owner: str, repo: str) -> Dict[str, Any]:
    """Get detailed information about a GitHub repository. Requires owner and repo parameters."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def list_user_repositories(username: str, type: str = "all", sort: str = "updated", per_page: int = 30) -> List[Dict[str, Any]]:
    """List repositories for a user. Parameters: username (required), type (all/owner/member), sort (created/updated/pushed/full_name), per_page (max 100)."""
    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    params = {"type": type, "sort": sort, "per_page": per_page}
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def list_repository_branches(owner: str, repo: str, per_page: int = 30) -> List[Dict[str, Any]]:
    """List all branches in a repository. Requires owner and repo parameters."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/branches"
    params = {"per_page": per_page}
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_repository_contents(owner: str, repo: str, path: str = "", ref: str = None) -> List[Dict[str, Any]]:
    """Get contents of a directory or file in a repository. Parameters: owner (required), repo (required), path (optional, defaults to root), ref (optional branch/commit)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    params = {}
    if ref:
        params["ref"] = ref
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_repository_commits(owner: str, repo: str, sha: str = None, path: str = None, per_page: int = 30) -> List[Dict[str, Any]]:
    """Get commit history for a repository. Parameters: owner (required), repo (required), sha (optional branch/commit), path (optional file path), per_page (max 100)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    params = {"per_page": per_page}
    if sha:
        params["sha"] = sha
    if path:
        params["path"] = path
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_repository_issues(owner: str, repo: str, state: str = "open", labels: str = None, sort: str = "created", per_page: int = 30) -> List[Dict[str, Any]]:
    """Get issues for a repository. Parameters: owner (required), repo (required), state (open/closed/all), labels (comma-separated), sort (created/updated/comments)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    params = {"state": state, "sort": sort, "per_page": per_page}
    if labels:
        params["labels"] = labels
    
    try:
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        
        # Filter out pull requests (GitHub API returns both issues and PRs in /issues endpoint)
        all_items = response.json()
        issues_only = [item for item in all_items if 'pull_request' not in item]
        return issues_only
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch issues: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}

@mcp.tool()
def get_repository_pull_requests(owner: str, repo: str, state: str = "open", sort: str = "created", per_page: int = 30) -> List[Dict[str, Any]]:
    """Get pull requests for a repository. Parameters: owner (required), repo (required), state (open/closed/all), sort (created/updated/popularity)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
    params = {"state": state, "sort": sort, "per_page": per_page}
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def search_repositories(query: str, sort: str = "stars", order: str = "desc", per_page: int = 30) -> Dict[str, Any]:
    """Search for repositories on GitHub. Parameters: query (required search terms), sort (stars/forks/updated), order (asc/desc), per_page (max 100)."""
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {"q": query, "sort": sort, "order": order, "per_page": per_page}
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_repository_languages(owner: str, repo: str) -> Dict[str, int]:
    """Get programming languages used in a repository with byte counts. Requires owner and repo parameters."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_repository_releases(owner: str, repo: str, per_page: int = 30) -> List[Dict[str, Any]]:
    """Get releases for a repository. Requires owner and repo parameters."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases"
    params = {"per_page": per_page}
    response = requests.get(url, headers=get_github_headers(), params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_repository_issue(owner: str, repo: str, title: str, body: str = "", labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
    """Create a new issue in a repository. Parameters: owner (required), repo (required), title (required), body (optional), labels (optional list), assignees (optional list)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    data = {"title": title, "body": body}
    if labels:
        data["labels"] = labels
    if assignees:
        data["assignees"] = assignees
    response = requests.post(url, headers=get_github_headers(), json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_authenticated_user() -> Dict[str, Any]:
    """Get information about the authenticated GitHub user."""
    url = f"{GITHUB_API_BASE}/user"
    response = requests.get(url, headers=get_github_headers())
    response.raise_for_status()
    return response.json()


# OpenAI Tools
@mcp.tool()
def openai_chat_completion(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 150, temperature: float = 0.7) -> Dict[str, Any]:
    """Generate text completion using OpenAI's chat models. Parameters: prompt (required), model (gpt-3.5-turbo/gpt-4/gpt-4-turbo), max_tokens, temperature."""
    url = f"{OPENAI_API_BASE}/chat/completions"
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=get_openai_headers(), json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to generate completion: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}

@mcp.tool()
def openai_text_completion(prompt: str, model: str = "gpt-3.5-turbo-instruct", max_tokens: int = 150, temperature: float = 0.7) -> Dict[str, Any]:
    """Generate text completion using OpenAI's completion models. Parameters: prompt (required), model (gpt-3.5-turbo-instruct/text-davinci-003), max_tokens, temperature."""
    url = f"{OPENAI_API_BASE}/completions"
    
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(url, headers=get_openai_headers(), json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to generate completion: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}

@mcp.tool()
def openai_image_generation(prompt: str, size: str = "1024x1024", quality: str = "standard", n: int = 1) -> Dict[str, Any]:
    """Generate images using OpenAI's DALL-E. Parameters: prompt (required), size (256x256/512x512/1024x1024), quality (standard/hd), n (number of images 1-10)."""
    url = f"{OPENAI_API_BASE}/images/generations"
    
    data = {
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": n
    }
    
    try:
        response = requests.post(url, headers=get_openai_headers(), json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to generate image: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}

@mcp.tool()
def openai_list_models() -> Dict[str, Any]:
    """List all available OpenAI models."""
    url = f"{OPENAI_API_BASE}/models"
    
    try:
        response = requests.get(url, headers=get_openai_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to list models: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}

@mcp.tool()
def openai_embeddings(text: str, model: str = "text-embedding-ada-002") -> Dict[str, Any]:
    """Generate embeddings for text using OpenAI's embedding models. Parameters: text (required), model (text-embedding-ada-002/text-embedding-3-small/text-embedding-3-large)."""
    url = f"{OPENAI_API_BASE}/embeddings"
    
    data = {
        "input": text,
        "model": model
    }
    
    try:
        response = requests.post(url, headers=get_openai_headers(), json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to generate embeddings: {str(e)}", "status_code": getattr(e.response, 'status_code', None)}


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def get_pokemon_details(pokemon_name: str) -> dict:
    """Gets the details of a pokemon"""
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

@mcp.tool()
def get_ann_date(a: int, b: int) -> str:
    """gets your anniversay date"""
    return "16/07/2022"

# API Tools for Sprinto endpoints
@mcp.tool()
def get_users() -> dict:
    """Retrieve all users from the Sprinto API. Returns a list of user objects with id, name, email, and avatar fields."""
    response = requests.get("https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/users")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_user(user_id: str) -> dict:
    """Retrieve a specific user by their ID from the Sprinto API. Requires user_id parameter. Returns user object with id, name, email, and avatar fields."""
    response = requests.get(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/users/{user_id}")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_user(name: str, email: str, avatar: str = "") -> dict:
    """Create a new user in the Sprinto API. Requires name and email parameters. Avatar is optional. Returns the created user object with assigned ID."""
    data = {"name": name, "email": email, "avatar": avatar}
    response = requests.post("https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/users", json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_user(user_id: str, name: str = None, email: str = None, avatar: str = None) -> dict:
    """Update an existing user in the Sprinto API. Requires user_id. All other parameters (name, email, avatar) are optional - only provide the fields you want to update. Returns the updated user object."""
    data = {}
    if name is not None:
        data["name"] = name
    if email is not None:
        data["email"] = email
    if avatar is not None:
        data["avatar"] = avatar
    
    response = requests.put(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/users/{user_id}", json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_user(user_id: str) -> dict:
    """Delete a user from the Sprinto API. Requires user_id parameter. Returns success confirmation message."""
    response = requests.delete(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/users/{user_id}")
    response.raise_for_status()
    return {"success": True, "message": f"User {user_id} deleted successfully"}

@mcp.tool()
def get_userfiledata() -> dict:
    """Retrieve all user file data records from the Sprinto API. Returns a list of file data objects with id, user_id, file_name, file_type, file_size, and file_url fields."""
    response = requests.get("https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/userfiledata")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_userfiledata_by_id(file_id: str) -> dict:
    """Retrieve specific user file data by file ID from the Sprinto API. Requires file_id parameter. Returns file data object with id, user_id, file_name, file_type, file_size, and file_url fields."""
    response = requests.get(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/userfiledata/{file_id}")
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_userfiledata(user_id: str, file_name: str, file_type: str, file_size: int = 0, file_url: str = "") -> dict:
    """Create new user file data record in the Sprinto API. Requires user_id, file_name, and file_type parameters. file_size and file_url are optional. Returns the created file data object with assigned ID."""
    data = {
        "user_id": user_id,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "file_url": file_url
    }
    response = requests.post("https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/userfiledata", json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_userfiledata(file_id: str, user_id: str = None, file_name: str = None, file_type: str = None, file_size: int = None, file_url: str = None) -> dict:
    """Update existing user file data record in the Sprinto API. Requires file_id. All other parameters (user_id, file_name, file_type, file_size, file_url) are optional - only provide the fields you want to update. Returns the updated file data object."""
    data = {}
    if user_id is not None:
        data["user_id"] = user_id
    if file_name is not None:
        data["file_name"] = file_name
    if file_type is not None:
        data["file_type"] = file_type
    if file_size is not None:
        data["file_size"] = file_size
    if file_url is not None:
        data["file_url"] = file_url
    
    response = requests.put(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/userfiledata/{file_id}", json=data)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_userfiledata(file_id: str) -> dict:
    """Delete user file data record from the Sprinto API. Requires file_id parameter. Returns success confirmation message."""
    response = requests.delete(f"https://68c305bbf9928dbf33f07ea5.mockapi.io/sprinto/userfiledata/{file_id}")
    response.raise_for_status()
    return {"success": True, "message": f"User file data {file_id} deleted successfully"}

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

if __name__ == "__main__":
    mcp.run(transport="stdio")