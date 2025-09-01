# Reddit Data Engine - GUI Interfaces 🖥️

Two graphical user interfaces for the Reddit Data Engine: a desktop Tkinter application and a web-based dashboard.

## Available GUIs

### 1. Tkinter Desktop GUI (`tkinter_gui.py`)
Native desktop application with real-time monitoring dashboard.

**Features:**
- 📊 Live data monitoring with automatic updates
- 📈 Trending tickers display with rankings
- 💭 Market sentiment analysis dashboard  
- ⚡ Priority posts browser with filtering
- ⚙️ Configuration settings panel
- 📤 Data export functionality
- 🚨 Real-time alerts system

### 2. Web-Based GUI (`web_gui.py`)
Modern web dashboard with WebSocket real-time updates.

**Features:**
- 🌐 Browser-based interface (works on any device)
- 🔄 Real-time WebSocket data updates
- 📱 Responsive design for mobile/tablet
- 📊 Interactive charts and visualizations
- 🔗 Clickable post links to Reddit
- 📥 JSON data export functionality
- 🎨 Modern Bootstrap UI

## Quick Start

### Prerequisites
```bash
# Install GUI dependencies
pip install -r requirements-gui.txt
```

### Desktop GUI (Tkinter)
```bash
cd gui
python tkinter_gui.py
```

### Web GUI (Flask)
```bash
cd gui  
python web_gui.py
```
Then open http://localhost:5000 in your browser.

## Desktop GUI (Tkinter)

### Interface Overview

**Main Tabs:**
1. **Overview** - Key metrics and market mood
2. **Trending Tickers** - Most mentioned stock symbols
3. **Sentiment** - Market sentiment analysis
4. **Priority Posts** - High-engagement posts
5. **Settings** - Configuration options

**Control Buttons:**
- **Start Monitoring** - Begin real-time data collection
- **Stop Monitoring** - Pause monitoring
- **Refresh Now** - Manual data update
- **Export Data** - Save current data to JSON

### Key Features

**Real-Time Updates:**
- Configurable update intervals (default: 30 seconds)
- Background threading for smooth UI performance
- Automatic error handling and retry logic

**Data Visualization:**
- Color-coded sentiment indicators
- Ranked ticker displays with mention counts
- Categorized subreddit activity metrics
- Filterable priority posts by category

**Export Functionality:**
- JSON export with timestamp
- Configurable data retention periods
- Load previously exported data

### Usage Example
```python
from tkinter_gui import RedditDataGUI

app = RedditDataGUI()
app.run()
```

## Web GUI (Flask)

### Interface Overview

**Dashboard Sections:**
- **Header** - Status indicator and control buttons  
- **Key Metrics** - Market mood, post counts, activity levels
- **Tabbed Content** - Tickers, sentiment, posts, subreddits
- **Real-Time Status** - Last updated timestamp

**WebSocket Features:**
- Instant data updates without page refresh
- Live monitoring status indicators
- Real-time error notifications
- Automatic reconnection handling

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/status` | GET | Current monitoring status |
| `/api/data` | GET | Current Reddit data |
| `/api/start_monitoring` | POST | Start monitoring |
| `/api/stop_monitoring` | POST | Stop monitoring |
| `/api/export` | GET | Export data as JSON |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client→Server | Client connection |
| `data_update` | Server→Client | Real-time data push |
| `monitoring_status` | Server→Client | Monitoring state change |
| `request_refresh` | Client→Server | Manual refresh request |
| `error` | Server→Client | Error notifications |

### Usage Example
```python
from web_gui import WebGUIServer

server = WebGUIServer(host='0.0.0.0', port=5000)
server.run(debug=False)
```

## Configuration

### Tkinter GUI Settings
- **Update Interval** - Frequency of data refreshes
- **Subreddit Selection** - Choose which subreddits to monitor
- **Filtering Criteria** - Minimum scores and engagement thresholds

### Web GUI Settings
- **Host/Port** - Server binding configuration
- **CORS Settings** - Cross-origin request handling
- **WebSocket Options** - Real-time connection settings

## Architecture

### Data Flow
```
Reddit API → API Interface → GUI Backend → UI Display
     ↓              ↓              ↓          ↑
Data Processing → WebSocket/Threading → Real-time Updates
```

### Threading Model

**Tkinter GUI:**
- Main thread for UI rendering
- Background thread for data fetching
- Queue-based communication for thread safety

**Web GUI:**
- Flask main thread for HTTP requests
- Background thread for monitoring loop
- WebSocket thread pool for client connections

## Customization

### Adding New Visualizations

**Tkinter:**
```python
def create_custom_tab(self):
    """Add new tab to notebook"""
    custom_frame = ttk.Frame(self.notebook)
    self.notebook.add(custom_frame, text="Custom")
    # Add widgets to custom_frame
```

**Web GUI:**
```javascript
// Add new chart or visualization
function updateCustomChart(data) {
    // Chart.js or custom visualization code
}
```

### Styling

**Tkinter:**
- TTK themes and styles
- Custom color schemes
- Font configurations

**Web GUI:**
- Bootstrap CSS framework
- Custom CSS modifications
- Responsive design patterns

## Performance Considerations

### Tkinter GUI
- **Memory Usage** - ~50-100MB typical
- **Update Frequency** - 30-60 second intervals recommended
- **Data Retention** - Configurable buffer sizes
- **Thread Pool** - Single background thread for data fetching

### Web GUI  
- **Memory Usage** - ~100-200MB with multiple clients
- **Concurrent Users** - 10-50 users supported
- **WebSocket Connections** - Automatic cleanup on disconnect
- **Data Broadcasting** - Efficient multi-client updates

## Deployment

### Local Development
```bash
# Tkinter (no additional setup required)
python tkinter_gui.py

# Web GUI
python web_gui.py
```

### Production Web Deployment
```bash
# Using Gunicorn with eventlet
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 web_gui:app --bind 0.0.0.0:5000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt -r gui/requirements-gui.txt
EXPOSE 5000
CMD ["python", "gui/web_gui.py"]
```

## Troubleshooting

### Common Issues

**Tkinter GUI:**
- **Import Errors** - Ensure tkinter is available (included with most Python installations)
- **Threading Issues** - Check that background threads are properly cleaned up
- **Memory Leaks** - Monitor data buffer sizes and cleanup intervals

**Web GUI:**
- **Port Conflicts** - Change port in `WebGUIServer(port=5001)`
- **WebSocket Issues** - Check firewall settings and browser compatibility
- **CORS Errors** - Configure `cors_allowed_origins` parameter

### Debug Mode
```bash
# Tkinter with debug logging
python tkinter_gui.py --debug

# Web GUI with Flask debug mode
python web_gui.py --debug
```

### Performance Monitoring
```python
# Add performance monitoring
import psutil
import time

def monitor_performance():
    process = psutil.Process()
    print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f}MB")
    print(f"CPU: {process.cpu_percent()}%")
```

## Integration with Main Engine

Both GUIs integrate seamlessly with the core Reddit Data Engine:

```python
# Import and use existing components
from api_interface import AnalysisAPI, SimpleAPI
from reddit_client import RedditClient
from config import MonitoringConfig

# GUIs use same data sources as CLI
api = AnalysisAPI()
tickers = await api.get_trending_tickers()
```

## Contributing

### Adding New Features
1. Follow existing code patterns and naming conventions
2. Add proper error handling and logging
3. Update both GUI versions when adding core features  
4. Test with various data scenarios and edge cases
5. Update this README with new functionality

### UI/UX Guidelines
- **Consistent Styling** - Follow existing color schemes and layouts
- **Responsive Design** - Test on different screen sizes (web GUI)
- **Accessibility** - Include proper labels and keyboard navigation
- **Performance** - Optimize for smooth real-time updates
- **Error Handling** - Provide clear feedback for errors and loading states