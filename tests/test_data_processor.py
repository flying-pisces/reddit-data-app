"""
Tests for data processing functionality
"""
import pytest
import time
import json
from unittest.mock import patch, MagicMock
from collections import Counter

from data_processor import DataProcessor
from reddit_client import RedditPost


class TestDataProcessor:
    """Tests for DataProcessor class"""
    
    def test_processor_initialization(self, temp_data_dir):
        """Test DataProcessor initialization"""
        processor = DataProcessor()
        
        assert len(processor.posts_buffer) == 0
        assert isinstance(processor.ticker_mentions, Counter)
        assert isinstance(processor.sentiment_scores, dict)
        assert len(processor.subreddit_activity) == 0
    
    def test_add_posts(self, temp_data_dir):
        """Test adding posts to processor"""
        processor = DataProcessor()
        
        # Create test posts with tickers
        posts = [
            RedditPost(
                id="test1",
                title="AAPL to the moon!",
                author="user1",
                subreddit="stocks",
                score=100,
                upvote_ratio=0.8,
                num_comments=20,
                created_utc=time.time(),
                url="http://test1.com",
                selftext="Bullish on $AAPL and $TSLA",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            RedditPost(
                id="test2",
                title="GME squeeze incoming",
                author="user2", 
                subreddit="wallstreetbets",
                score=500,
                upvote_ratio=0.9,
                num_comments=100,
                created_utc=time.time(),
                url="http://test2.com",
                selftext="YOLO on $GME calls!",
                flair="YOLO",
                stickied=False,
                over_18=False,
                category="yolo_meme",
                timestamp_collected=time.time()
            )
        ]
        
        processor.add_posts(posts)
        
        assert len(processor.posts_buffer) == 2
        assert "AAPL" in processor.ticker_mentions
        assert "TSLA" in processor.ticker_mentions
        assert "GME" in processor.ticker_mentions
        assert processor.ticker_mentions["AAPL"] == 1
        assert processor.ticker_mentions["GME"] == 1
    
    def test_extract_tickers(self, temp_data_dir):
        """Test ticker extraction from post content"""
        processor = DataProcessor()
        
        post = RedditPost(
            id="test",
            title="Analysis of $AAPL, $MSFT, and $GOOGL",
            author="user",
            subreddit="investing",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=time.time(),
            url="http://test.com",
            selftext="Also considering $NVDA and $AMD for tech exposure",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        processor._extract_tickers(post)
        
        expected_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD"]
        for ticker in expected_tickers:
            assert ticker in processor.ticker_mentions
            assert processor.ticker_mentions[ticker] == 1
    
    def test_sentiment_analysis(self, temp_data_dir):
        """Test basic sentiment analysis"""
        processor = DataProcessor()
        
        # Bullish post
        bullish_post = RedditPost(
            id="bull",
            title="Strong buy on this stock",
            author="user",
            subreddit="stocks",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=time.time(),
            url="http://test.com",
            selftext="Bullish sentiment, great growth potential, strong profit",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        # Bearish post
        bearish_post = RedditPost(
            id="bear",
            title="Time to sell this declining stock",
            author="user",
            subreddit="stocks",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=time.time(),
            url="http://test.com",
            selftext="Bearish outlook, expecting crash and major loss",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        processor._analyze_sentiment(bullish_post)
        processor._analyze_sentiment(bearish_post)
        
        assert processor.sentiment_scores["bull"] > 0  # Positive sentiment
        assert processor.sentiment_scores["bear"] < 0  # Negative sentiment
    
    def test_speculative_post_detection(self, temp_data_dir):
        """Test detection of speculative posts"""
        processor = DataProcessor()
        
        # Speculative post with YOLO keywords
        yolo_post = RedditPost(
            id="yolo",
            title="YOLO GME to the moon! 🚀",
            author="user",
            subreddit="wallstreetbets",
            score=1000,
            upvote_ratio=0.85,
            num_comments=200,
            created_utc=time.time() - 1800,  # 30 minutes ago
            url="http://test.com",
            selftext="Diamond hands, rocket ship, squeeze incoming!",
            flair="YOLO",
            stickied=False,
            over_18=False,
            category="yolo_meme",
            timestamp_collected=time.time()
        )
        
        # Regular post
        regular_post = RedditPost(
            id="regular",
            title="Quarterly earnings analysis",
            author="user",
            subreddit="investing",
            score=50,
            upvote_ratio=0.8,
            num_comments=15,
            created_utc=time.time() - 7200,  # 2 hours ago
            url="http://test.com",
            selftext="Detailed financial analysis of fundamentals",
            flair="Analysis",
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        assert processor.is_speculative_post(yolo_post) == True
        assert processor.is_speculative_post(regular_post) == False
    
    def test_filter_priority_posts(self, temp_data_dir):
        """Test filtering of priority posts"""
        processor = DataProcessor()
        
        posts = [
            # High score post
            RedditPost(
                id="high_score",
                title="Market analysis",
                author="user",
                subreddit="stocks",
                score=600,  # Above 500 threshold
                upvote_ratio=0.8,
                num_comments=50,
                created_utc=time.time(),
                url="http://test.com",
                selftext="Analysis",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            # High comments post
            RedditPost(
                id="high_comments",
                title="Discussion thread",
                author="user",
                subreddit="investing",
                score=100,
                upvote_ratio=0.8,
                num_comments=250,  # Above 200 threshold
                created_utc=time.time(),
                url="http://test.com",
                selftext="Discussion",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            # Regular post
            RedditPost(
                id="regular",
                title="Normal post",
                author="user",
                subreddit="stocks",
                score=50,
                upvote_ratio=0.8,
                num_comments=10,
                created_utc=time.time(),
                url="http://test.com",
                selftext="Content",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            )
        ]
        
        priority_posts = processor.filter_priority_posts(posts)
        
        assert len(priority_posts) == 2
        priority_ids = [post.id for post in priority_posts]
        assert "high_score" in priority_ids
        assert "high_comments" in priority_ids
        assert "regular" not in priority_ids
    
    def test_trending_tickers(self, temp_data_dir):
        """Test getting trending tickers"""
        processor = DataProcessor()
        
        # Manually populate ticker mentions
        processor.ticker_mentions.update({
            "AAPL": 10,
            "TSLA": 8,
            "GME": 15,
            "AMC": 5,
            "NVDA": 12
        })
        
        trending = processor.get_trending_tickers(top_n=3)
        
        assert len(trending) == 3
        assert trending[0] == ("GME", 15)  # Most mentioned
        assert trending[1] == ("NVDA", 12)
        assert trending[2] == ("AAPL", 10)
    
    def test_subreddit_insights(self, temp_data_dir):
        """Test subreddit insights generation"""
        processor = DataProcessor()
        
        # Add posts to generate insights
        posts = [
            RedditPost(
                id="post1",
                title="AAPL discussion",
                author="user1",
                subreddit="stocks",
                score=100,
                upvote_ratio=0.8,
                num_comments=20,
                created_utc=time.time(),
                url="http://test1.com",
                selftext="Regular discussion",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            RedditPost(
                id="post2",
                title="YOLO GME",
                author="user2",
                subreddit="stocks",
                score=200,
                upvote_ratio=0.9,
                num_comments=50,
                created_utc=time.time(),
                url="http://test2.com",
                selftext="YOLO rocket moon",
                flair=None,
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            )
        ]
        
        processor.add_posts(posts)
        insights = processor.get_subreddit_insights()
        
        assert "stocks" in insights
        stocks_data = insights["stocks"]
        assert stocks_data["total_posts"] == 2
        assert stocks_data["avg_score"] == 150.0  # (100 + 200) / 2
        assert stocks_data["avg_comments"] == 35.0  # (20 + 50) / 2
        assert stocks_data["speculative_ratio"] > 0  # Should detect speculative post
    
    @pytest.mark.asyncio
    async def test_export_for_analysis(self, temp_data_dir):
        """Test data export for analysis"""
        processor = DataProcessor()
        
        # Add test data
        test_posts = [
            RedditPost(
                id="export_test",
                title="$AAPL analysis",
                author="user",
                subreddit="investing",
                score=150,
                upvote_ratio=0.85,
                num_comments=30,
                created_utc=time.time(),
                url="http://test.com",
                selftext="Bullish on Apple",
                flair="DD",
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            )
        ]
        
        processor.add_posts(test_posts)
        export_data = processor.export_for_analysis()
        
        assert "metadata" in export_data
        assert "trending_tickers" in export_data
        assert "subreddit_insights" in export_data
        assert "sentiment_analysis" in export_data
        assert "activity_summary" in export_data
        
        assert export_data["metadata"]["total_posts"] == 1
        assert "AAPL" in export_data["trending_tickers"]
        assert export_data["activity_summary"]["total_posts"] == 1
    
    @pytest.mark.asyncio
    async def test_save_export_data(self, temp_data_dir):
        """Test saving export data to file"""
        processor = DataProcessor()
        
        test_data = {
            "metadata": {"timestamp": "2025-01-01T00:00:00"},
            "test": "data"
        }
        
        await processor.save_export_data(test_data, "test_export.json")
        
        # Verify file was created and contains correct data
        import os
        from config import DataConfig
        
        filepath = os.path.join(DataConfig.EXPORTS_DIR, "test_export.json")
        assert os.path.exists(filepath)
        
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == test_data
    
    def test_cleanup_old_data(self, temp_data_dir):
        """Test cleanup of old data"""
        processor = DataProcessor()
        
        # Add old and new posts
        old_time = time.time() - 86400 * 2  # 2 days ago
        new_time = time.time()
        
        old_post = RedditPost(
            id="old",
            title="Old post",
            author="user",
            subreddit="stocks",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=old_time,
            url="http://old.com",
            selftext="Old content",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=old_time
        )
        
        new_post = RedditPost(
            id="new",
            title="New post",
            author="user",
            subreddit="stocks",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=new_time,
            url="http://new.com",
            selftext="New content",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=new_time
        )
        
        processor.add_posts([old_post, new_post])
        assert len(processor.posts_buffer) == 2
        
        # Cleanup should remove old post (assuming 24h retention)
        processor._cleanup_old_data()
        
        remaining_posts = [post for post in processor.posts_buffer]
        assert len(remaining_posts) == 1
        assert remaining_posts[0].id == "new"