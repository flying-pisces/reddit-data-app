"""
Integration tests for Reddit Data Engine
"""
import pytest
import asyncio
import time
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock

from reddit_client import RedditClient, AsyncRedditClient, RedditPost
from data_processor import DataProcessor
from api_interface import AnalysisAPI
from monitor import RedditMonitor
from config import MonitoringConfig


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_data_flow(self, temp_data_dir):
        """Test complete data flow from Reddit API to export"""
        # Create test posts
        test_posts = [
            RedditPost(
                id="integration1",
                title="$AAPL earnings beat expectations",
                author="analyst",
                subreddit="stocks",
                score=250,
                upvote_ratio=0.9,
                num_comments=67,
                created_utc=time.time() - 1800,
                url="https://reddit.com/test1",
                selftext="Strong buy recommendation with bullish outlook",
                flair="Earnings",
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            RedditPost(
                id="integration2",
                title="YOLO GME calls! 🚀🚀🚀",
                author="diamond_hands",
                subreddit="wallstreetbets",
                score=1500,
                upvote_ratio=0.85,
                num_comments=450,
                created_utc=time.time() - 900,
                url="https://reddit.com/test2",
                selftext="To the moon! Diamond hands rocket squeeze!",
                flair="YOLO",
                stickied=False,
                over_18=False,
                category="yolo_meme",
                timestamp_collected=time.time()
            )
        ]
        
        # Process through data processor
        processor = DataProcessor()
        processor.add_posts(test_posts)
        
        # Verify processing
        assert len(processor.posts_buffer) == 2
        assert "AAPL" in processor.ticker_mentions
        assert "GME" in processor.ticker_mentions
        
        # Check speculative detection
        assert processor.is_speculative_post(test_posts[1]) == True
        assert processor.is_speculative_post(test_posts[0]) == False
        
        # Export data
        export_data = processor.export_for_analysis()
        
        # Verify export structure
        assert "metadata" in export_data
        assert "trending_tickers" in export_data
        assert "subreddit_insights" in export_data
        assert export_data["metadata"]["total_posts"] == 2
        
        # Verify ticker extraction
        assert export_data["trending_tickers"]["AAPL"] == 1
        assert export_data["trending_tickers"]["GME"] == 1
        
        # Verify subreddit insights
        insights = export_data["subreddit_insights"]
        assert "stocks" in insights
        assert "wallstreetbets" in insights
        assert insights["wallstreetbets"]["speculative_ratio"] > 0
    
    @pytest.mark.asyncio
    async def test_api_integration_flow(self, temp_data_dir):
        """Test API integration with data processor"""
        # Setup API with mock data
        api = AnalysisAPI()
        
        # Create mock latest data file
        from config import DataConfig
        test_data = {
            "trending_tickers": {"AAPL": 15, "TSLA": 12, "GME": 8},
            "sentiment_analysis": {"average": 0.25, "mood": "bullish", "total": 50},
            "recent_priority_posts": [
                {
                    "id": "api_test",
                    "title": "API Integration Test",
                    "subreddit": "stocks",
                    "score": 200,
                    "comments": 45,
                    "category": "serious_investing",
                    "is_speculative": False
                }
            ],
            "activity_summary": {
                "speculative_ratio": 0.2,
                "total_posts": 50
            }
        }
        
        # Save test data
        latest_path = os.path.join(DataConfig.EXPORTS_DIR, 'latest.json')
        with open(latest_path, 'w') as f:
            json.dump(test_data, f)
        
        # Test API methods
        trending = await api.get_trending_tickers(limit=3)
        assert len(trending) == 3
        assert trending[0]["ticker"] == "AAPL"
        
        sentiment = await api.get_sentiment_overview()
        assert sentiment["mood"] == "bullish"
        
        signals = await api.get_speculative_signals()
        assert signals["speculative_ratio"] == 0.2
    
    def test_configuration_integration(self):
        """Test configuration integration across components"""
        # Test subreddit configuration
        assert len(MonitoringConfig.ALL_SUBREDDITS) > 0
        assert "wallstreetbets" in MonitoringConfig.ALL_SUBREDDITS
        assert "stocks" in MonitoringConfig.ALL_SUBREDDITS
        
        # Test category mapping
        processor = DataProcessor()
        category = processor._get_subreddit_category("wallstreetbets")
        assert category == "yolo_meme"
        
        # Test filtering criteria
        test_post = RedditPost(
            id="config_test",
            title="Config test",
            author="user",
            subreddit="stocks",
            score=MonitoringConfig.MIN_SCORE + 10,
            upvote_ratio=0.8,
            num_comments=MonitoringConfig.MIN_COMMENTS + 5,
            created_utc=time.time(),
            url="http://test.com",
            selftext="Test",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        assert test_post.meets_criteria(
            MonitoringConfig.MIN_SCORE,
            MonitoringConfig.MIN_COMMENTS
        ) == True


class TestMonitorIntegration:
    """Integration tests for monitoring system"""
    
    @pytest.mark.asyncio
    async def test_monitor_initialization(self):
        """Test monitor system initialization"""
        monitor = RedditMonitor()
        
        assert monitor.data_processor is not None
        assert isinstance(monitor.seen_post_ids, set)
        assert len(monitor.subreddit_stats) == 0
        assert monitor.running == False
    
    @pytest.mark.asyncio
    async def test_post_processing_pipeline(self):
        """Test complete post processing pipeline"""
        monitor = RedditMonitor()
        
        # Create test posts
        posts = [
            RedditPost(
                id="pipeline1",
                title="$AAPL strong buy",
                author="user1",
                subreddit="stocks",
                score=150,
                upvote_ratio=0.85,
                num_comments=35,
                created_utc=time.time() - 1800,
                url="http://test1.com",
                selftext="Bullish analysis",
                flair="DD",
                stickied=False,
                over_18=False,
                category="serious_investing",
                timestamp_collected=time.time()
            ),
            RedditPost(
                id="pipeline2",
                title="GME YOLO play",
                author="user2",
                subreddit="wallstreetbets",
                score=800,
                upvote_ratio=0.9,
                num_comments=200,
                created_utc=time.time() - 1200,
                url="http://test2.com",
                selftext="YOLO diamond hands rocket",
                flair="YOLO",
                stickied=False,
                over_18=False,
                category="yolo_meme",
                timestamp_collected=time.time()
            )
        ]
        
        # Process posts through monitor pipeline
        await monitor._process_posts(posts, "hot", "stocks")
        
        # Verify processing
        assert len(monitor.seen_post_ids) == 2
        assert len(monitor.post_buffer) == 2
        assert monitor.subreddit_stats["stocks"]["total_posts"] == 2
        assert monitor.subreddit_stats["stocks"]["speculative_posts"] == 1  # GME post
        
        # Verify data processor integration
        processor = monitor.data_processor
        assert len(processor.posts_buffer) == 2
        assert "AAPL" in processor.ticker_mentions
        assert "GME" in processor.ticker_mentions


class TestPerformanceIntegration:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_high_volume_processing(self, temp_data_dir):
        """Test processing high volume of posts"""
        processor = DataProcessor()
        
        # Generate large number of test posts
        posts = []
        tickers = ["AAPL", "TSLA", "GME", "AMC", "NVDA", "MSFT", "GOOGL", "AMZN"]
        
        for i in range(1000):  # 1000 posts
            post = RedditPost(
                id=f"perf{i}",
                title=f"Analysis of ${tickers[i % len(tickers)]}",
                author=f"user{i}",
                subreddit="stocks" if i % 2 == 0 else "wallstreetbets",
                score=50 + (i % 500),
                upvote_ratio=0.7 + (i % 30) / 100,
                num_comments=10 + (i % 100),
                created_utc=time.time() - (i * 10),
                url=f"http://test{i}.com",
                selftext=f"Content for post {i}",
                flair="DD" if i % 3 == 0 else None,
                stickied=False,
                over_18=False,
                category="serious_investing" if i % 2 == 0 else "yolo_meme",
                timestamp_collected=time.time()
            )
            posts.append(post)
        
        # Measure processing time
        start_time = time.time()
        processor.add_posts(posts)
        processing_time = time.time() - start_time
        
        # Verify results
        assert len(processor.posts_buffer) == 1000
        assert len(processor.ticker_mentions) == len(tickers)
        assert processing_time < 5.0  # Should process 1000 posts in under 5 seconds
        
        # Test export performance
        start_time = time.time()
        export_data = processor.export_for_analysis()
        export_time = time.time() - start_time
        
        assert export_time < 2.0  # Export should be fast
        assert export_data["metadata"]["total_posts"] == 1000
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent processing capabilities"""
        # Create multiple processors
        processors = [DataProcessor() for _ in range(5)]
        
        # Create tasks for concurrent processing
        async def process_batch(processor, batch_id):
            posts = []
            for i in range(100):
                post = RedditPost(
                    id=f"concurrent{batch_id}_{i}",
                    title=f"Batch {batch_id} post {i}",
                    author=f"user{i}",
                    subreddit="stocks",
                    score=100,
                    upvote_ratio=0.8,
                    num_comments=20,
                    created_utc=time.time(),
                    url=f"http://test{i}.com",
                    selftext="Content",
                    flair=None,
                    stickied=False,
                    over_18=False,
                    category="serious_investing",
                    timestamp_collected=time.time()
                )
                posts.append(post)
            
            processor.add_posts(posts)
            return len(processor.posts_buffer)
        
        # Run concurrent processing
        tasks = [
            process_batch(processors[i], i)
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all batches processed correctly
        assert all(result == 100 for result in results)


class TestErrorHandlingIntegration:
    """Integration tests for error handling"""
    
    @pytest.mark.asyncio
    async def test_api_error_recovery(self, temp_data_dir):
        """Test API error handling and recovery"""
        api = AnalysisAPI()
        
        # Test with missing data file
        data = await api.get_latest_data()
        assert data is None
        
        # Test with corrupted data file
        from config import DataConfig
        corrupted_path = os.path.join(DataConfig.EXPORTS_DIR, 'latest.json')
        with open(corrupted_path, 'w') as f:
            f.write("invalid json {")
        
        data = await api.get_latest_data()
        assert data is None  # Should handle corrupted file gracefully
    
    def test_data_processor_error_handling(self, temp_data_dir):
        """Test data processor error handling"""
        processor = DataProcessor()
        
        # Test with malformed posts
        malformed_posts = [None, "not a post", {}]
        
        # Should handle gracefully without crashing
        try:
            processor.add_posts(malformed_posts)
        except Exception as e:
            # Specific error handling can be tested here
            pass
        
        # Processor should still be functional
        valid_post = RedditPost(
            id="valid",
            title="Valid post",
            author="user",
            subreddit="stocks",
            score=100,
            upvote_ratio=0.8,
            num_comments=20,
            created_utc=time.time(),
            url="http://test.com",
            selftext="Content",
            flair=None,
            stickied=False,
            over_18=False,
            category="serious_investing",
            timestamp_collected=time.time()
        )
        
        processor.add_posts([valid_post])
        assert len([p for p in processor.posts_buffer if isinstance(p, RedditPost)]) >= 1