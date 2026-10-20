"""
Flask web application for Gemini GitHub Assistant chatbot
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from openai_github_client import OpenAIGitHubClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the OpenAI GitHub client
openai_client = None

def initialize_client():
    """Initialize the OpenAI GitHub client with environment variables or defaults"""
    global openai_client
    try:
        # Set default values for demonstration
        # In production, these should be actual environment variables
        openai_api_key = ""
        github_token = ""
        
        
        openai_client = OpenAIGitHubClient(
            openai_api_key=openai_api_key,
            github_token=github_token
        )
        logger.info("OpenAI GitHub client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI GitHub client: {e}")
        return False

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Check if client is initialized
        if openai_client is None:
            if not initialize_client():
                return jsonify({
                    'success': False,
                    'error': 'AI service is not available. Please check configuration.'
                })
        
        # Handle special commands or direct GitHub API calls if Gemini is not available
        response = handle_message(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

def handle_message(user_message):
    """Process user message and generate response"""
    try:
        # First try with Gemini if available
        if openai_client:
            try:
                logger.info(f"Using OpenAI for query: {user_message[:50]}...")
                response = openai_client.chat_with_tools(user_message)
                if not response.startswith("Error:"):
                    logger.info("OpenAI response successful")
                    return response
                else:
                    logger.warning(f"OpenAI returned error: {response}")
            except Exception as e:
                logger.warning(f"OpenAI API error: {e}")
        
        # Fallback to direct GitHub API operations
        return handle_github_commands(user_message.lower())
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return f"I encountered an error: {str(e)}"

def handle_github_commands(message):
    """Handle GitHub commands directly when Gemini is not available"""
    try:
        from github import Github, GithubException
        
        github_token = ""
        if not github_token:
            return "GitHub token is not configured."
        
        github = Github(github_token)
        user = github.get_user()
        
        # Handle different command types
        if "list" in message and ("repo" in message or "repositories" in message):
            repos = list(user.get_repos()[:10])  # Limit to 10 repos
            if repos:
                repo_list = "\n".join([f"• {repo.name} ({repo.private and 'private' or 'public'}) - {repo.description or 'No description'}" for repo in repos])
                return f"📚 Your repositories:\n{repo_list}"
            else:
                return "You don't have any repositories yet."
        
        elif "create" in message and "repo" in message:
            return "To create a repository, please specify: 'Create repository named [name] with description [description]'"
        
        elif "list" in message and "issue" in message:
            # Try to get issues from the first repository
            repos = list(user.get_repos()[:1])
            if repos:
                repo = repos[0]
                issues = list(repo.get_issues(state='open')[:5])
                if issues:
                    issue_list = "\n".join([f"• #{issue.number}: {issue.title}" for issue in issues])
                    return f"🐛 Open issues in {repo.name}:\n{issue_list}"
                else:
                    return f"No open issues in {repo.name}"
            else:
                return "You don't have any repositories to check for issues."
        
        elif "help" in message or "what can you do" in message:
            return """🤖 I can help you with GitHub operations:

📚 **Repository Management:**
• "List my repositories"
• "Get repository info for [owner/repo]"

🐛 **Issues:**
• "List issues in [repo]"
• "Create issue in [repo] titled [title]"

🔄 **Pull Requests:**
• "List pull requests in [repo]"
• "Create pull request in [repo]"

💡 **Tips:**
• Be specific with repository names
• Use natural language - I'll understand!

Note: Full AI capabilities require a valid Google API key for Gemini."""
        
        elif "who am i" in message or "my info" in message:
            return f"👤 You are logged in as: **{user.login}**\n📧 Email: {user.email or 'Not public'}\n🏢 Company: {user.company or 'Not specified'}\n📍 Location: {user.location or 'Not specified'}\n📊 Public repos: {user.public_repos}"
        
        elif ("org" in message or "organization" in message) and "list" in message and "repo" in message:
            # Extract organization name from message
            words = message.split()
            org_name = None
            for word in words:
                if '/' not in word and word not in ['list', 'org', 'organization', 'repositories', 'repos', 'in', 'for']:
                    org_name = word
                    break
            
            if org_name:
                try:
                    org = github.get_organization(org_name)
                    repos = list(org.get_repos()[:10])
                    if repos:
                        repo_list = "\n".join([f"• {repo.name} ({repo.private and 'private' or 'public'}) - {repo.description or 'No description'}" for repo in repos])
                        return f"🏢 Repositories in {org_name}:\n{repo_list}"
                    else:
                        return f"No repositories found in organization {org_name}"
                except:
                    return f"Could not find organization '{org_name}' or you don't have access to it."
            else:
                return "Please specify an organization name, e.g., 'list repositories in microsoft'"
        
        elif ("org" in message or "organization" in message) and "info" in message:
            # Extract organization name from message
            words = message.split()
            org_name = None
            for word in words:
                if word not in ['org', 'organization', 'info', 'about', 'get']:
                    org_name = word
                    break
            
            if org_name:
                try:
                    org = github.get_organization(org_name)
                    return f"🏢 **{org.name or org.login}**\n📝 {org.description or 'No description'}\n📍 {org.location or 'Location not specified'}\n🌐 {org.blog or 'No website'}\n📊 Public repos: {org.public_repos}\n👥 Type: {org.type}\n🔗 {org.html_url}"
                except:
                    return f"Could not find organization '{org_name}' or you don't have access to it."
            else:
                return "Please specify an organization name, e.g., 'organization info microsoft'"
        
        else:
            # Try to extract repository information from the message
            words = message.split()
            for word in words:
                if '/' in word:  # Looks like owner/repo format
                    try:
                        repo = github.get_repo(word)
                        return f"📚 **{repo.full_name}**\n📝 {repo.description or 'No description'}\n⭐ Stars: {repo.stargazers_count}\n🍴 Forks: {repo.forks_count}\n📅 Created: {repo.created_at.strftime('%Y-%m-%d')}\n🔗 URL: {repo.html_url}"
                    except GithubException:
                        continue
            
            return """I understand you want to work with GitHub! Here are some things you can try:

• "List my repositories"
• "List issues"
• "Who am I" 
• "Help" - for more commands

Or mention a specific repository like "octocat/Hello-World" to get its information."""
    
    except Exception as e:
        logger.error(f"GitHub API error: {e}")
        return f"GitHub API error: {str(e)}"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'openai_available': openai_client is not None,
        'github_configured': bool(os.environ.get("GITHUB_TOKEN"))
    })

if __name__ == '__main__':
    # Initialize the client on startup
    initialize_client()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)