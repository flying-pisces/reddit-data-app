#!/bin/bash
# Launch Reddit Data Engine Web Dashboard

echo "🌐 Launching Reddit Data Engine Web Dashboard..."
echo "============================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Navigate to the GUI directory
cd "$(dirname "$0")"

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Flask is not installed. Installing requirements..."
    pip install -r requirements.txt
fi

# Launch the web dashboard
echo "✅ Starting Web Dashboard..."
echo "📱 Open your browser and navigate to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python3 web_app/app.py