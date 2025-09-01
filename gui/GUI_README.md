# Reddit Data Engine - GUI Applications

This folder contains two intuitive GUI interfaces for the Reddit Data Engine:

1. **Desktop GUI** (Tkinter-based) - Native desktop application
2. **Web Dashboard** (Flask-based) - Browser-based interface

## 🖥️ Desktop GUI (Tkinter)

A modern, dark-themed desktop application with real-time monitoring capabilities.

### Features
- ✅ Real-time Reddit post monitoring
- 📊 Live statistics and charts
- 💹 Trending ticker analysis
- 💡 Market insights generation
- 📤 Data export functionality
- ⚙️ Customizable settings

### Launch
```bash
./launch_desktop.sh
# or
python tkinter_app/reddit_monitor_gui.py
```

### Screenshots
- **Main Dashboard**: Live feed of Reddit posts with statistics
- **Tickers Tab**: Track trending stock symbols
- **Insights Tab**: Generate market analysis
- **Export Tab**: Export data to JSON
- **Settings Tab**: Configure monitoring parameters

## 🌐 Web Dashboard (Flask)

A responsive web-based dashboard accessible from any browser.

### Features
- 🚀 Real-time monitoring with WebSocket updates
- 📈 Interactive charts (Chart.js)
- 🎯 Filter posts by subreddit
- 💾 Export data via REST API
- 📱 Mobile-responsive design
- 🌙 Dark theme

### Launch
```bash
./launch_web.sh
# or
python web_app/app.py
```

Then open your browser to: **http://localhost:5000**

### API Endpoints
- `GET /` - Main dashboard
- `GET /api/status` - Current monitoring status
- `GET /api/posts` - Recent posts
- `GET /api/tickers` - Trending tickers
- `GET /api/insights` - Market insights
- `POST /api/start_monitoring` - Start monitoring
- `POST /api/stop_monitoring` - Stop monitoring
- `POST /api/export` - Export data

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Choose Your Interface

#### Option A: Desktop GUI
Perfect for single-user monitoring on your local machine.
```bash
./launch_desktop.sh
```

#### Option B: Web Dashboard
Ideal for remote access or multi-user scenarios.
```bash
./launch_web.sh
```

## 🎮 User Guide

### Desktop GUI Controls

1. **Start Monitoring**
   - Click the green "▶ Start Monitoring" button
   - Posts will begin appearing in the live feed
   - Statistics update automatically

2. **View Tickers**
   - Switch to the "💹 Tickers" tab
   - See trending stock symbols with mention counts
   - Color-coded sentiment indicators

3. **Generate Insights**
   - Go to "💡 Insights" tab
   - Click "Generate Insights"
   - View AI-powered market analysis

4. **Export Data**
   - Navigate to "📤 Export" tab
   - Select subreddits and time range
   - Click "Export to JSON"

### Web Dashboard Controls

1. **Start Monitoring**
   - Click "▶ Start Monitoring" in the header
   - Real-time updates begin automatically
   - Connection status shows green

2. **Filter Posts**
   - Use the dropdown to filter by subreddit
   - Posts update instantly

3. **View Charts**
   - Activity chart shows posts per minute
   - Top tickers bar chart updates live

4. **Export Data**
   - Go to Export tab
   - Configure parameters
   - Download JSON file

## 📊 Data Visualization

Both interfaces provide:
- **Real-time post feed** with scores and comments
- **Trending tickers** with mention frequency
- **Market sentiment** analysis
- **Activity charts** showing posting patterns
- **Statistics cards** for quick metrics

## ⚙️ Configuration

### Desktop GUI Settings
- Refresh interval: 10-300 seconds
- Max posts per subreddit: 5-50
- Custom subreddit lists
- Save settings for persistence

### Web Dashboard Settings
- API-based configuration
- Adjustable monitoring parameters
- Custom subreddit selection
- Export format options

## 🔧 Troubleshooting

### Desktop GUI Issues

**"tkinter not found"**
- macOS: Comes with Python
- Linux: `sudo apt install python3-tk`
- Windows: Reinstall Python with tkinter

**"Cannot connect to Reddit"**
- Check `.env` file has valid credentials
- Verify internet connection
- Run `python main.py test` to verify API

### Web Dashboard Issues

**"Port 5000 already in use"**
- Change port in `app.py`
- Or kill existing process: `lsof -i :5000`

**"Module not found"**
- Install requirements: `pip install -r requirements.txt`
- Check virtual environment activation

## 🎨 Customization

### Themes
Both GUIs use a dark theme by default. To customize:

**Desktop GUI**: Edit colors dictionary in `reddit_monitor_gui.py`
```python
self.colors = {
    'bg': '#1e1e1e',      # Background
    'accent': '#007acc',   # Primary accent
    ...
}
```

**Web Dashboard**: Modify CSS variables in `style.css`
```css
:root {
    --bg-primary: #1e1e1e;
    --accent: #007acc;
    ...
}
```

## 📝 Development

### Adding New Features

1. **Desktop GUI**: Extend `RedditMonitorGUI` class
2. **Web Dashboard**: Add new routes in `app.py`
3. **Both**: Update data processing in respective files

### API Integration
Both GUIs use the same Reddit client from the parent directory.
Ensure parent directory is in Python path.

## 🚨 Important Notes

- Both GUIs require valid Reddit API credentials
- Run `python setup_reddit_api.py` from parent directory first
- Monitor responsibly - respect Reddit's rate limits
- Data is stored locally in `exports/` directory

## 📜 License

Part of the Reddit Data Engine project. See main LICENSE file.

---

**Enjoy monitoring Reddit with these intuitive interfaces!** 🎉