#!/usr/bin/env python3
"""
Reddit Insight App - Demo Setup Script
Sets up the modern Reddit analysis app with all dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return False

def check_node_installed():
    """Check if Node.js is installed"""
    return run_command("node --version") and run_command("npm --version")

def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Failed to install Python dependencies")
        return False
    
    # Install additional Python packages for AI features
    ai_packages = [
        "textblob",
        "openai",
        "scikit-learn",
        "numpy",
        "pandas"
    ]
    
    for package in ai_packages:
        run_command(f"pip install {package}")
    
    # Install Node.js dependencies
    if check_node_installed():
        print("Installing Node.js dependencies...")
        if not run_command("npm install"):
            print("❌ Failed to install Node.js dependencies")
            return False
        
        # Install additional Electron dependencies
        if not run_command("npm install -D electron-is-dev"):
            print("❌ Failed to install Electron dependencies")
            return False
    else:
        print("⚠️  Node.js not found. Install Node.js to build the Electron app.")
        print("   You can still run the Python backend.")
    
    return True

def setup_env_file():
    """Create .env file with Reddit API configuration"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔧 Setting up Reddit API configuration...")
    print("You'll need Reddit API credentials from https://www.reddit.com/prefs/apps")
    
    client_id = input("Enter your Reddit Client ID: ").strip()
    client_secret = input("Enter your Reddit Client Secret: ").strip()
    user_agent = input("Enter User Agent (e.g., RedditInsightApp/1.0): ").strip()
    
    if not user_agent:
        user_agent = "RedditInsightApp/1.0"
    
    env_content = f"""# Reddit API Configuration
REDDIT_CLIENT_ID={client_id}
REDDIT_CLIENT_SECRET={client_secret}
REDDIT_USER_AGENT={user_agent}

# Optional: OpenAI API for enhanced summarization
# OPENAI_API_KEY=your_openai_api_key_here

# App Configuration
NODE_ENV=development
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    return True

def create_demo_data():
    """Create demo configuration and data"""
    print("🎯 Creating demo configuration...")
    
    # Create config.json for demo
    config_data = {
        "monitoring": {
            "subreddits": [
                "stocks", "investing", "wallstreetbets", "technology",
                "programming", "productivity", "personalfinance"
            ],
            "refresh_interval": 30
        },
        "app": {
            "demo_mode": True,
            "use_mock_data": True,
            "ai_summarization": True
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    print("✅ Created demo configuration")

def setup_project_structure():
    """Ensure all required directories exist"""
    directories = [
        "backend/intelligence",
        "backend/personalization", 
        "backend/api",
        "src/components/Auth",
        "src/components/Onboarding",
        "src/components/Feed",
        "src/components/Common",
        "src/context",
        "src/utils",
        "electron",
        "public",
        "exports",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Project structure validated")

def run_tests():
    """Run basic tests to validate setup"""
    print("🧪 Running setup validation...")
    
    # Test Python imports
    try:
        import praw
        import asyncpraw
        print("✅ Reddit API libraries installed")
    except ImportError as e:
        print(f"❌ Missing Reddit API library: {e}")
        return False
    
    # Test configuration
    if Path(".env").exists():
        print("✅ Environment configuration found")
    else:
        print("⚠️  No .env file found")
    
    # Test Node.js setup if available
    if check_node_installed() and Path("package.json").exists():
        print("✅ Node.js environment ready")
    
    return True

def display_next_steps():
    """Show user what to do next"""
    print("\n" + "="*60)
    print("🎉 Reddit Insight App Setup Complete!")
    print("="*60)
    
    print("\n📱 To start the app:")
    print("   Desktop App (Electron):")
    print("     npm run electron-dev")
    print("")
    print("   Web Version (React):")
    print("     npm start")
    print("")
    print("   Backend Only (Python):")
    print("     python main.py monitor")
    
    print("\n🔧 Available commands:")
    print("   python main.py test          # Test Reddit API connection")
    print("   python main.py insights      # Show current insights")
    print("   python launch_gui.py         # Launch GUI selector")
    
    print("\n📚 Key Features:")
    print("   ✨ Modern swipe-based interface")
    print("   🤖 AI-powered content summarization")
    print("   📊 Visual data insights and charts")
    print("   🎯 Personalized content recommendations")
    print("   📱 Cross-platform desktop app")
    
    print("\n🛠️  Configuration:")
    print("   • Edit .env for Reddit API credentials")
    print("   • Edit config.json for subreddit preferences")
    print("   • Add OPENAI_API_KEY to .env for enhanced AI features")
    
    print("\n💡 Demo Mode:")
    print("   The app starts with mock data for immediate testing.")
    print("   Configure Reddit API credentials for real data.")
    
    print("\n🚀 Ready to discover Reddit insights!")

def main():
    """Main setup process"""
    print("🚀 Setting up Reddit Insight App...")
    print("Modern, AI-powered Reddit content discovery")
    print("")
    
    # Validate Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    setup_project_structure()
    
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    setup_env_file()
    create_demo_data()
    
    if not run_tests():
        print("⚠️  Some validation tests failed, but setup may still work")
    
    display_next_steps()

if __name__ == "__main__":
    main()