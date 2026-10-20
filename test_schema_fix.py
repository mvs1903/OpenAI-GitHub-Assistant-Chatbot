#!/usr/bin/env python3
"""
Test script to verify Gemini schema fixes
"""

import os
import sys
from gemini_github_client import GeminiGitHubClient

def test_client_init():
    """Test basic client initialization"""
    try:
        # Set environment variables
        os.environ["GITHUB_TOKEN"] = "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"
        os.environ["GOOGLE_API_KEY"] = "AIzaSyAFZPQGzOO-rR936htzc1La8lX6OmRWRC8"
        
        print("Initializing GeminiGitHubClient...")
        client = GeminiGitHubClient()
        print("✓ Client initialized successfully")
        
        print(f"✓ Found {len(client.tools)} tool groups")
        print(f"✓ Found {len(client.tools[0].function_declarations)} function declarations")
        
        # Test a simple query
        print("\nTesting simple query: 'what issues need urgent attention?'")
        response = client.chat_with_tools("what issues need urgent attention?")
        print(f"Response: {response[:200]}...")
        
        if not response.startswith("Error:"):
            print("✓ Query completed successfully!")
            return True
        else:
            print(f"✗ Query failed: {response}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_client_init()
    sys.exit(0 if success else 1)