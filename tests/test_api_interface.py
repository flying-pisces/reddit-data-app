"""
Tests for API interface functionality
"""
import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import os

from api_interface import AnalysisAPI, SimpleAPI, get_reddit_insights
from reddit_client import RedditPost
import time


class TestAnalysisAPI:
    """Tests for AnalysisAPI class"""
    
    @pytest.fixture
    def sample_export_data(self):
        """Sample export data for testing"""
        return {
            "metadata": {
                "timestamp": "2025-01-01T12:00:00",
                "total_posts": 100
            },
            "trending_tickers": {
                "AAPL": 25,
                "TSLA": 20,
                "GME": 15,
                "NVDA": 10,
                "AMC": 8
            },
            "subreddit_insights": {
                "wallstreetbets": {
                    "total_posts": 45,
                    "speculative_ratio": 0.65,
                    "recent_activity": 12,
                    "category": "yolo_meme"
                },
                "stocks": {
                    "total_posts": 35,
                    "speculative_ratio": 0.15,
                    "recent_activity": 8,
                    "category": "serious_investing"
                }
            },
            "recent_priority_posts": [
                {
                    "id": "post1",
                    "title": "AAPL earnings beat expectations",
                    "subreddit": "stocks",
                    "score": 450,
                    "comments": 89,
                    "category": "serious_investing",
                    "is_speculative": False
                },
                {
                    "id": "post2",
                    "title": "GME to the moon! 🚀",
                    "subreddit": "wallstreetbets",
                    "score": 1200,
                    "comments": 340,
                    "category": "yolo_meme",
                    "is_speculative": True
                }
            ],
            "sentiment_analysis": {
                "average": 0.15,
                "positive": 60,
                "negative": 25,
                "neutral": 15,
                "total": 100
            },
            "activity_summary": {
                "total_posts": 100,
                "speculative_posts": 30,
                "speculative_ratio": 0.3,
                "posting_rate_per_hour": 25.5
            }
        }
    
    @pytest.fixture
    def mock_latest_file(self, sample_export_data, temp_data_dir):
        """Create mock latest.json file"""
        from config import DataConfig
        
        latest_path = os.path.join(DataConfig.EXPORTS_DIR, 'latest.json')
        with open(latest_path, 'w') as f:
            json.dump(sample_export_data, f)
        
        return latest_path
    
    @pytest.mark.asyncio
    async def test_get_latest_data(self, mock_latest_file, sample_export_data):
        """Test getting latest exported data"""
        api = AnalysisAPI()
        
        data = await api.get_latest_data()
        
        assert data is not None
        assert data["metadata"]["total_posts"] == 100
        assert "AAPL" in data["trending_tickers"]
    
    @pytest.mark.asyncio
    async def test_get_latest_data_no_file(self, temp_data_dir):
        """Test getting latest data when no file exists"""
        api = AnalysisAPI()
        
        data = await api.get_latest_data()
        
        assert data is None
    
    @pytest.mark.asyncio
    async def test_get_trending_tickers(self, mock_latest_file):
        """Test getting trending tickers"""
        api = AnalysisAPI()
        
        tickers = await api.get_trending_tickers(limit=3)
        
        assert len(tickers) == 3
        assert tickers[0]["ticker"] == "AAPL"
        assert tickers[0]["mentions"] == 25
        assert tickers[0]["rank"] == 1
        assert tickers[1]["ticker"] == "TSLA"
        assert tickers[2]["ticker"] == "GME"
    
    @pytest.mark.asyncio
    async def test_get_subreddit_activity(self, mock_latest_file):
        """Test getting subreddit activity"""
        api = AnalysisAPI()
        
        # Test all subreddits
        all_activity = await api.get_subreddit_activity()
        assert "wallstreetbets" in all_activity
        assert "stocks" in all_activity
        
        # Test specific subreddit
        wsb_activity = await api.get_subreddit_activity("wallstreetbets")
        assert wsb_activity["total_posts"] == 45
        assert wsb_activity["speculative_ratio"] == 0.65
        
        # Test non-existent subreddit
        empty_activity = await api.get_subreddit_activity("nonexistent")
        assert empty_activity == {}
    
    @pytest.mark.asyncio
    async def test_get_priority_posts(self, mock_latest_file):
        """Test getting priority posts"""
        api = AnalysisAPI()
        
        # Test all posts
        all_posts = await api.get_priority_posts()
        assert len(all_posts) == 2
        
        # Test filtered by category
        serious_posts = await api.get_priority_posts(category="serious_investing")
        assert len(serious_posts) == 1
        assert serious_posts[0]["id"] == "post1"
        
        yolo_posts = await api.get_priority_posts(category="yolo_meme")
        assert len(yolo_posts) == 1
        assert yolo_posts[0]["id"] == "post2"
    
    @pytest.mark.asyncio
    async def test_get_speculative_signals(self, mock_latest_file):
        """Test getting speculative signals"""
        api = AnalysisAPI()
        
        signals = await api.get_speculative_signals()
        
        assert signals["total_speculative_posts"] == 30
        assert signals["speculative_ratio"] == 0.3
        assert len(signals["recent_speculative_posts"]) == 1
        assert signals["recent_speculative_posts"][0]["id"] == "post2"
        assert len(signals["active_speculative_subreddits"]) == 1
        assert signals["active_speculative_subreddits"][0]["subreddit"] == "wallstreetbets"
    
    @pytest.mark.asyncio
    async def test_get_sentiment_overview(self, mock_latest_file):
        """Test getting sentiment overview"""
        api = AnalysisAPI()
        
        sentiment = await api.get_sentiment_overview()
        
        assert sentiment["average"] == 0.15
        assert sentiment["positive"] == 60
        assert sentiment["mood"] == "neutral"  # 0.15 is between -0.2 and 0.2
        assert sentiment["confidence"] == 0.15
    
    @pytest.mark.asyncio
    async def test_get_real_time_feed(self):
        """Test getting real-time feed"""
        api = AnalysisAPI()
        
        # Mock the sync client
        with patch.object(api, 'sync_client') as mock_client:
            mock_posts = [
                RedditPost(
                    id="rt1",
                    title="Real-time post 1",
                    author="user1",
                    subreddit="stocks",
                    score=75,
                    upvote_ratio=0.8,
                    num_comments=20,
                    created_utc=time.time() - 1800,  # 30 minutes ago
                    url="http://test1.com",
                    selftext="Content 1",
                    flair=None,
                    stickied=False,
                    over_18=False,
                    category="serious_investing",
                    timestamp_collected=time.time()
                ),
                RedditPost(
                    id="rt2",
                    title="Real-time post 2",
                    author="user2",
                    subreddit="investing",
                    score=25,  # Below min_score
                    upvote_ratio=0.7,
                    num_comments=5,
                    created_utc=time.time() - 1800,
                    url="http://test2.com",
                    selftext="Content 2",
                    flair=None,
                    stickied=False,
                    over_18=False,
                    category="serious_investing",
                    timestamp_collected=time.time()
                )
            ]
            
            mock_client.get_hot_posts.return_value = mock_posts
            
            feed = await api.get_real_time_feed(min_score=50)
            
            assert len(feed) == 1  # Only post with score >= 50
            assert feed[0]["id"] == "rt1"
            assert feed[0]["score"] == 75
    
    @pytest.mark.asyncio
    async def test_export_custom_data(self):
        """Test custom data export"""
        api = AnalysisAPI()
        
        # Mock async client
        with patch('api_interface.AsyncRedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock return data
            test_posts = [
                RedditPost(
                    id="custom1",
                    title="Custom export test",
                    author="user",
                    subreddit="stocks",
                    score=100,
                    upvote_ratio=0.8,
                    num_comments=25,
                    created_utc=time.time() - 3600,  # 1 hour ago
                    url="http://test.com",
                    selftext="$AAPL analysis",
                    flair="DD",
                    stickied=False,
                    over_18=False,
                    category="serious_investing",
                    timestamp_collected=time.time()
                )
            ]
            
            mock_client.get_hot_posts.return_value = test_posts
            mock_client.get_new_posts.return_value = test_posts
            mock_client.get_rising_posts.return_value = test_posts
            
            result = await api.export_custom_data(
                subreddits=["stocks"],
                hours_back=24,
                min_engagement=50
            )
            
            assert "metadata" in result
            assert "posts" in result
            assert "trending_tickers" in result
            assert "summary" in result
            assert result["metadata"]["subreddits_requested"] == ["stocks"]


class TestSimpleAPI:
    """Tests for SimpleAPI class"""
    
    @pytest.mark.asyncio
    async def test_get_hot_tickers(self):
        """Test getting hot tickers"""
        simple_api = SimpleAPI()
        
        # Mock the underlying API
        with patch.object(simple_api.api, 'get_trending_tickers') as mock_trending:
            mock_trending.return_value = [
                {"ticker": "AAPL", "mentions": 25, "rank": 1},
                {"ticker": "TSLA", "mentions": 20, "rank": 2},
                {"ticker": "GME", "mentions": 15, "rank": 3}
            ]
            
            hot_tickers = await simple_api.get_hot_tickers(limit=3)
            
            assert hot_tickers == ["AAPL", "TSLA", "GME"]
    
    @pytest.mark.asyncio
    async def test_get_market_mood(self):
        """Test getting market mood"""
        simple_api = SimpleAPI()
        
        with patch.object(simple_api.api, 'get_sentiment_overview') as mock_sentiment:
            mock_sentiment.return_value = {"mood": "bullish"}
            
            mood = await simple_api.get_market_mood()
            
            assert mood == "bullish"
    
    @pytest.mark.asyncio
    async def test_get_yolo_activity(self):
        """Test getting YOLO activity"""
        simple_api = SimpleAPI()
        
        with patch.object(simple_api.api, 'get_subreddit_activity') as mock_activity:
            mock_activity.return_value = {
                "recent_activity": 25,
                "speculative_ratio": 0.75
            }
            
            yolo_activity = await simple_api.get_yolo_activity()
            
            assert yolo_activity["recent_posts"] == 25
            assert yolo_activity["speculative_ratio"] == 75  # Converted to percentage
    
    @pytest.mark.asyncio
    async def test_alert_check(self):
        """Test alert checking"""
        simple_api = SimpleAPI()
        
        with patch.object(simple_api.api, 'get_speculative_signals') as mock_signals, \
             patch.object(simple_api.api, 'get_sentiment_overview') as mock_sentiment:
            
            # High speculation scenario
            mock_signals.return_value = {"speculative_ratio": 0.4}
            mock_sentiment.return_value = {"average": 0.6}
            
            alerts = await simple_api.alert_check()
            
            assert alerts["alert_count"] == 2  # High speculation + extreme sentiment
            assert any(alert["type"] == "high_speculation" for alert in alerts["alerts"])
            assert any(alert["type"] == "extreme_sentiment" for alert in alerts["alerts"])


@pytest.mark.asyncio
async def test_get_reddit_insights():
    """Test the convenience function for getting insights"""
    with patch('api_interface.AnalysisAPI') as mock_api_class:
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        # Mock async methods
        mock_api.get_trending_tickers.return_value = [{"ticker": "AAPL", "mentions": 10}]
        mock_api.get_sentiment_overview.return_value = {"mood": "neutral"}
        mock_api.get_speculative_signals.return_value = {"speculative_ratio": 0.2}
        mock_api.get_priority_posts.return_value = [{"id": "test", "title": "Test"}]
        
        insights = await get_reddit_insights()
        
        assert "trending_tickers" in insights
        assert "market_sentiment" in insights
        assert "speculative_signals" in insights
        assert "priority_posts" in insights