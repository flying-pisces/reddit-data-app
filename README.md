# Reddit Data Engine 🚀

A fast, real-time Reddit data collection and analysis engine specifically designed for monitoring popular investment and trading subreddits. Extract market sentiment, trending tickers, and speculative trading signals from Reddit's most active financial communities.

## Features

- **Real-time Monitoring**: Continuously monitors 13+ investment subreddits
- **Speculative Signal Detection**: Automatically identifies YOLO trades and meme stock activity  
- **Ticker Extraction**: Extracts and ranks trending stock symbols ($AAPL, $TSLA, etc.)
- **Sentiment Analysis**: Analyzes bullish/bearish sentiment across posts
- **Priority Post Detection**: Identifies high-engagement, trending posts
- **Export Interface**: JSON data export for integration with upper-level analysis systems
- **Async Architecture**: High-performance concurrent monitoring using Python asyncio

## Monitored Subreddits

| Category | Subreddits | Focus |
|----------|------------|--------|
| **YOLO/Meme** | r/wallstreetbets | High-risk speculation, meme stocks |
| **Serious Investing** | r/stocks, r/investing | Fundamental analysis, long-term strategy |
| **Speculative** | r/pennystocks | Penny stock trading |
| **Value Investing** | r/UndervaluedStonks, r/ValueInvesting | Value-oriented picks |
| **Options Trading** | r/options | Options strategies and analysis |
| **Day Trading** | r/trading, r/technicalanalysis, r/daytrading | Technical analysis, short-term trading |
| **Sector Specific** | r/stockmarket, r/biotech_stocks, r/SecurityAnalysis | Sector news and analysis |

## Quick Start

### 1. Installation

```bash
git clone https://github.com/yourusername/reddit-data
cd reddit-data
pip install -r requirements.txt
```

### 2. Reddit API Setup

1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Copy `.env.example` to `.env`
3. Fill in your Reddit API credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Test Connection

```bash
python main.py test
```

### 4. Start Real-time Monitoring

```bash
python main.py monitor
```

## Usage

### Command Line Interface

```bash
# Start real-time monitoring
python main.py monitor

# Test Reddit API connection
python main.py test  

# Get current market insights
python main.py insights

# Export custom data
python main.py export --subreddits stocks investing wallstreetbets --hours 12
```

### Programmatic Usage

```python
from api_interface import get_reddit_insights, AnalysisAPI

# Quick insights
insights = await get_reddit_insights()
print(insights['trending_tickers'])

# Advanced API
api = AnalysisAPI()
hot_tickers = await api.get_trending_tickers(limit=10)
speculative_signals = await api.get_speculative_signals()
```

## Data Export Format

The engine exports data in JSON format suitable for analysis systems:

```json
{
  "metadata": {
    "timestamp": "2025-01-01T12:00:00",
    "total_posts": 1250,
    "data_window_hours": 24
  },
  "trending_tickers": {
    "AAPL": 45,
    "TSLA": 32,
    "GME": 28
  },
  "subreddit_insights": {
    "wallstreetbets": {
      "total_posts": 156,
      "speculative_ratio": 0.65,
      "avg_score": 234.5
    }
  },
  "recent_priority_posts": [...],
  "sentiment_analysis": {
    "average": 0.15,
    "mood": "bullish",
    "positive": 450,
    "negative": 200
  }
}
```

## Key Components

### RedditClient (`reddit_client.py`)
- Synchronous and asynchronous Reddit API clients
- Rate-limit aware with automatic retry
- Structured post data extraction

### Monitor (`monitor.py`)  
- Real-time monitoring system
- Concurrent subreddit polling
- Graceful shutdown handling
- Statistics reporting

### DataProcessor (`data_processor.py`)
- Post filtering and analysis
- Ticker extraction using regex
- Sentiment scoring
- Speculative content detection

### API Interface (`api_interface.py`)
- Export interface for external systems
- Real-time data feeds
- Custom data queries
- Simplified API for common tasks

## Configuration

Edit `config.py` to customize:

- **Subreddit lists**: Add/remove monitored subreddits
- **Monitoring intervals**: Adjust polling frequency  
- **Filtering criteria**: Minimum score/comments thresholds
- **Speculative keywords**: Keywords for detecting YOLO content
- **Export settings**: Data retention and export intervals

## Performance

- **Concurrent monitoring** of all subreddits using asyncio
- **Memory efficient** with configurable data retention
- **Rate limit compliant** with Reddit API guidelines
- **Handles 1000+ posts/hour** typical throughput

## Integration Examples

### Alert System
```python
from api_interface import SimpleAPI

api = SimpleAPI()
alerts = await api.alert_check()

if alerts['alert_count'] > 0:
    for alert in alerts['alerts']:
        print(f"🚨 {alert['message']}")
```

### Trading Bot Integration
```python
# Get hot tickers for analysis
hot_tickers = await api.get_hot_tickers(limit=5)
# ['AAPL', 'TSLA', 'NVDA', 'GME', 'AMC']

# Check WSB activity level  
yolo_activity = await api.get_yolo_activity()
# {'recent_posts': 45, 'speculative_ratio': 67}
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reddit API    │◄───│  RedditClient    │◄───│    Monitor      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  DataProcessor   │◄───│  Post Buffer    │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  API Interface   │───►│  JSON Export    │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Analysis Engine  │ (External)
                       └──────────────────┘
```

## Support the Project ❤️

If you find this Reddit Data Engine useful, please consider supporting its development:

### 💰 Donations
- **PayPal**: [paypal.me/redditdataengine](https://paypal.me/redditdataengine)
- **GitHub Sponsors**: [Sponsor this project](https://github.com/sponsors/yourusername)
- **Buy Me a Coffee**: [buymeacoffee.com/redditengine](https://buymeacoffee.com/redditengine)

### 🌟 Other Ways to Support
- ⭐ Star this repository on GitHub
- 🐛 Report bugs and suggest features  
- 📖 Improve documentation
- 🔄 Share with other developers

Your support helps maintain and improve this open-source project!

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## Testing

Run the automated test suite:

```bash
cd tests
python -m pytest test_all.py -v
python test_integration.py
```

See the `tests/` folder for comprehensive test coverage including unit tests, integration tests, and performance benchmarks.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Always comply with Reddit's API terms of service and rate limits. Not financial advice.