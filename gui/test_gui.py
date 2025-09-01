#!/usr/bin/env python3
"""Test script to verify GUI components are working"""

import sys
import os

def test_tkinter():
    """Test if Tkinter GUI can be imported"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        
        # Try to import the desktop GUI
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from tkinter_app.reddit_monitor_gui import RedditMonitorGUI
        print("✅ Desktop GUI module loads successfully")
        return True
    except ImportError as e:
        print(f"❌ Tkinter GUI error: {e}")
        return False

def test_flask():
    """Test if Flask web app can be imported"""
    try:
        import flask
        print("✅ Flask is available")
        
        # Try to import the web app
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from web_app.app import app
        print("✅ Web Dashboard module loads successfully")
        return True
    except ImportError as e:
        print(f"❌ Flask web app error: {e}")
        return False

def main():
    print("=" * 60)
    print("Reddit Data Engine - GUI Test")
    print("=" * 60)
    
    print("\n1. Testing Desktop GUI (Tkinter)...")
    tkinter_ok = test_tkinter()
    
    print("\n2. Testing Web Dashboard (Flask)...")
    flask_ok = test_flask()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    if tkinter_ok and flask_ok:
        print("🎉 All GUI components are ready!")
        print("\nTo launch:")
        print("  Desktop GUI: ./launch_desktop.sh")
        print("  Web Dashboard: ./launch_web.sh")
    elif tkinter_ok:
        print("✅ Desktop GUI is ready")
        print("⚠️  Web Dashboard needs Flask: pip install flask flask-cors")
    elif flask_ok:
        print("✅ Web Dashboard is ready")
        print("⚠️  Desktop GUI needs tkinter")
    else:
        print("❌ Both GUIs need dependencies installed")
        print("Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()