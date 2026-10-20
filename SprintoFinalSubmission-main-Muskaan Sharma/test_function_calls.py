#!/usr/bin/env python3
"""
Test specific function calls with the fixed Gemini client
"""

import os
import sys
from gemini_github_client import GeminiGitHubClient

def test_function_calls():
    """Test specific function calls that should work"""
    try:
        # Set environment variables
        os.environ["GITHUB_TOKEN"] = "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"
        os.environ["GOOGLE_API_KEY"] = "AIzaSyAFZPQGzOO-rR936htzc1La8lX6OmRWRC8"
        
        print("Initializing GeminiGitHubClient...")
        client = GeminiGitHubClient()
        print("✓ Client initialized successfully")
        
        # Test repository listing (should trigger function call)
        print("\nTesting query: 'List my repositories'")
        response = client.chat_with_tools("List my repositories")
        print(f"Response: {response[:300]}...")
        
        if "Error:" not in response:
            print("✓ Repository listing worked!")
        else:
            print(f"✗ Repository listing failed: {response}")
            return False
            
        return True
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_function_calls()
    sys.exit(0 if success else 1)