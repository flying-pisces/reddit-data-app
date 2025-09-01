"""
Reddit Data Engine Configuration
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class RedditConfig:
    """Reddit API configuration"""
    CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditDataEngine/1.0')
    USERNAME = os.getenv('REDDIT_USERNAME')
    PASSWORD = os.getenv('REDDIT_PASSWORD')

class MonitoringConfig:
    """Monitoring and data collection settings"""
    
    # Target subreddits organized by category
    SUBREDDITS: Dict[str, List[str]] = {
        'yolo_meme': ['wallstreetbets'],
        'serious_investing': ['stocks', 'investing'],
        'speculative': ['pennystocks'],
        'value_oriented': ['UndervaluedStonks', 'ValueInvesting'],
        'options_focus': ['options'],
        'trading': ['trading', 'technicalanalysis', 'daytrading'],
        'sector_specific': ['stockmarket', 'biotech_stocks', 'SecurityAnalysis']
    }
    
    # Flattened list for easy iteration
    ALL_SUBREDDITS = [sub for subs in SUBREDDITS.values() for sub in subs]
    
    # Monitoring intervals (seconds)
    HOT_POSTS_INTERVAL = 60
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