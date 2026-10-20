#!/usr/bin/env python3
"""
Launch script for the OpenAI GitHub Assistant chatbot
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open the chatbot in the default browser"""
    webbrowser.open('http://localhost:8000')

def main():
    """Main function to start the chatbot application"""
    print("🤖 Starting OpenAI GitHub Assistant Chatbot...")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        return
    
    if not os.path.exists('templates/index.html'):
        print("❌ Error: templates/index.html not found!")
        return
    
    # Show configuration status
    print("📋 Configuration Status:")
    print(f"   GitHub Token: {'✓ Set' if os.getenv('GITHUB_TOKEN') else '❌ Not set'}")
    print(f"   OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print()
    
    # Information about API keys
    if not os.getenv('OPENAI_API_KEY'):
        print("💡 Note: OpenAI GPT requires an OpenAI API key for full functionality.")
        print("   The chatbot will work with GitHub operations using fallback mode.")
        print("   To enable full AI features, set OPENAI_API_KEY environment variable.")
        print()
    
    print("🌐 Starting web server...")
    print("   URL: http://localhost:8000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser after a short delay
    Timer(2.0, open_browser).start()
    
    # Start the Flask app
    try:
        from app import app
        app.run(host='0.0.0.0', port=8000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Shutting down the chatbot. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting the application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())