#!/usr/bin/env python3
"""
Reddit Data Engine - GUI Launcher
Simple launcher to choose between Desktop and Web interfaces
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("🚀 Reddit Data Engine - GUI Launcher")
    print("="*60)
    print()

def check_requirements():
    """Check if basic requirements are met"""
    # Check for Reddit credentials
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("   Run 'python setup_reddit_api.py' to configure Reddit API")
        print()
    
    # Check for exports directory
    Path('exports').mkdir(exist_ok=True)

def launch_desktop():
    """Launch the desktop GUI"""
    print("🖥️  Launching Desktop GUI...")
    print("-" * 40)
    
    try:
        # Navigate to GUI directory and launch
        gui_path = Path(__file__).parent / 'gui' / 'tkinter_app' / 'reddit_monitor_gui.py'
        
        if gui_path.exists():
            subprocess.run([sys.executable, str(gui_path)])
        else:
            # Try alternate path
            gui_path = Path(__file__).parent / 'GUI' / 'tkinter_app' / 'reddit_monitor_gui.py'
            if gui_path.exists():
                subprocess.run([sys.executable, str(gui_path)])
            else:
                print("❌ Desktop GUI not found")
                print("   Expected at: gui/tkinter_app/reddit_monitor_gui.py")
    
    except KeyboardInterrupt:
        print("\n✅ Desktop GUI closed")
    except Exception as e:
        print(f"❌ Error launching desktop GUI: {e}")

def launch_web():
    """Launch the web dashboard"""
    print("🌐 Launching Web Dashboard...")
    print("-" * 40)
    print("📱 Opening at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        # Navigate to GUI directory and launch
        app_path = Path(__file__).parent / 'gui' / 'web_app' / 'app.py'
        
        if app_path.exists():
            subprocess.run([sys.executable, str(app_path)])
        else:
            # Try alternate path
            app_path = Path(__file__).parent / 'GUI' / 'web_app' / 'app.py'
            if app_path.exists():
                subprocess.run([sys.executable, str(app_path)])
            else:
                print("❌ Web dashboard not found")
                print("   Expected at: gui/web_app/app.py")
    
    except KeyboardInterrupt:
        print("\n✅ Web server stopped")
    except Exception as e:
        print(f"❌ Error launching web dashboard: {e}")

def main():
    """Main launcher menu"""
    print_header()
    check_requirements()
    
    print("Choose your interface:")
    print()
    print("  1️⃣  Desktop GUI (Tkinter)")
    print("      • Native desktop application")
    print("      • Real-time monitoring")
    print("      • Dark theme interface")
    print()
    print("  2️⃣  Web Dashboard (Browser)")
    print("      • Access from any browser")
    print("      • Interactive charts")
    print("      • REST API endpoints")
    print()
    print("  3️⃣  Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            launch_desktop()
            break
        elif choice == '2':
            launch_web()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Launcher closed")