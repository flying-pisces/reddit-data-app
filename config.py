"""
Reddit Data Engine Configuration
"""
import os
import json
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Try to load from config.json first, fall back to environment variables
config_file = Path('config.json')
config_data = {}
if config_file.exists():
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
    except Exception:
        pass

class RedditConfig:
    """Reddit API configuration"""
    # Load from config.json first, then environment variables
    reddit_config = config_data.get('reddit', {})
    CLIENT_ID = reddit_config.get('client_id') or os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET = reddit_config.get('client_secret') or os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT = reddit_config.get('user_agent') or os.getenv('REDDIT_USER_AGENT', 'RedditDataEngine/1.0')
    USERNAME = reddit_config.get('username') or os.getenv('REDDIT_USERNAME')
    PASSWORD = reddit_config.get('password') or os.getenv('REDDIT_PASSWORD')

class MonitoringConfig:
    """Monitoring and data collection settings"""
    
    # Load monitoring settings from config.json if available
    monitoring_config = config_data.get('monitoring', {})
    
    # Target subreddits - can be overridden by config.json
    if 'subreddits' in monitoring_config:
        # Simple list from config.json
        ALL_SUBREDDITS = monitoring_config['subreddits']
        SUBREDDITS = {'general': ALL_SUBREDDITS}
    else:
        # Default categorized subreddits
        SUBREDDITS: Dict[str, List[str]] = {
            'yolo_meme': ['wallstreetbets'],
            'serious_investing': ['stocks', 'investing'],
            'speculative': ['pennystocks'],
            'value_oriented': ['UndervaluedStonks', 'ValueInvesting'],
            'options_focus': ['options'],
            'trading': ['trading', 'technicalanalysis', 'daytrading'],
            'sector_specific': ['stockmarket', 'biotech_stocks', 'SecurityAnalysis']
        }
        ALL_SUBREDDITS = [sub for subs in SUBREDDITS.values() for sub in subs]
    
    # Monitoring intervals (seconds)
    HOT_POSTS_INTERVAL = monitoring_config.get('refresh_interval', 60)
    NEW_POSTS_INTERVAL = 30
    RISING_POSTS_INTERVAL = 45
    
    # Post filtering criteria
    MIN_SCORE = 10
    MIN_COMMENTS = 5
    MAX_AGE_HOURS = 24
    
    # Keywords for speculative picks detection
    SPECULATIVE_KEYWORDS = [
        'yolo', 'moon', 'rocket', 'diamond hands', 'hodl', 'squeeze',
        'gamma', 'short interest', 'DD', 'due diligence', 'calls', 'puts'
    ]
    
    # High-priority detection patterns
    PRIORITY_PATTERNS = [
        r'\$[A-Z]{1,5}\b',  # Stock tickers like $AAPL
        r'\b[A-Z]{1,5}\s+(calls?|puts?)\b',  # Options mentions
        r'\b(buy|sell|hold)\s+[A-Z]{1,5}\b',  # Trading recommendations
    ]

class DataConfig:
    """Data processing and export settings"""
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'json')
    EXPORT_INTERVAL = int(os.getenv('EXPORT_INTERVAL', '300'))
    DATA_RETENTION_HOURS = int(os.getenv('DATA_RETENTION_HOURS', '24'))
    
    # Output directories
    DATA_DIR = 'data'
    EXPORTS_DIR = 'exports'
    LOGS_DIR = 'logs'