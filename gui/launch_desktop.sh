#!/bin/bash
# Launch Reddit Data Engine Desktop GUI

echo "🚀 Launching Reddit Data Engine Desktop GUI..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Navigate to the GUI directory
cd "$(dirname "$0")"

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter is not installed"
    echo "Please install tkinter:"
    echo "  macOS: tkinter comes with Python"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    exit 1
fi

# Launch the desktop GUI
echo "✅ Starting Desktop GUI..."
python3 tkinter_app/reddit_monitor_gui.py

echo "GUI closed."