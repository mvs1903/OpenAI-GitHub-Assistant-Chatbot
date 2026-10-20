# 🤖 OpenAI GitHub Assistant Chatbot

A modern web-based chatbot that combines OpenAI's GPT models with GitHub API to provide intelligent GitHub repository management through natural language conversations.

## ✨ Features

- **🗣️ Natural Language Interface**: Chat with your GitHub repositories using plain English
- **🤖 AI-Powered**: Powered by OpenAI's GPT models for intelligent responses
- **📚 Repository Management**: List, create, and manage repositories
- **🐛 Issue Tracking**: Create, list, and manage GitHub issues
- **🔄 Pull Request Management**: Handle PRs with conversational commands
- **💻 Modern UI**: Beautiful, responsive chatbot interface
- **⚡ Real-time**: Instant responses with typing indicators
- **🔒 Secure**: Uses OAuth tokens for GitHub authentication

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- GitHub Personal Access Token
- OpenAI API Key (required for AI features)

### Installation

1. **Clone or download the files to your directory**

2. **Install dependencies:**
   ```bash
   source venv/bin/activate  # Activate virtual environment
   pip install flask flask-cors openai PyGithub
   ```

3. **Set up environment variables:**
   ```bash
   export GITHUB_TOKEN="your_github_personal_access_token"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

4. **Run the chatbot:**
   ```bash
   python run_chatbot.py
   ```

5. **Open your browser** to `http://localhost:8000`

## 🎯 Usage Examples

Try these natural language commands in the chatbot:

### Repository Operations
- "List my repositories"
- "Show me info about octocat/Hello-World"
- "What repositories do I have?"

### Issue Management  
- "List issues in my repo"
- "Show open issues"
- "Create an issue titled 'Bug in login'"

### User Information
- "Who am I?"
- "Show my GitHub profile"

### General Help
- "Help"
- "What can you do?"

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│  Gemini AI API  │
│   (Frontend)    │    │   (Backend)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  GitHub API     │
                       │                 │
                       └─────────────────┘
```

## 📁 Project Structure

```
├── app.py                 # Flask backend server
├── openai_github_client.py # OpenAI + GitHub integration
├── run_chatbot.py         # Launch script
├── templates/
│   └── index.html         # Chatbot web interface
├── test_openai_github.py  # Test script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT models |

### Getting API Keys

#### GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with repo, issues, and pull requests permissions
3. Copy the token and set it as `GITHUB_TOKEN`

#### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Set it as `OPENAI_API_KEY`

**Note**: OpenAI API key is required for AI-powered features.

## 🌟 Features Detail

### 🤖 AI Integration
- **GPT-4o**: Advanced language understanding and reasoning
- **Function Calling**: Direct GitHub API integration
- **Context Awareness**: Maintains conversation context
- **Error Handling**: Graceful fallbacks and error messages

### 🎨 User Interface
- **Modern Design**: Clean, gradient-based interface
- **Responsive**: Works on desktop and mobile
- **Real-time**: Typing indicators and instant responses
- **Accessibility**: Keyboard navigation and screen reader friendly

### 🔒 Security
- **Token-based Auth**: Secure GitHub authentication
- **Input Validation**: Prevents injection attacks
- **Error Sanitization**: Safe error message handling

## 🛠️ Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Testing

```bash
python test_gemini_github.py
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve chatbot interface |
| `/chat` | POST | Process chat messages |
| `/health` | GET | Health check |

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **"Invalid GitHub token"**
   - Check your GITHUB_TOKEN environment variable
   - Ensure token has required permissions

3. **"OpenAI API errors"**
   - Verify OPENAI_API_KEY is correct
   - Check API quota limits

4. **Port 5000 in use**
   - Change port in `app.py`: `app.run(port=8000)`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs in the terminal
3. Ensure all environment variables are set
4. Try the basic GitHub API test first

---

**Made with ❤️ using OpenAI GPT and GitHub API**

## How to Run the Project

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set the environment variables:**
    ```bash
    export GITHUB_TOKEN="your_github_personal_access_token"
    export OPENAI_API_KEY="your_openai_api_key"
    ```

5.  **Run the application:**
    ```bash
    python run_chatbot.py
    ```

6.  **Open your browser** and navigate to `http://localhost:8000`.
