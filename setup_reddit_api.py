#!/usr/bin/env python3
"""
Reddit API Setup Utility
Helps users configure their Reddit API credentials
"""

import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, Optional
import getpass
import sys


class RedditAPISetup:
    def __init__(self):
        self.config_file = Path("config.json")
        self.env_file = Path(".env")
        
    def print_header(self):
        print("\n" + "="*60)
        print("🤖 Reddit API Configuration Setup")
        print("="*60 + "\n")
    
    def print_registration_guide(self):
        print("📋 STEP 1: Register for Reddit API (if you haven't already)")
        print("-" * 50)
        print("1. Opening Reddit Apps page in your browser...")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Fill in:")
        print("   • Name: reddit-monitor (or any name)")
        print("   • Type: Select 'script' (IMPORTANT!)")
        print("   • Description: Personal monitoring tool")
        print("   • Redirect URI: http://localhost:8080")
        print("4. Click 'Create app'")
        print("5. You'll need:")
        print("   • Client ID: String under 'personal use script'")
        print("   • Client Secret: The secret key shown\n")
        
        input("Press Enter to open Reddit Apps page in browser...")
        webbrowser.open("https://www.reddit.com/prefs/apps")
        input("Press Enter after you've created your app and have the credentials...")
    
    def get_credentials(self) -> Dict[str, str]:
        print("\n📝 STEP 2: Enter your Reddit API credentials")
        print("-" * 50)
        
        credentials = {}
        
        # Client ID
        print("\nClient ID (found under 'personal use script'):")
        credentials['client_id'] = input("→ ").strip()
        
        # Client Secret
        print("\nClient Secret:")
        credentials['client_secret'] = getpass.getpass("→ ").strip()
        
        # User Agent
        print("\nUser Agent (e.g., 'reddit-monitor:v1.0 by /u/YOUR_USERNAME'):")
        default_ua = "reddit-monitor:v1.0"
        user_agent = input(f"→ (default: {default_ua}): ").strip()
        credentials['user_agent'] = user_agent or default_ua
        
        # Optional: Username and Password for authenticated requests
        print("\n⚠️  Optional: Reddit account credentials")
        print("(Leave blank for read-only access to public subreddits)")
        
        username = input("Reddit username (optional): ").strip()
        if username:
            credentials['username'] = username
            credentials['password'] = getpass.getpass("Reddit password: ").strip()
        
        return credentials
    
    def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Basic validation of credentials"""
        if not credentials.get('client_id'):
            print("❌ Client ID is required!")
            return False
        if not credentials.get('client_secret'):
            print("❌ Client Secret is required!")
            return False
        if len(credentials['client_id']) < 10:
            print("❌ Client ID seems too short. Please check it.")
            return False
        return True
    
    def save_config(self, credentials: Dict[str, str]):
        """Save configuration to config.json"""
        config = {
            "reddit": {
                "client_id": credentials['client_id'],
                "client_secret": credentials['client_secret'],
                "user_agent": credentials['user_agent']
            },
            "monitoring": {
                "subreddits": ["technology", "programming", "worldnews"],
                "refresh_interval": 30,
                "max_posts_per_sub": 25
            },
            "alerts": {
                "enabled": True,
                "keywords": ["breaking", "urgent", "announcement"],
                "min_score": 1000
            },
            "database": {
                "path": "reddit_data.db",
                "backup_enabled": True
            }
        }
        
        # Add optional username/password if provided
        if credentials.get('username'):
            config['reddit']['username'] = credentials['username']
            config['reddit']['password'] = credentials['password']
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved to {self.config_file}")
    
    def save_env(self, credentials: Dict[str, str]):
        """Save credentials to .env file for security"""
        env_content = f"""# Reddit API Credentials
REDDIT_CLIENT_ID={credentials['client_id']}
REDDIT_CLIENT_SECRET={credentials['client_secret']}
REDDIT_USER_AGENT={credentials['user_agent']}
"""
        
        if credentials.get('username'):
            env_content += f"""REDDIT_USERNAME={credentials['username']}
REDDIT_PASSWORD={credentials['password']}
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Environment variables saved to {self.env_file}")
        
        # Add .env to .gitignore if not already there
        gitignore = Path(".gitignore")
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            if '.env' not in content:
                with open(gitignore, 'a') as f:
                    f.write("\n# Environment variables\n.env\n")
                print("✅ Added .env to .gitignore")
    
    def test_connection(self):
        """Test the Reddit API connection"""
        print("\n🔧 Testing Reddit API connection...")
        print("-" * 50)
        
        try:
            from reddit_client import RedditClient
            client = RedditClient()
            
            if client.test_connection():
                print("✅ Successfully connected to Reddit API!")
                print("\nYou can now run: python main.py")
                return True
            else:
                print("❌ Connection test failed. Please check your credentials.")
                return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
    
    def run(self):
        """Main setup flow"""
        self.print_header()
        
        # Check if config already exists
        if self.config_file.exists():
            print("⚠️  Configuration file already exists!")
            overwrite = input("Do you want to overwrite it? (y/n): ").lower()
            if overwrite != 'y':
                print("Setup cancelled.")
                return
        
        # Registration guide
        register = input("Do you need to register for Reddit API? (y/n): ").lower()
        if register == 'y':
            self.print_registration_guide()
        
        # Get credentials
        credentials = self.get_credentials()
        
        # Validate
        if not self.validate_credentials(credentials):
            print("\n❌ Invalid credentials. Please run setup again.")
            return
        
        # Save configuration
        print("\n💾 Saving configuration...")
        self.save_config(credentials)
        self.save_env(credentials)
        
        # Test connection
        test = input("\nDo you want to test the connection now? (y/n): ").lower()
        if test == 'y':
            self.test_connection()
        
        print("\n✨ Setup complete!")
        print("\nNext steps:")
        print("1. Run: python main.py monitor")
        print("2. Or test: python main.py test")
        print("3. Configure subreddits in config.json")


def main():
    setup = RedditAPISetup()
    try:
        setup.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()