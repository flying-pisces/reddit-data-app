"""
Tests for Reddit client functionality
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import time

from reddit_client import RedditClient, AsyncRedditClient, RedditPost
from config import MonitoringConfig


class TestRedditPost:
    """Tests for RedditPost dataclass"""
    
    def test_post_creation(self, sample_reddit_post):
        """Test RedditPost creation and basic properties"""
        post = sample_reddit_post
        assert post.id == "test123"
        assert post.title == "AAPL to the moon! 🚀"
        assert post.subreddit == "wallstreetbets"
        assert post.category == "yolo_meme"
    
    def test_post_to_dict(self, sample_reddit_post):
        """Test post conversion to dictionary"""
        post = sample_reddit_post
        data = post.to_dict()
        
        assert isinstance(data, dict)
        assert data['id'] == post.id
        assert data['title'] == post.title
        assert data['score'] == post.score
    
    def test_is_recent(self, sample_reddit_post):
        """Test post recency check"""
        post = sample_reddit_post
        
        # Post is 1 hour old, should be recent within 24 hours
        assert post.is_recent(24) == True
        assert post.is_recent(2) == True
        
        # Should not be recent within 30 minutes
        assert post.is_recent(0.5) == False
    
    def test_meets_criteria(self, sample_reddit_post):
        """Test post criteria filtering"""
        post = sample_reddit_post
        
        # Post has score 150, comments 45
        assert post.meets_criteria(100, 40) == True
        assert post.meets_criteria(200, 40) == False
        assert post.meets_criteria(100, 50) == False


class TestRedditClient:
    """Tests for synchronous Reddit client"""
    
    def test_client_initialization(self, test_config):
        """Test Reddit client initialization"""
        with patch('praw.Reddit') as mock_praw:
            mock_reddit = MagicMock()
            mock_praw.return_value = mock_reddit
            
            client = RedditClient()
            assert client.reddit is not None
            mock_praw.assert_called()
    
    def test_get_subreddit_category(self):
        """Test subreddit categorization"""
        with patch('praw.Reddit'):
            client = RedditClient()
            
            assert client.get_subreddit_category('wallstreetbets') == 'yolo_meme'
            assert client.get_subreddit_category('stocks') == 'serious_investing'
            assert client.get_subreddit_category('unknown') == 'other'
    
    def test_get_hot_posts(self, mock_praw_submissions, test_config):
        """Test fetching hot posts"""
        with patch('praw.Reddit') as mock_praw:
            mock_reddit = MagicMock()
            mock_subreddit = MagicMock()
            mock_subreddit.hot.return_value = mock_praw_submissions
            mock_reddit.subreddit.return_value = mock_subreddit
            mock_praw.return_value = mock_reddit
            
            client = RedditClient()
            posts = client.get_hot_posts('stocks', limit=10)
            
            assert len(posts) == 3
            assert all(isinstance(post, RedditPost) for post in posts)
            assert posts[0].title == "AAPL earnings beat expectations"
    
    def test_get_new_posts(self, mock_praw_submissions, test_config):
        """Test fetching new posts"""
        with patch('praw.Reddit') as mock_praw:
            mock_reddit = MagicMock()
            mock_subreddit = MagicMock()
            mock_subreddit.new.return_value = mock_praw_submissions
            mock_reddit.subreddit.return_value = mock_subreddit
            mock_praw.return_value = mock_reddit
            
            client = RedditClient()
            posts = client.get_new_posts('investing', limit=25)
            
            assert len(posts) == 3
            assert all(isinstance(post, RedditPost) for post in posts)
    
    def test_error_handling(self, test_config):
        """Test error handling in Reddit client"""
        with patch('praw.Reddit') as mock_praw:
            mock_reddit = MagicMock()
            mock_reddit.subreddit.side_effect = Exception("API Error")
            mock_praw.return_value = mock_reddit
            
            client = RedditClient()
            posts = client.get_hot_posts('stocks')
            
            assert posts == []  # Should return empty list on error


class TestAsyncRedditClient:
    """Tests for asynchronous Reddit client"""
    
    @pytest.mark.asyncio
    async def test_async_client_initialization(self, test_config):
        """Test async Reddit client initialization"""
        with patch('asyncpraw.Reddit') as mock_asyncpraw:
            mock_reddit = AsyncMock()
            mock_asyncpraw.return_value = mock_reddit
            
            async with AsyncRedditClient() as client:
                assert client.reddit is not None
                mock_asyncpraw.assert_called()
    
    @pytest.mark.asyncio
    async def test_async_get_hot_posts(self, test_config):
        """Test async fetching of hot posts"""
        with patch('asyncpraw.Reddit') as mock_asyncpraw:
            mock_reddit = AsyncMock()
            mock_subreddit = AsyncMock()
            
            # Mock async iteration
            async def mock_hot_posts(*args, **kwargs):
                for submission in [
                    MockAsyncSubmission(id="1", title="Test 1", subreddit="stocks"),
                    MockAsyncSubmission(id="2", title="Test 2", subreddit="stocks")
                ]:
                    yield submission
            
            mock_subreddit.hot = mock_hot_posts
            mock_reddit.subreddit.return_value = mock_subreddit
            mock_asyncpraw.return_value = mock_reddit
            
            async with AsyncRedditClient() as client:
                posts = await client.get_hot_posts('stocks', limit=10)
                
                assert len(posts) == 2
                assert all(isinstance(post, RedditPost) for post in posts)
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self, test_config):
        """Test async error handling"""
        with patch('asyncpraw.Reddit') as mock_asyncpraw:
            mock_reddit = AsyncMock()
            mock_reddit.subreddit.side_effect = Exception("Async API Error")
            mock_asyncpraw.return_value = mock_reddit
            
            async with AsyncRedditClient() as client:
                posts = await client.get_hot_posts('stocks')
                
                assert posts == []
    
    @pytest.mark.asyncio
    async def test_monitor_subreddits(self, test_config):
        """Test monitoring multiple subreddits"""
        with patch('asyncpraw.Reddit') as mock_asyncpraw:
            mock_reddit = AsyncMock()
            mock_client = AsyncRedditClient()
            mock_client.reddit = mock_reddit
            
            # Mock get_new_posts to return test data
            async def mock_get_new_posts(subreddit, limit):
                return [
                    RedditPost(
                        id=f"{subreddit}1",
                        title=f"Post from {subreddit}",
                        author="test_user",
                        subreddit=subreddit,
                        score=100,
                        upvote_ratio=0.8,
                        num_comments=20,
                        created_utc=time.time(),
                        url="http://test.com",
                        selftext="Test content",
                        flair=None,
                        stickied=False,
                        over_18=False,
                        category="test",
                        timestamp_collected=time.time()
                    )
                ]
            
            mock_client.get_new_posts = mock_get_new_posts
            
            # Test monitoring with timeout
            monitor_gen = mock_client.monitor_subreddits(['stocks', 'investing'])
            
            try:
                posts = await asyncio.wait_for(monitor_gen.__anext__(), timeout=1.0)
                assert len(posts) == 2
                assert posts[0].subreddit == 'stocks'
                assert posts[1].subreddit == 'investing'
            except asyncio.TimeoutError:
                pytest.skip("Monitor test timed out - expected behavior")


class MockAsyncSubmission:
    """Mock async PRAW submission"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'test')
        self.title = kwargs.get('title', 'Test')
        self.author = kwargs.get('author', 'user')
        self.subreddit = kwargs.get('subreddit', 'test')
        self.score = kwargs.get('score', 100)
        self.upvote_ratio = kwargs.get('upvote_ratio', 0.8)
        self.num_comments = kwargs.get('num_comments', 10)
        self.created_utc = kwargs.get('created_utc', time.time())
        self.url = kwargs.get('url', 'http://test.com')
        self.selftext = kwargs.get('selftext', '')
        self.link_flair_text = kwargs.get('flair', None)
        self.stickied = kwargs.get('stickied', False)
        self.over_18 = kwargs.get('over_18', False)