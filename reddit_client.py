"""
Reddit API Client for data collection
"""
import praw
import asyncpraw
import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import logging
import time
from config import RedditConfig, MonitoringConfig

@dataclass
class RedditPost:
    """Structured representation of a Reddit post"""
    id: str
    title: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    url: str
    selftext: str
    flair: Optional[str]
    stickied: bool
    over_18: bool
    category: str
    timestamp_collected: float
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def is_recent(self, hours: int = 24) -> bool:
        """Check if post is within specified hours"""
        now = time.time()
        return (now - self.created_utc) <= (hours * 3600)
    
    def meets_criteria(self, min_score: int = 10, min_comments: int = 5) -> bool:
        """Check if post meets minimum engagement criteria"""
        return self.score >= min_score and self.num_comments >= min_comments

class RedditClient:
    """Synchronous Reddit client for basic operations"""
    
    def __init__(self):
        self.reddit = None
        self.logger = logging.getLogger(__name__)
        self._setup_client()
    
    def _setup_client(self):
        """Initialize Reddit client"""
        try:
            self.reddit = praw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT,
                username=RedditConfig.USERNAME,
                password=RedditConfig.PASSWORD
            )
            # Test connection
            self.reddit.user.me()
            self.logger.info("Reddit client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit client: {e}")
            # Fallback to read-only mode
            self.reddit = praw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT
            )
    
    def get_subreddit_category(self, subreddit_name: str) -> str:
        """Determine category for a subreddit"""
        for category, subreddits in MonitoringConfig.SUBREDDITS.items():
            if subreddit_name.lower() in [s.lower() for s in subreddits]:
                return category
        return 'other'
    
    def _post_to_dataclass(self, post, category: str) -> RedditPost:
        """Convert praw submission to RedditPost dataclass"""
        return RedditPost(
            id=post.id,
            title=post.title,
            author=str(post.author) if post.author else '[deleted]',
            subreddit=str(post.subreddit),
            score=post.score,
            upvote_ratio=post.upvote_ratio,
            num_comments=post.num_comments,
            created_utc=post.created_utc,
            url=post.url,
            selftext=post.selftext,
            flair=post.link_flair_text,
            stickied=post.stickied,
            over_18=post.over_18,
            category=category,
            timestamp_collected=time.time()
        )
    
    def get_hot_posts(self, subreddit_name: str, limit: int = 25) -> List[RedditPost]:
        """Get hot posts from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            category = self.get_subreddit_category(subreddit_name)
            posts = []
            
            for post in subreddit.hot(limit=limit):
                if not post.stickied:  # Skip pinned posts
                    reddit_post = self._post_to_dataclass(post, category)
                    posts.append(reddit_post)
            
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching hot posts from r/{subreddit_name}: {e}")
            return []
    
    def get_new_posts(self, subreddit_name: str, limit: int = 25) -> List[RedditPost]:
        """Get new posts from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            category = self.get_subreddit_category(subreddit_name)
            posts = []
            
            for post in subreddit.new(limit=limit):
                reddit_post = self._post_to_dataclass(post, category)
                posts.append(reddit_post)
            
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching new posts from r/{subreddit_name}: {e}")
            return []
    
    def get_rising_posts(self, subreddit_name: str, limit: int = 25) -> List[RedditPost]:
        """Get rising posts from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            category = self.get_subreddit_category(subreddit_name)
            posts = []
            
            for post in subreddit.rising(limit=limit):
                if not post.stickied:
                    reddit_post = self._post_to_dataclass(post, category)
                    posts.append(reddit_post)
            
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching rising posts from r/{subreddit_name}: {e}")
            return []

class AsyncRedditClient:
    """Asynchronous Reddit client for high-performance operations"""
    
    def __init__(self):
        self.reddit = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._setup_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.reddit:
            await self.reddit.close()
    
    async def _setup_client(self):
        """Initialize async Reddit client"""
        try:
            self.reddit = asyncpraw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT,
                username=RedditConfig.USERNAME,
                password=RedditConfig.PASSWORD
            )
            self.logger.info("Async Reddit client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize async Reddit client: {e}")
            self.reddit = asyncpraw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT
            )
    
    def get_subreddit_category(self, subreddit_name: str) -> str:
        """Determine category for a subreddit"""
        for category, subreddits in MonitoringConfig.SUBREDDITS.items():
            if subreddit_name.lower() in [s.lower() for s in subreddits]:
                return category
        return 'other'
    
    async def _post_to_dataclass(self, post, category: str) -> RedditPost:
        """Convert asyncpraw submission to RedditPost dataclass"""
        return RedditPost(
            id=post.id,
            title=post.title,
            author=str(post.author) if post.author else '[deleted]',
            subreddit=str(post.subreddit),
            score=post.score,
            upvote_ratio=post.upvote_ratio,
            num_comments=post.num_comments,
            created_utc=post.created_utc,
            url=post.url,
            selftext=post.selftext,
            flair=post.link_flair_text,
            stickied=post.stickied,
            over_18=post.over_18,
            category=category,
            timestamp_collected=time.time()
        )
    
    async def get_hot_posts(self, subreddit_name: str, limit: int = 25) -> List[RedditPost]:
        """Get hot posts from a subreddit asynchronously"""
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            category = self.get_subreddit_category(subreddit_name)
            posts = []
            
            async for post in subreddit.hot(limit=limit):
                if not post.stickied:
                    reddit_post = await self._post_to_dataclass(post, category)
                    posts.append(reddit_post)
            
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching hot posts from r/{subreddit_name}: {e}")
            return []
    
    async def get_new_posts(self, subreddit_name: str, limit: int = 25) -> List[RedditPost]:
        """Get new posts from a subreddit asynchronously"""
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            category = self.get_subreddit_category(subreddit_name)
            posts = []
            
            async for post in subreddit.new(limit=limit):
                reddit_post = await self._post_to_dataclass(post, category)
                posts.append(reddit_post)
            
            return posts
        except Exception as e:
            self.logger.error(f"Error fetching new posts from r/{subreddit_name}: {e}")
            return []
    
    async def monitor_subreddits(self, subreddit_names: List[str]) -> AsyncGenerator[List[RedditPost], None]:
        """Monitor multiple subreddits for new posts"""
        while True:
            all_posts = []
            tasks = []
            
            for subreddit_name in subreddit_names:
                # Create tasks for parallel fetching
                tasks.append(self.get_new_posts(subreddit_name, limit=10))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_posts.extend(result)
                else:
                    self.logger.error(f"Error in monitor_subreddits: {result}")
            
            if all_posts:
                yield all_posts
            
            await asyncio.sleep(MonitoringConfig.NEW_POSTS_INTERVAL)