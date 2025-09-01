"""
Pytest configuration and fixtures for Reddit Data Engine tests
"""
import pytest
import asyncio
import logging
import tempfile
import os
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
import time

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reddit_client import RedditPost
from config import RedditConfig, MonitoringConfig


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_reddit_post():
    """Create a sample Reddit post for testing"""
    return RedditPost(
        id="test123",
        title="AAPL to the moon! 🚀",
        author="test_user",
        subreddit="wallstreetbets",
        score=150,
        upvote_ratio=0.85,
        num_comments=45,
        created_utc=time.time() - 3600,  # 1 hour ago
        url="https://reddit.com/r/wallstreetbets/test123",
        selftext="This is a test post about AAPL going up!",
        flair="DD",
        stickied=False,
        over_18=False,
        category="yolo_meme",
        timestamp_collected=time.time()
    )


@pytest.fixture
def sample_reddit_posts():
    """Create multiple sample Reddit posts for testing"""
    posts = []
    tickers = ["AAPL", "TSLA", "GME", "AMC", "NVDA"]
    subreddits = ["wallstreetbets", "stocks", "investing"]
    
    for i, ticker in enumerate(tickers):
        post = RedditPost(
            id=f"test{i}",
            title=f"{ticker} analysis and predictions 📈",
            author=f"user_{i}",
            subreddit=subreddits[i % len(subreddits)],
            score=100 + i * 20,
            upvote_ratio=0.8 + i * 0.02,
            num_comments=20 + i * 10,
            created_utc=time.time() - (i * 1800),  # Spaced 30 min apart
            url=f"https://reddit.com/r/test/test{i}",
            selftext=f"Analysis of ${ticker} stock with bullish sentiment",
            flair="Analysis",
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        posts.append(post)
    
    return posts


@pytest.fixture
def mock_reddit_client():
    """Mock Reddit client for testing"""
    mock = MagicMock()
    mock.get_hot_posts.return_value = []
    mock.get_new_posts.return_value = []
    mock.get_rising_posts.return_value = []
    return mock


@pytest.fixture
def mock_async_reddit_client():
    """Mock async Reddit client for testing"""
    mock = AsyncMock()
    mock.get_hot_posts.return_value = []
    mock.get_new_posts.return_value = []
    mock.get_rising_posts.return_value = []
    return mock


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update config to use temp directory
        original_data_dir = MonitoringConfig.DATA_DIR if hasattr(MonitoringConfig, 'DATA_DIR') else None
        original_exports_dir = MonitoringConfig.EXPORTS_DIR if hasattr(MonitoringConfig, 'EXPORTS_DIR') else None
        
        MonitoringConfig.DATA_DIR = os.path.join(temp_dir, 'data')
        MonitoringConfig.EXPORTS_DIR = os.path.join(temp_dir, 'exports')
        
        os.makedirs(MonitoringConfig.DATA_DIR, exist_ok=True)
        os.makedirs(MonitoringConfig.EXPORTS_DIR, exist_ok=True)
        
        yield temp_dir
        
        # Restore original paths
        if original_data_dir:
            MonitoringConfig.DATA_DIR = original_data_dir
        if original_exports_dir:
            MonitoringConfig.EXPORTS_DIR = original_exports_dir


@pytest.fixture
def test_config():
    """Test configuration with mock values"""
    original_values = {}
    
    # Store original values
    if hasattr(RedditConfig, 'CLIENT_ID'):
        original_values['CLIENT_ID'] = RedditConfig.CLIENT_ID
    if hasattr(RedditConfig, 'CLIENT_SECRET'):
        original_values['CLIENT_SECRET'] = RedditConfig.CLIENT_SECRET
    
    # Set test values
    RedditConfig.CLIENT_ID = "test_client_id"
    RedditConfig.CLIENT_SECRET = "test_client_secret"
    RedditConfig.USER_AGENT = "TestRedditDataEngine/1.0"
    
    yield RedditConfig
    
    # Restore original values
    for key, value in original_values.items():
        setattr(RedditConfig, key, value)


@pytest.fixture
def capture_logs():
    """Capture log messages for testing"""
    import logging
    from io import StringIO
    
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    yield log_stream
    
    logger.removeHandler(handler)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for each test"""
    # Disable real API calls during tests
    os.environ['REDDIT_TEST_MODE'] = '1'
    
    yield
    
    # Cleanup
    if 'REDDIT_TEST_MODE' in os.environ:
        del os.environ['REDDIT_TEST_MODE']


class MockPrawSubmission:
    """Mock PRAW submission for testing"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'test123')
        self.title = kwargs.get('title', 'Test Post')
        self.author = kwargs.get('author', 'test_user')
        self.subreddit = MagicMock()
        self.subreddit.__str__ = lambda: kwargs.get('subreddit', 'test')
        self.score = kwargs.get('score', 100)
        self.upvote_ratio = kwargs.get('upvote_ratio', 0.8)
        self.num_comments = kwargs.get('num_comments', 10)
        self.created_utc = kwargs.get('created_utc', time.time())
        self.url = kwargs.get('url', 'https://reddit.com/test')
        self.selftext = kwargs.get('selftext', 'Test content')
        self.link_flair_text = kwargs.get('flair', None)
        self.stickied = kwargs.get('stickied', False)
        self.over_18 = kwargs.get('over_18', False)


@pytest.fixture
def mock_praw_submissions():
    """Create mock PRAW submissions"""
    submissions = [
        MockPrawSubmission(
            id="post1",
            title="AAPL earnings beat expectations",
            subreddit="stocks",
            score=245,
            num_comments=67
        ),
        MockPrawSubmission(
            id="post2", 
            title="TSLA delivery numbers looking strong",
            subreddit="investing",
            score=189,
            num_comments=34
        ),
        MockPrawSubmission(
            id="post3",
            title="GME to the moon! 🚀🚀🚀",
            subreddit="wallstreetbets",
            score=1250,
            num_comments=340,
            selftext="This is not financial advice but GME is going up!"
        )
    ]
    
    return submissions