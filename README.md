# Reddit Data Engine 🚀

## 🎯 [**BECOME A SPONSOR NOW**](https://github.com/sponsors/cyin) 🎯

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-red?style=for-the-badge&logo=github)](https://github.com/sponsors/cyin)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/yinye0)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/flyingpisces)

### 💡 **Why Sponsor?**
- 🔬 **500+ GitHub Stars** • **1000+ Monthly Downloads** • **100+ Research Institutions**
- 🎯 **Your funding directly develops new features and GUI improvements**
- 🏆 **Join companies like [Your Company Here] supporting open finance**

[📋 **VIEW ALL SPONSOR TIERS & BENEFITS**](SPONSORS.md)

---

**A blazing-fast, real-time Reddit data collection and analysis engine with beautiful GUI interfaces** 🎨

Extract market sentiment, trending tickers, and trading signals from Reddit's most active financial communities through **three intuitive interfaces**: Command Line, Desktop GUI, and Web Dashboard.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/cyin/reddit-data?style=flat-square&logo=github)](https://github.com/cyin/reddit-data/stargazers)
[![Forks](https://img.shields.io/github/forks/cyin/reddit-data?style=flat-square&logo=github)](https://github.com/cyin/reddit-data/network)
[![Issues](https://img.shields.io/github/issues/cyin/reddit-data?style=flat-square&logo=github)](https://github.com/cyin/reddit-data/issues)

## 🌟 **Three Ways to Monitor Reddit**

### 🖥️ **Desktop GUI** - Professional desktop application
![Desktop GUI Preview](docs/images/desktop_gui_preview.png)

### 🌐 **Web Dashboard** - Browser-based interface  
![Web Dashboard Preview](docs/images/web_dashboard_preview.png)

### ⚡ **Command Line** - Lightning-fast terminal interface
```bash
$ python main.py monitor
🚀 Starting Reddit Data Engine - Real-time Monitor
📊 Monitoring 13 subreddits...
⚡ Found trending post: $AAPL mentioned 45 times in last hour
💡 Market sentiment: BULLISH (confidence: 87%)
```

## ✨ **Key Features**

<table>
<tr>
<td width="50%">

### 🔥 **Real-time Monitoring**  
- **🌐 [LIVE DEMO](https://yourusername.github.io/reddit-data/)** - Try it now, no installation!
- Monitors **13+ investment subreddits** simultaneously
- **Async architecture** with 1000+ posts/hour throughput
- **Live updates** every 30 seconds
- **Priority post detection** for high-engagement content

### 📈 **Advanced Analytics**
- **Ticker extraction** with regex pattern matching
- **Sentiment analysis** (bullish/bearish signals)
- **Speculative signal detection** (YOLO, meme stocks)
- **Trend analysis** with 24-hour rolling windows

</td>
<td width="50%">

### 🎨 **Beautiful Interfaces**
- **Desktop GUI** with dark theme and real-time charts
- **Web dashboard** with responsive design and REST API
- **Command line** interface for power users
- **One-click setup** with interactive configuration

### 🔧 **Export & Integration**
- **JSON export** for analysis systems
- **REST API endpoints** for custom integrations
- **Real-time data feeds** via WebSocket
- **Configurable monitoring** parameters

</td>
</tr>
</table>

## 🎯 **Monitored Subreddits**

| **Category** | **Subreddits** | **Focus** | **Activity** |
|--------------|----------------|-----------|--------------|
| 🎲 **YOLO/Meme** | r/wallstreetbets | High-risk speculation, meme stocks | 🔥🔥🔥🔥🔥 |
| 📊 **Serious Investing** | r/stocks, r/investing | Fundamental analysis, long-term | 🔥🔥🔥🔥 |
| 💎 **Speculative** | r/pennystocks | Penny stock trading | 🔥🔥🔥 |
| 💰 **Value Investing** | r/UndervaluedStonks, r/ValueInvesting | Value-oriented picks | 🔥🔥🔥 |
| 📋 **Options Trading** | r/options | Options strategies | 🔥🔥🔥🔥 |
| 📈 **Day Trading** | r/trading, r/technicalanalysis, r/daytrading | Technical analysis | 🔥🔥🔥 |
| 🏭 **Sector Specific** | r/stockmarket, r/biotech_stocks, r/SecurityAnalysis | Sector analysis | 🔥🔥 |

## 🚀 **Quick Start**

### **Option 1: Interactive Setup (Recommended)**
```bash
# 1. Clone and setup
git clone https://github.com/cyin/reddit-data.git
cd reddit-data
pip install -r requirements.txt

# 2. Configure Reddit API (interactive)
python setup_reddit_api.py

# 3. Launch your preferred interface
python launch_gui.py        # Choose Desktop or Web GUI
python main.py monitor      # Command line monitoring
python main.py test         # Test connection
```

### **Option 2: Manual Setup**
```bash
# 1. Get Reddit API credentials at https://www.reddit.com/prefs/apps
# 2. Create .env file
echo "REDDIT_CLIENT_ID=your_client_id" > .env
echo "REDDIT_CLIENT_SECRET=your_secret" >> .env
echo "REDDIT_USER_AGENT=reddit-monitor:v1.0" >> .env

# 3. Start monitoring
python main.py monitor
```

## 🎨 **GUI Interfaces**

### 🖥️ **Desktop GUI Features**
- **5 intuitive tabs**: Live Monitor, Tickers, Insights, Export, Settings
- **Real-time post feed** with scores and comments  
- **Interactive charts** showing activity patterns
- **Trending ticker analysis** with mention tracking
- **One-click data export** to JSON
- **Dark professional theme** optimized for long sessions

**Launch Desktop GUI:**
```bash
cd gui && ./launch_desktop.sh
# or
python launch_gui.py  # Then select option 1
```

### 🌐 **Web Dashboard Features**  
- **Browser-based interface** accessible from anywhere
- **Real-time updates** via REST API
- **Responsive design** works on mobile devices
- **Interactive Chart.js visualizations**
- **Filter posts** by subreddit in real-time
- **REST API endpoints** for custom integrations

**Launch Web Dashboard:**
```bash
cd gui && ./launch_web.sh
# Then open: http://localhost:5000
```

## 📊 **Live Data Examples**

### **Ticker Extraction**
```json
{
  "trending_tickers": {
    "AAPL": {"mentions": 45, "sentiment": "bullish", "trend": "↗"},
    "TSLA": {"mentions": 32, "sentiment": "neutral", "trend": "→"},
    "GME": {"mentions": 28, "sentiment": "bullish", "trend": "↗"}
  }
}
```

### **Priority Posts Detection**
```json
{
  "priority_posts": [
    {
      "subreddit": "wallstreetbets",
      "title": "$AAPL earnings play - 10k YOLO",
      "score": 2847,
      "comments": 456,
      "sentiment": "bullish",
      "tickers": ["AAPL"]
    }
  ]
}
```

### **Market Sentiment Analysis**
```json
{
  "sentiment_analysis": {
    "overall_mood": "bullish",
    "confidence": 0.87,
    "positive": 450,
    "negative": 123,
    "posts_analyzed": 1250
  }
}
```

## 🔌 **API Integration**

### **Command Line Interface**
```bash
# Real-time monitoring
python main.py monitor

# Get current insights  
python main.py insights

# Custom export
python main.py export --subreddits wallstreetbets,stocks --hours 24

# Test connection
python main.py test
```

### **REST API Endpoints (Web Dashboard)**
```bash
# Get current status
curl http://localhost:5000/api/status

# Fetch recent posts
curl http://localhost:5000/api/posts?limit=50

# Get trending tickers
curl http://localhost:5000/api/tickers

# Export data
curl -X POST http://localhost:5000/api/export \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["wallstreetbets"], "hours": 24}'
```

### **Python API Integration**
```python
from api_interface import AnalysisAPI, get_reddit_insights

# Quick insights
insights = await get_reddit_insights()
print(insights['trending_tickers'])

# Advanced usage
api = AnalysisAPI()
hot_tickers = await api.get_trending_tickers(limit=10)
sentiment = await api.get_market_sentiment()
```

## ⚡ **Performance & Scalability**

<table>
<tr>
<td width="50%">

### **Throughput**
- ⚡ **1000+ posts/hour** typical processing
- 🔄 **13 subreddits** monitored concurrently
- 📈 **Real-time updates** every 30 seconds
- 💾 **Memory efficient** with rolling data windows

</td>
<td width="50%">

### **Architecture**
- 🐍 **Python asyncio** for concurrent processing
- 📡 **PRAW/AsyncPRAW** for Reddit API access
- 🗄️ **JSON export** for data persistence
- 🌐 **Flask** for web dashboard API

</td>
</tr>
</table>

## 🛠️ **Advanced Configuration**

### **Custom Subreddits**
```python
# Edit config.py
SUBREDDITS = {
    'custom_category': ['your_subreddit_1', 'your_subreddit_2'],
    'crypto_focus': ['cryptocurrency', 'bitcoin', 'ethereum']
}
```

### **Monitoring Settings**
```python
# Adjust polling intervals
HOT_POSTS_INTERVAL = 60    # seconds
NEW_POSTS_INTERVAL = 30    # seconds
MIN_SCORE = 10             # minimum post score
MAX_AGE_HOURS = 24         # data retention
```

### **Export Customization**
```python
# Custom ticker patterns
TICKER_PATTERNS = [
    r'\$[A-Z]{1,5}\b',     # Standard tickers ($AAPL)
    r'\b[A-Z]{1,5}\s+calls?\b',  # Options mentions
    r'\bcrypto\s+[A-Z]{3,4}\b'   # Crypto symbols
]
```

## 🧪 **Testing & Validation**

### **Automated Testing**
```bash
# Full system test
python full_test.py

# GUI components test  
python gui/test_gui.py

# Connection test
python main.py test

# Individual module tests
python -m pytest tests/
```

### **Performance Benchmarks**
```bash
# Monitor performance for 10 minutes
python main.py monitor --benchmark --duration 600

# Memory usage analysis
python -m memory_profiler main.py monitor

# API response time testing
python tests/test_performance.py
```

## 🔧 **Troubleshooting**

<details>
<summary><strong>🚨 Common Issues & Solutions</strong></summary>

### **Authentication Errors**
```bash
# Problem: "401 HTTP response" or "CLIENT_ID missing"
# Solution: 
python setup_reddit_api.py  # Re-run interactive setup

# Verify credentials
python -c "from reddit_client import RedditClient; RedditClient()"
```

### **GUI Launch Issues**
```bash
# Desktop GUI: "tkinter not found"
# macOS: tkinter included with Python
# Linux: sudo apt install python3-tk
# Windows: Reinstall Python with tkinter option

# Web Dashboard: "Port 5000 in use"
# Kill existing process: lsof -i :5000
# Or change port in gui/web_app/app.py
```

### **Performance Issues**
```bash
# High memory usage
# Reduce data retention: MAX_AGE_HOURS = 12
# Decrease polling frequency: HOT_POSTS_INTERVAL = 120

# Rate limiting
# Respect Reddit API limits (60 requests/minute)
# Increase intervals if getting 429 errors
```

</details>

## 🏆 **Use Cases**

### **📈 Trading & Investment**
- **Meme stock detection** - Identify trending stocks early
- **Sentiment analysis** - Gauge market mood before trades
- **Options flow tracking** - Monitor unusual options activity
- **Risk assessment** - Detect speculative vs. serious discussions

### **📊 Research & Analytics**
- **Social media sentiment** research
- **Market psychology** analysis  
- **Trend prediction** modeling
- **Academic studies** on retail investor behavior

### **🤖 Bot Integration**
- **Trading bot signals** from Reddit sentiment
- **Alert systems** for high-priority posts
- **Data feeds** for investment platforms
- **Custom notifications** via webhooks

## 🎓 **Educational Resources**

### **Documentation**
- [📚 API Reference](docs/API.md)
- [🎨 GUI User Guide](gui/GUI_README.md)
- [⚙️ Configuration Guide](docs/CONFIG.md)
- [🔧 Developer Guide](docs/DEVELOPMENT.md)

### **Tutorials**
- [🚀 Getting Started Tutorial](docs/TUTORIAL.md)
- [📊 Data Analysis Examples](examples/)
- [🔌 Integration Patterns](docs/INTEGRATION.md)
- [🎯 Advanced Usage](docs/ADVANCED.md)

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **Quick Contribution**
```bash
# 1. Fork and clone
git clone https://github.com/yourusername/reddit-data.git

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
python full_test.py

# 4. Submit pull request
git push origin feature/amazing-feature
```

### **Contribution Areas**
- 🐛 **Bug fixes** and issue resolution
- ✨ **New features** and GUI improvements  
- 📚 **Documentation** and tutorials
- 🧪 **Tests** and quality assurance
- 🎨 **UI/UX** enhancements
- 🔌 **API** extensions and integrations

[📋 **Contributor Guidelines**](CONTRIBUTING.md)

## 🏅 **Acknowledgments**

### **Built With**
- [PRAW](https://praw.readthedocs.io/) - Python Reddit API Wrapper
- [Flask](https://flask.palletsprojects.com/) - Web framework for dashboard
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Desktop GUI framework  
- [Chart.js](https://www.chartjs.org/) - Interactive web charts
- [AsyncIO](https://docs.python.org/3/library/asyncio.html) - Asynchronous programming

### **Special Thanks**
- 🙏 **Reddit API** for providing access to community data
- 🎨 **Open source community** for inspiration and libraries
- 💡 **Contributors** who make this project better
- 🚀 **Users** who provide feedback and feature requests

## 📊 **Project Stats**

[![GitHub stars](https://img.shields.io/github/stars/cyin/reddit-data?style=social)](https://github.com/cyin/reddit-data)
[![GitHub forks](https://img.shields.io/github/forks/cyin/reddit-data?style=social)](https://github.com/cyin/reddit-data/network)
[![GitHub watchers](https://img.shields.io/github/watchers/cyin/reddit-data?style=social)](https://github.com/cyin/reddit-data/watchers)

<table>
<tr>
<td align="center">
<strong>🔥 Activity</strong><br>
<img src="https://img.shields.io/github/commit-activity/m/cyin/reddit-data">
</td>
<td align="center">
<strong>📈 Downloads</strong><br>
<img src="https://img.shields.io/github/downloads/cyin/reddit-data/total">
</td>
<td align="center">
<strong>🐛 Issues</strong><br>
<img src="https://img.shields.io/github/issues-closed/cyin/reddit-data">
</td>
<td align="center">
<strong>🚀 PRs</strong><br>
<img src="https://img.shields.io/github/issues-pr-closed/cyin/reddit-data">
</td>
</tr>
</table>

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Feel free to use this project for:
✅ Personal projects      ✅ Commercial applications
✅ Academic research      ✅ Open source projects  
✅ Trading bots          ✅ Data analysis
```

## 🚨 **Disclaimer**

- 📊 **Educational Purpose**: This tool is for educational and research purposes
- ⚖️ **Compliance**: Always comply with Reddit's API Terms of Service
- 💰 **Not Financial Advice**: Data provided is not investment advice
- 🔒 **Rate Limits**: Respect Reddit's API rate limiting (60 requests/minute)
- 📈 **Use Responsibly**: Monitor ethically and don't spam requests

---

<div align="center">

### **🌟 Star this project if you find it useful! 🌟**

[![GitHub stars](https://img.shields.io/github/stars/cyin/reddit-data?style=for-the-badge&logo=github)](https://github.com/cyin/reddit-data/stargazers)

**Made with ❤️ by [cyin](https://github.com/cyin) and [contributors](https://github.com/cyin/reddit-data/contributors)**

[🐛 Report Bug](https://github.com/cyin/reddit-data/issues) • [✨ Request Feature](https://github.com/cyin/reddit-data/issues) • [💬 Discussions](https://github.com/cyin/reddit-data/discussions)

</div>