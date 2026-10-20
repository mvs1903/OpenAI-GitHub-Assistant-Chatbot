"""
OpenAI LLM client with comprehensive GitHub tools for PR, issues, and repository management.
"""

from openai import OpenAI
from github import Github, GithubException
from typing import Optional, Dict, List, Any, Union
import os
import json


class OpenAIGitHubClient:
    """
    A client that combines OpenAI's GPT models with GitHub API functionality.
    Provides comprehensive tools for managing repositories, pull requests, and issues.
    """
    
    def __init__(self, openai_api_key: str = None, github_token: str = None):
        """
        Initialize the OpenAI GitHub client.
        
        Args:
            openai_api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            github_token: GitHub personal access token (uses GITHUB_TOKEN env var if not provided)
        """
        # Configure OpenAI
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass openai_api_key parameter.")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Configure GitHub
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass github_token parameter.")
        
        self.github = Github(self.github_token)
        
        # Define available tools for OpenAI function calling
        self.tools = [
            # Repository tools
            {
                "type": "function",
                "function": {
                    "name": "create_repository",
                    "description": "Create a new GitHub repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Repository name"},
                            "description": {"type": "string", "description": "Repository description"},
                            "private": {"type": "boolean", "description": "Whether repository should be private"},
                            "auto_init": {"type": "boolean", "description": "Initialize with README"}
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_repository",
                    "description": "Get repository information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_repositories",
                    "description": "List repositories for authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "description": "Repository type: all, owner, member"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, pushed, full_name"},
                            "per_page": {"type": "integer", "description": "Number of results per page (max 100)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_repository",
                    "description": "Update repository settings",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "name": {"type": "string", "description": "New repository name"},
                            "description": {"type": "string", "description": "Repository description"},
                            "private": {"type": "boolean", "description": "Whether repository should be private"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            # Pull Request tools
            {
                "type": "function",
                "function": {
                    "name": "create_pull_request",
                    "description": "Create a new pull request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "title": {"type": "string", "description": "Pull request title"},
                            "head": {"type": "string", "description": "Head branch"},
                            "base": {"type": "string", "description": "Base branch"},
                            "body": {"type": "string", "description": "Pull request description"},
                            "draft": {"type": "boolean", "description": "Create as draft PR"}
                        },
                        "required": ["owner", "repo", "title", "head", "base"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_pull_requests",
                    "description": "List pull requests in a repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "state": {"type": "string", "description": "PR state: open, closed, all"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, popularity"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pull_request",
                    "description": "Get specific pull request details with files changed, comments, and review status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Pull request number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_pull_request",
                    "description": "Analyze a pull request to understand why it was created, what problem it solves, and its impact",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Pull request number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "merge_pull_request",
                    "description": "Merge a pull request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Pull request number"},
                            "commit_message": {"type": "string", "description": "Merge commit message"},
                            "merge_method": {"type": "string", "description": "Merge method: merge, squash, rebase"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "close_pull_request",
                    "description": "Close a pull request without merging",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Pull request number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            # Organization tools
            {
                "type": "function",
                "function": {
                    "name": "get_organization",
                    "description": "Get organization information and details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_organization_repositories",
                    "description": "List repositories in an organization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "type": {"type": "string", "description": "Repository type: all, public, private, forks, sources, member"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, pushed, full_name"},
                            "per_page": {"type": "integer", "description": "Number of results per page (max 100)"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_organization_members",
                    "description": "List members of an organization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "role": {"type": "string", "description": "Filter by role: all, admin, member"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_organization_teams",
                    "description": "List teams in an organization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_organization_team",
                    "description": "Get specific team information and members",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "team_slug": {"type": "string", "description": "Team slug/name"}
                        },
                        "required": ["org", "team_slug"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_organization_health",
                    "description": "Analyze organization-wide health, activity patterns, and development trends",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_organization_issues",
                    "description": "Get issues across all organization repositories",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "state": {"type": "string", "description": "Issue state: open, closed, all"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "Filter by labels"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, comments"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["org"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_organization_pull_requests",
                    "description": "Get pull requests across all organization repositories",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "org": {"type": "string", "description": "Organization name"},
                            "state": {"type": "string", "description": "PR state: open, closed, all"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, popularity"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["org"]
                    }
                }
            },
            # Issue tools
            {
                "type": "function",
                "function": {
                    "name": "create_issue",
                    "description": "Create a new issue",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "title": {"type": "string", "description": "Issue title"},
                            "body": {"type": "string", "description": "Issue description"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "Issue labels"},
                            "assignees": {"type": "array", "items": {"type": "string"}, "description": "Issue assignees"}
                        },
                        "required": ["owner", "repo", "title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_issues",
                    "description": "List issues in a repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "state": {"type": "string", "description": "Issue state: open, closed, all"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "Filter by labels"},
                            "sort": {"type": "string", "description": "Sort by: created, updated, comments"},
                            "per_page": {"type": "integer", "description": "Number of results per page"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_issue",
                    "description": "Get specific issue details with comments and timeline",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Issue number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_issue",
                    "description": "Analyze an issue to understand the problem, root cause, priority, and suggested solutions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Issue number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_repository_health",
                    "description": "Analyze repository health, activity patterns, and development trends",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"}
                        },
                        "required": ["owner", "repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_issue",
                    "description": "Update an existing issue",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Issue number"},
                            "title": {"type": "string", "description": "Issue title"},
                            "body": {"type": "string", "description": "Issue description"},
                            "state": {"type": "string", "description": "Issue state: open, closed"},
                            "labels": {"type": "array", "items": {"type": "string"}, "description": "Issue labels"},
                            "assignees": {"type": "array", "items": {"type": "string"}, "description": "Issue assignees"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "close_issue",
                    "description": "Close an issue",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string", "description": "Repository owner"},
                            "repo": {"type": "string", "description": "Repository name"},
                            "number": {"type": "integer", "description": "Issue number"}
                        },
                        "required": ["owner", "repo", "number"]
                    }
                }
            }
        ]

    def chat_with_tools(self, message: str, history: List[Dict[str, Any]] = None) -> str:
        """
        Chat with OpenAI using GitHub tools.
        
        Args:
            message: User message
            history: Conversation history
            
        Returns:
            AI response
        """
        try:
            print(f"Starting chat with tools. Message: {message[:50]}...")
            print(f"Tools available: {len(self.tools)}")
            
            # Prepare messages
            messages = history or []
            messages.append({"role": "user", "content": message})
            
            # Make initial request with tools
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message_response = response.choices[0].message
            
            # Check if there are tool calls
            if message_response.tool_calls:
                print(f"Received {len(message_response.tool_calls)} tool calls")
                
                # Add assistant message with tool calls
                messages.append(message_response)
                
                # Execute each tool call
                for tool_call in message_response.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"Function call: {function_name} with args: {function_args}")
                    
                    # Execute the function
                    result = self._execute_function(function_name, function_args)
                    
                    print(f"Function result: {str(result)[:100]}...")
                    
                    # Add tool response
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                
                # Get final response with tool results
                final_response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )
                
                return final_response.choices[0].message.content
            
            print("No tool calls detected, returning direct text response")
            return message_response.content
            
        except Exception as e:
            print(f"Error in chat_with_tools: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return f"Error: {str(e)}"

    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GitHub function based on the function name and arguments."""
        try:
            if function_name == "create_repository":
                return self._create_repository(**args)
            elif function_name == "get_repository":
                return self._get_repository(**args)
            elif function_name == "list_repositories":
                return self._list_repositories(**args)
            elif function_name == "update_repository":
                return self._update_repository(**args)
            elif function_name == "create_pull_request":
                return self._create_pull_request(**args)
            elif function_name == "list_pull_requests":
                return self._list_pull_requests(**args)
            elif function_name == "get_pull_request":
                return self._get_pull_request(**args)
            elif function_name == "analyze_pull_request":
                return self._analyze_pull_request(**args)
            elif function_name == "merge_pull_request":
                return self._merge_pull_request(**args)
            elif function_name == "close_pull_request":
                return self._close_pull_request(**args)
            elif function_name == "create_issue":
                return self._create_issue(**args)
            elif function_name == "list_issues":
                return self._list_issues(**args)
            elif function_name == "get_issue":
                return self._get_issue(**args)
            elif function_name == "analyze_issue":
                return self._analyze_issue(**args)
            elif function_name == "analyze_repository_health":
                return self._analyze_repository_health(**args)
            elif function_name == "update_issue":
                return self._update_issue(**args)
            elif function_name == "close_issue":
                return self._close_issue(**args)
            elif function_name == "get_organization":
                return self._get_organization(**args)
            elif function_name == "list_organization_repositories":
                return self._list_organization_repositories(**args)
            elif function_name == "list_organization_members":
                return self._list_organization_members(**args)
            elif function_name == "list_organization_teams":
                return self._list_organization_teams(**args)
            elif function_name == "get_organization_team":
                return self._get_organization_team(**args)
            elif function_name == "analyze_organization_health":
                return self._analyze_organization_health(**args)
            elif function_name == "get_organization_issues":
                return self._get_organization_issues(**args)
            elif function_name == "get_organization_pull_requests":
                return self._get_organization_pull_requests(**args)
            else:
                return {"error": f"Unknown function: {function_name}"}
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}

    # Repository functions
    def _create_repository(self, name: str, description: str = "", private: bool = False, auto_init: bool = True) -> Dict[str, Any]:
        """Create a new repository."""
        try:
            user = self.github.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init
            )
            return {
                "success": True,
                "repository": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "private": repo.private,
                    "description": repo.description
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            return {
                "success": True,
                "repository": {
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "url": repository.html_url,
                    "private": repository.private,
                    "description": repository.description,
                    "language": repository.language,
                    "stars": repository.stargazers_count,
                    "forks": repository.forks_count,
                    "open_issues": repository.open_issues_count,
                    "created_at": repository.created_at.isoformat() if repository.created_at else None,
                    "updated_at": repository.updated_at.isoformat() if repository.updated_at else None
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_repositories(self, type: str = "owner", sort: str = "updated", per_page: int = 30) -> Dict[str, Any]:
        """List repositories for authenticated user."""
        try:
            user = self.github.get_user()
            repos = user.get_repos(type=type, sort=sort)
            
            repositories = []
            for i, repo in enumerate(repos):
                if i >= per_page:
                    break
                repositories.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "private": repo.private,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count
                })
            
            return {"success": True, "repositories": repositories}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _update_repository(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """Update repository settings."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            repository.edit(**{k: v for k, v in kwargs.items() if v is not None})
            return {"success": True, "message": "Repository updated successfully"}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    # Pull Request functions
    def _create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, 
                           body: str = "", draft: bool = False) -> Dict[str, Any]:
        """Create a new pull request."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
            return {
                "success": True,
                "pull_request": {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "state": pr.state,
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_pull_requests(self, owner: str, repo: str, state: str = "open", 
                          sort: str = "created", per_page: int = 30) -> Dict[str, Any]:
        """List pull requests in a repository."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            prs = repository.get_pulls(state=state, sort=sort)
            
            pull_requests = []
            for i, pr in enumerate(prs):
                if i >= per_page:
                    break
                pull_requests.append({
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "state": pr.state,
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "user": pr.user.login if pr.user else None,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None
                })
            
            return {"success": True, "pull_requests": pull_requests}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_pull_request(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Get specific pull request details with enhanced information."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(number)
            
            # Get files changed
            files_changed = []
            try:
                for file in pr.get_files():
                    files_changed.append({
                        "filename": file.filename,
                        "status": file.status,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "changes": file.changes
                    })
            except:
                files_changed = []
            
            # Get comments
            comments = []
            try:
                for comment in pr.get_issue_comments():
                    comments.append({
                        "user": comment.user.login if comment.user else "Unknown",
                        "body": comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None
                    })
            except:
                comments = []
            
            # Get reviews
            reviews = []
            try:
                for review in pr.get_reviews():
                    reviews.append({
                        "user": review.user.login if review.user else "Unknown",
                        "state": review.state,
                        "body": review.body[:100] + "..." if review.body and len(review.body) > 100 else review.body,
                        "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None
                    })
            except:
                reviews = []
            
            return {
                "success": True,
                "pull_request": {
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "url": pr.html_url,
                    "state": pr.state,
                    "head": pr.head.ref,
                    "base": pr.base.ref,
                    "user": pr.user.login if pr.user else None,
                    "mergeable": pr.mergeable,
                    "merged": pr.merged,
                    "draft": pr.draft,
                    "additions": pr.additions,
                    "deletions": pr.deletions,
                    "changed_files": pr.changed_files,
                    "commits": pr.commits,
                    "files_changed": files_changed[:10],  # Limit to first 10 files
                    "comments": comments[:5],  # Limit to first 5 comments
                    "reviews": reviews[:5],  # Limit to first 5 reviews
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _merge_pull_request(self, owner: str, repo: str, number: int, 
                          commit_message: str = None, merge_method: str = "merge") -> Dict[str, Any]:
        """Merge a pull request."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(number)
            result = pr.merge(commit_message=commit_message, merge_method=merge_method)
            return {
                "success": True,
                "merged": result.merged,
                "sha": result.sha,
                "message": result.message
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _close_pull_request(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Close a pull request without merging."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(number)
            pr.edit(state="closed")
            return {"success": True, "message": f"Pull request #{number} closed"}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    # Issue functions
    def _create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                     labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
        """Create a new issue."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            return {
                "success": True,
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "created_at": issue.created_at.isoformat() if issue.created_at else None
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_issues(self, owner: str, repo: str, state: str = "open", 
                    labels: List[str] = None, sort: str = "created", per_page: int = 30) -> Dict[str, Any]:
        """List issues in a repository."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issues = repository.get_issues(state=state, labels=labels or [], sort=sort)
            
            issue_list = []
            for i, issue in enumerate(issues):
                if i >= per_page:
                    break
                # Filter out pull requests (GitHub API returns both issues and PRs)
                if issue.pull_request is None:
                    issue_list.append({
                        "number": issue.number,
                        "title": issue.title,
                        "url": issue.html_url,
                        "state": issue.state,
                        "labels": [label.name for label in issue.labels],
                        "assignees": [assignee.login for assignee in issue.assignees],
                        "user": issue.user.login if issue.user else None,
                        "created_at": issue.created_at.isoformat() if issue.created_at else None
                    })
            
            return {"success": True, "issues": issue_list}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_issue(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Get specific issue details with enhanced information."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(number)
            
            # Get comments
            comments = []
            try:
                for comment in issue.get_comments():
                    comments.append({
                        "user": comment.user.login if comment.user else "Unknown",
                        "body": comment.body[:300] + "..." if len(comment.body) > 300 else comment.body,
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "updated_at": comment.updated_at.isoformat() if comment.updated_at else None
                    })
            except:
                comments = []
            
            # Get events (timeline)
            events = []
            try:
                for event in issue.get_events()[:10]:  # Limit to recent events
                    events.append({
                        "event": event.event,
                        "actor": event.actor.login if event.actor else "Unknown",
                        "created_at": event.created_at.isoformat() if event.created_at else None
                    })
            except:
                events = []
            
            return {
                "success": True,
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "url": issue.html_url,
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "user": issue.user.login if issue.user else None,
                    "comments": issue.comments,
                    "comments_detail": comments[:5],  # First 5 comments with details
                    "events": events[:5],  # Recent events
                    "milestone": issue.milestone.title if issue.milestone else None,
                    "locked": issue.locked,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _update_issue(self, owner: str, repo: str, number: int, **kwargs) -> Dict[str, Any]:
        """Update an existing issue."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(number)
            issue.edit(**{k: v for k, v in kwargs.items() if v is not None})
            return {"success": True, "message": f"Issue #{number} updated successfully"}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _close_issue(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Close an issue."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(number)
            issue.edit(state="closed")
            return {"success": True, "message": f"Issue #{number} closed"}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _analyze_pull_request(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Analyze a pull request to understand why it was created and its impact."""
        try:
            # First get the detailed PR information
            pr_data = self._get_pull_request(owner, repo, number)
            if not pr_data["success"]:
                return pr_data
            
            pr = pr_data["pull_request"]
            
            # Prepare analysis prompt for OpenAI
            analysis_prompt = f"""
Analyze this GitHub Pull Request and provide insights:

**Pull Request Details:**
- Title: {pr['title']}
- Description: {pr['body'][:500] if pr['body'] else 'No description'}
- Author: {pr['user']}
- Files Changed: {pr['changed_files']} files
- Lines Added: {pr['additions']}
- Lines Deleted: {pr['deletions']}
- Status: {pr['state']} ({'Draft' if pr.get('draft') else 'Ready'})

**Files Modified:**
{chr(10).join([f"- {f['filename']} ({f['status']}, +{f['additions']}/-{f['deletions']})" for f in pr['files_changed'][:5]])}

**Comments Summary:**
{chr(10).join([f"- {c['user']}: {c['body'][:100]}" for c in pr['comments'][:3]])}

**Reviews:**
{chr(10).join([f"- {r['user']}: {r['state']} - {r['body'][:50] if r['body'] else 'No comment'}" for r in pr['reviews'][:3]])}

Please analyze and answer:
1. **WHY was this PR created?** (What problem does it solve?)
2. **WHAT is the main purpose/goal?** (Feature, bugfix, refactor, etc.)
3. **HOW significant is the impact?** (Based on files changed and scope)
4. **WHAT are the key risks or concerns?** (Based on reviews and discussions)
5. **SHOULD this be merged?** (Based on reviews, tests, and overall quality)

Provide a comprehensive analysis in a structured format.
"""
            
            # Generate analysis using OpenAI
            analysis = self.generate_text(analysis_prompt)
            
            return {
                "success": True,
                "analysis": {
                    "pull_request_number": number,
                    "analysis_text": analysis,
                    "metadata": {
                        "files_changed": pr['changed_files'],
                        "lines_changed": pr['additions'] + pr['deletions'],
                        "author": pr['user'],
                        "reviewers": len(pr['reviews']),
                        "comments": len(pr['comments'])
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_issue(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """Analyze an issue to understand the problem and suggest solutions."""
        try:
            # Get the detailed issue information
            issue_data = self._get_issue(owner, repo, number)
            if not issue_data["success"]:
                return issue_data
            
            issue = issue_data["issue"]
            
            # Prepare analysis prompt for OpenAI
            analysis_prompt = f"""
Analyze this GitHub Issue and provide insights:

**Issue Details:**
- Title: {issue['title']}
- Description: {issue['body'][:500] if issue['body'] else 'No description'}
- Author: {issue['user']}
- Labels: {', '.join(issue['labels']) if issue['labels'] else 'None'}
- Assignees: {', '.join(issue['assignees']) if issue['assignees'] else 'None'}
- Comments: {issue['comments']} comments
- Status: {issue['state']}
- Created: {issue['created_at']}

Please analyze and answer:
1. **WHY was this issue created?** (What problem or need does it address?)
2. **WHAT type of issue is this?** (Bug, feature request, question, documentation, etc.)
3. **HOW urgent/important is this?** (Based on labels, description, and impact)
4. **WHAT are potential solutions?** (Suggest 2-3 approaches to resolve this)
5. **WHO should handle this?** (What type of expertise is needed?)
6. **WHEN should this be prioritized?** (Timeline estimation)

Provide a comprehensive analysis in a structured format.
"""
            
            # Generate analysis using OpenAI
            analysis = self.generate_text(analysis_prompt)
            
            return {
                "success": True,
                "analysis": {
                    "issue_number": number,
                    "analysis_text": analysis,
                    "metadata": {
                        "labels": issue['labels'],
                        "comments_count": issue['comments'],
                        "author": issue['user'],
                        "assignees": issue['assignees']
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_repository_health(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository health and development patterns."""
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            
            # Get recent activity data
            recent_commits = list(repository.get_commits()[:10])
            open_issues = list(repository.get_issues(state='open')[:10])
            closed_issues = list(repository.get_issues(state='closed')[:5])
            open_prs = list(repository.get_pulls(state='open')[:5])
            closed_prs = list(repository.get_pulls(state='closed')[:5])
            
            # Prepare analysis prompt for OpenAI
            analysis_prompt = f"""
Analyze this GitHub Repository's health and development patterns:

**Repository Overview:**
- Name: {repository.full_name}
- Description: {repository.description or 'No description'}
- Stars: {repository.stargazers_count}
- Forks: {repository.forks_count}
- Watchers: {repository.watchers_count}
- Language: {repository.language}
- Size: {repository.size} KB
- Created: {repository.created_at.isoformat() if repository.created_at else 'Unknown'}
- Last Updated: {repository.updated_at.isoformat() if repository.updated_at else 'Unknown'}

**Current Activity:**
- Open Issues: {len(open_issues)} (Total: {repository.open_issues_count})
- Open PRs: {len(open_prs)}
- Recent Commits: {len(recent_commits)} in last period
- Default Branch: {repository.default_branch}

**Recent Commit Activity:**
{chr(10).join([f"- {commit.commit.message[:100]} by {commit.commit.author.name}" for commit in recent_commits[:5]])}

**Open Issues Sample:**
{chr(10).join([f"- #{issue.number}: {issue.title[:80]}" for issue in open_issues[:5]])}

Please analyze and provide insights on:
1. **Repository Health Score** (1-10 based on activity, maintenance, community)
2. **Development Velocity** (How active is the development?)
3. **Community Engagement** (Stars, forks, issue discussions)
4. **Code Quality Indicators** (Based on PR patterns, issue types)
5. **Maintenance Status** (Is this actively maintained?)
6. **Potential Issues** (What problems do you see?)
7. **Recommendations** (What should be improved?)

Provide a comprehensive health analysis.
"""
            
            # Generate analysis using OpenAI
            analysis = self.generate_text(analysis_prompt)
            
            return {
                "success": True,
                "analysis": {
                    "repository": f"{owner}/{repo}",
                    "analysis_text": analysis,
                    "metadata": {
                        "stars": repository.stargazers_count,
                        "forks": repository.forks_count,
                        "open_issues": repository.open_issues_count,
                        "language": repository.language,
                        "last_updated": repository.updated_at.isoformat() if repository.updated_at else None,
                        "recent_commits": len(recent_commits),
                        "open_prs": len(open_prs)
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Organization functions
    def _get_organization(self, org: str) -> Dict[str, Any]:
        """Get organization information."""
        try:
            organization = self.github.get_organization(org)
            return {
                "success": True,
                "organization": {
                    "name": organization.name,
                    "login": organization.login,
                    "description": organization.description,
                    "location": organization.location,
                    "email": organization.email,
                    "blog": organization.blog,
                    "company": organization.company,
                    "public_repos": organization.public_repos,
                    "public_gists": organization.public_gists,
                    "followers": organization.followers,
                    "following": organization.following,
                    "html_url": organization.html_url,
                    "created_at": organization.created_at.isoformat() if organization.created_at else None,
                    "updated_at": organization.updated_at.isoformat() if organization.updated_at else None,
                    "type": organization.type
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_organization_repositories(self, org: str, type: str = "all", sort: str = "updated", per_page: int = 30) -> Dict[str, Any]:
        """List repositories in an organization."""
        try:
            organization = self.github.get_organization(org)
            repos = organization.get_repos(type=type, sort=sort)
            
            repositories = []
            for i, repo in enumerate(repos):
                if i >= per_page:
                    break
                repositories.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "private": repo.private,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                })
            
            return {"success": True, "repositories": repositories, "organization": org}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_organization_members(self, org: str, role: str = "all", per_page: int = 30) -> Dict[str, Any]:
        """List members of an organization."""
        try:
            organization = self.github.get_organization(org)
            members = organization.get_members()
            
            member_list = []
            for i, member in enumerate(members):
                if i >= per_page:
                    break
                member_list.append({
                    "login": member.login,
                    "name": member.name,
                    "email": member.email,
                    "company": member.company,
                    "location": member.location,
                    "bio": member.bio,
                    "public_repos": member.public_repos,
                    "followers": member.followers,
                    "following": member.following,
                    "html_url": member.html_url,
                    "avatar_url": member.avatar_url
                })
            
            return {"success": True, "members": member_list, "organization": org}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _list_organization_teams(self, org: str, per_page: int = 30) -> Dict[str, Any]:
        """List teams in an organization."""
        try:
            organization = self.github.get_organization(org)
            teams = organization.get_teams()
            
            team_list = []
            for i, team in enumerate(teams):
                if i >= per_page:
                    break
                team_list.append({
                    "name": team.name,
                    "slug": team.slug,
                    "description": team.description,
                    "privacy": team.privacy,
                    "permission": team.permission,
                    "members_count": team.members_count,
                    "repos_count": team.repos_count,
                    "html_url": team.html_url
                })
            
            return {"success": True, "teams": team_list, "organization": org}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_organization_team(self, org: str, team_slug: str) -> Dict[str, Any]:
        """Get specific team information and members."""
        try:
            organization = self.github.get_organization(org)
            team = organization.get_team_by_slug(team_slug)
            
            # Get team members
            members = []
            try:
                for member in team.get_members():
                    members.append({
                        "login": member.login,
                        "name": member.name,
                        "html_url": member.html_url
                    })
            except:
                members = []
            
            # Get team repositories
            repositories = []
            try:
                for repo in team.get_repos():
                    repositories.append({
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "url": repo.html_url,
                        "private": repo.private
                    })
            except:
                repositories = []
            
            return {
                "success": True,
                "team": {
                    "name": team.name,
                    "slug": team.slug,
                    "description": team.description,
                    "privacy": team.privacy,
                    "permission": team.permission,
                    "members_count": team.members_count,
                    "repos_count": team.repos_count,
                    "html_url": team.html_url,
                    "members": members[:10],  # Limit to first 10
                    "repositories": repositories[:10]  # Limit to first 10
                }
            }
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_organization_issues(self, org: str, state: str = "open", labels: List[str] = None, 
                                sort: str = "created", per_page: int = 30) -> Dict[str, Any]:
        """Get issues across all organization repositories."""
        try:
            organization = self.github.get_organization(org)
            repos = list(organization.get_repos()[:10])  # Limit to first 10 repos for performance
            
            all_issues = []
            for repo in repos:
                try:
                    issues = repo.get_issues(state=state, labels=labels or [], sort=sort)
                    repo_issues = []
                    for i, issue in enumerate(issues):
                        if len(all_issues) >= per_page:
                            break
                        # Filter out pull requests
                        if issue.pull_request is None:
                            repo_issues.append({
                                "repository": repo.name,
                                "number": issue.number,
                                "title": issue.title,
                                "url": issue.html_url,
                                "state": issue.state,
                                "labels": [label.name for label in issue.labels],
                                "assignees": [assignee.login for assignee in issue.assignees],
                                "user": issue.user.login if issue.user else None,
                                "created_at": issue.created_at.isoformat() if issue.created_at else None
                            })
                    all_issues.extend(repo_issues)
                    if len(all_issues) >= per_page:
                        break
                except:
                    continue
            
            return {"success": True, "issues": all_issues, "organization": org}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _get_organization_pull_requests(self, org: str, state: str = "open", 
                                       sort: str = "created", per_page: int = 30) -> Dict[str, Any]:
        """Get pull requests across all organization repositories."""
        try:
            organization = self.github.get_organization(org)
            repos = list(organization.get_repos()[:10])  # Limit to first 10 repos for performance
            
            all_prs = []
            for repo in repos:
                try:
                    prs = repo.get_pulls(state=state, sort=sort)
                    repo_prs = []
                    for i, pr in enumerate(prs):
                        if len(all_prs) >= per_page:
                            break
                        repo_prs.append({
                            "repository": repo.name,
                            "number": pr.number,
                            "title": pr.title,
                            "url": pr.html_url,
                            "state": pr.state,
                            "head": pr.head.ref,
                            "base": pr.base.ref,
                            "user": pr.user.login if pr.user else None,
                            "created_at": pr.created_at.isoformat() if pr.created_at else None
                        })
                    all_prs.extend(repo_prs)
                    if len(all_prs) >= per_page:
                        break
                except:
                    continue
            
            return {"success": True, "pull_requests": all_prs, "organization": org}
        except GithubException as e:
            return {"success": False, "error": str(e)}

    def _analyze_organization_health(self, org: str) -> Dict[str, Any]:
        """Analyze organization-wide health and development patterns."""
        try:
            organization = self.github.get_organization(org)
            
            # Get organization data
            repos = list(organization.get_repos()[:20])  # Sample of repositories
            members = list(organization.get_members()[:50])  # Sample of members
            
            # Calculate metrics
            total_repos = len(repos)
            total_stars = sum(repo.stargazers_count for repo in repos)
            total_forks = sum(repo.forks_count for repo in repos)
            total_open_issues = sum(repo.open_issues_count for repo in repos)
            
            # Get recent activity data
            recent_repos = [repo for repo in repos if repo.updated_at and repo.updated_at > repo.created_at]
            active_repos = len([repo for repo in repos if repo.open_issues_count > 0])
            
            # Language distribution
            languages = {}
            for repo in repos:
                if repo.language:
                    languages[repo.language] = languages.get(repo.language, 0) + 1
            
            # Prepare analysis prompt
            analysis_prompt = f"""
Analyze this GitHub Organization's health and development patterns:

**Organization Overview:**
- Name: {organization.name or organization.login}
- Description: {organization.description or 'No description'}
- Public Repos: {organization.public_repos}
- Members: {len(members)}
- Location: {organization.location or 'Not specified'}
- Website: {organization.blog or 'Not specified'}

**Repository Metrics:**
- Sample Analyzed: {total_repos} repositories
- Total Stars: {total_stars}
- Total Forks: {total_forks}
- Total Open Issues: {total_open_issues}
- Active Repositories: {active_repos}

**Language Distribution:**
{chr(10).join([f"- {lang}: {count} repos" for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]])}

**Top Repositories by Stars:**
{chr(10).join([f"- {repo.name}: {repo.stargazers_count} stars" for repo in sorted(repos, key=lambda x: x.stargazers_count, reverse=True)[:5]])}

Please analyze and provide insights on:
1. **Organization Health Score** (1-10 based on activity, diversity, community)
2. **Development Activity** (How active is the organization?)
3. **Technology Stack** (What technologies does the org focus on?)
4. **Community Engagement** (Stars, forks, contributions)
5. **Repository Quality** (Based on maintenance patterns)
6. **Growth Patterns** (Expansion and development trends)
7. **Recommendations** (What should be improved organization-wide?)

Provide a comprehensive organizational analysis.
"""
            
            # Generate analysis using OpenAI
            analysis = self.generate_text(analysis_prompt)
            
            return {
                "success": True,
                "analysis": {
                    "organization": org,
                    "analysis_text": analysis,
                    "metadata": {
                        "total_repos_sampled": total_repos,
                        "total_stars": total_stars,
                        "total_forks": total_forks,
                        "total_open_issues": total_open_issues,
                        "members_count": len(members),
                        "public_repos": organization.public_repos,
                        "languages": languages,
                        "organization_created": organization.created_at.isoformat() if organization.created_at else None
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_text(self, prompt: str) -> str:
        """Generate text using OpenAI without tools."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Initialize client (requires OPENAI_API_KEY and GITHUB_TOKEN environment variables)
    try:
        client = OpenAIGitHubClient()
        
        # Example conversation
        response = client.chat_with_tools("List my repositories")
        print("AI Response:", response)
        
        response = client.chat_with_tools("Create a new issue in my repository titled 'Test Issue'")
        print("AI Response:", response)
        
    except Exception as e:
        print(f"Error initializing client: {e}")