"""
Data Processing and Analysis Module for Reddit Posts
"""
import re
import json
import asyncio
import aiofiles
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timezone
import time
import logging
import os
from dataclasses import asdict

from reddit_client import RedditPost
from config import MonitoringConfig, DataConfig

class DataProcessor:
    """Process and analyze Reddit posts for insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.posts_buffer: List[RedditPost] = []
        self.ticker_mentions: Counter = Counter()
        self.sentiment_scores: Dict[str, float] = {}
        self.trending_keywords: Counter = Counter()
        self.subreddit_activity: Dict[str, Dict] = defaultdict(lambda: {
            'posts': [],
            'total_score': 0,
            'total_comments': 0,
            'speculative_count': 0
        })
        
        # Compile regex patterns for better performance
        self._compile_patterns()
        self._ensure_directories()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        self.ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b')
        self.priority_patterns = [
            re.compile(pattern) for pattern in MonitoringConfig.PRIORITY_PATTERNS
        ]
        self.speculative_pattern = re.compile(
            '|'.join(MonitoringConfig.SPECULATIVE_KEYWORDS),
            re.IGNORECASE
        )
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [DataConfig.DATA_DIR, DataConfig.EXPORTS_DIR, DataConfig.LOGS_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def add_posts(self, posts: List[RedditPost]):
        """Add posts to the processing buffer"""
        self.posts_buffer.extend(posts)
        
        # Process posts for immediate insights
        for post in posts:
            self._extract_tickers(post)
            self._analyze_sentiment(post)
            self._update_subreddit_activity(post)
    
    def _extract_tickers(self, post: RedditPost):
        """Extract stock tickers from post content"""
        content = f"{post.title} {post.selftext}".upper()
        tickers = self.ticker_pattern.findall(content)
        
        for ticker in tickers:
            if len(ticker) <= 5:  # Valid ticker length
                self.ticker_mentions[ticker] += 1
                self.logger.debug(f"Ticker ${ticker} mentioned in r/{post.subreddit}")
    
    def _analyze_sentiment(self, post: RedditPost):
        """Basic sentiment analysis based on keywords"""
        content = f"{post.title} {post.selftext}".lower()
        
        # Simple sentiment scoring
        positive_words = ['buy', 'bull', 'moon', 'rocket', 'strong', 'growth', 'profit']
        negative_words = ['sell', 'bear', 'crash', 'dump', 'loss', 'decline', 'drop']
        
        positive_score = sum(1 for word in positive_words if word in content)
        negative_score = sum(1 for word in negative_words if word in content)
        
        # Normalize score (-1 to 1)
        total_words = len(content.split())
        if total_words > 0:
            sentiment = (positive_score - negative_score) / max(total_words / 10, 1)
            self.sentiment_scores[post.id] = max(-1, min(1, sentiment))
    
    def _update_subreddit_activity(self, post: RedditPost):
        """Update activity metrics for subreddit"""
        activity = self.subreddit_activity[post.subreddit]
        activity['posts'].append({
            'id': post.id,
            'score': post.score,
            'comments': post.num_comments,
            'timestamp': post.created_utc
        })
        activity['total_score'] += post.score
        activity['total_comments'] += post.num_comments
        
        if self.is_speculative_post(post):
            activity['speculative_count'] += 1
    
    def is_speculative_post(self, post: RedditPost) -> bool:
        """Determine if a post contains speculative content"""
        content = f"{post.title} {post.selftext}".lower()
        
        # Check for speculative keywords
        if self.speculative_pattern.search(content):
            return True
        
        # Check for high score with rapid growth (rising posts with high engagement)
        if post.score > 100 and post.num_comments > 50:
            post_age_hours = (time.time() - post.created_utc) / 3600
            if post_age_hours < 6:  # Recent post with high engagement
                return True
        
        # Check for options-related content
        options_keywords = ['calls', 'puts', 'strike', 'expiry', 'iv', 'theta']
        if any(keyword in content for keyword in options_keywords):
            return True
        
        return False
    
    def filter_priority_posts(self, posts: List[RedditPost]) -> List[RedditPost]:
        """Filter posts that match priority patterns"""
        priority_posts = []
        
        for post in posts:
            content = f"{post.title} {post.selftext}"
            
            # Check against priority patterns
            for pattern in self.priority_patterns:
                if pattern.search(content):
                    priority_posts.append(post)
                    break
            
            # High engagement posts
            elif post.score > 500 or post.num_comments > 200:
                priority_posts.append(post)
            
            # Rapid growth detection
            elif self._is_trending_post(post):
                priority_posts.append(post)
        
        return priority_posts
    
    def _is_trending_post(self, post: RedditPost) -> bool:
        """Detect if a post is trending based on engagement rate"""
        post_age_hours = (time.time() - post.created_utc) / 3600
        
        if post_age_hours < 1:  # Very recent posts
            return post.score > 50 or post.num_comments > 20
        elif post_age_hours < 6:  # Recent posts
            return post.score > 200 or post.num_comments > 75
        
        return False
    
    def get_trending_tickers(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most mentioned tickers"""
        return self.ticker_mentions.most_common(top_n)
    
    def get_subreddit_insights(self) -> Dict[str, Dict]:
        """Get insights for each monitored subreddit"""
        insights = {}
        
        for subreddit, activity in self.subreddit_activity.items():
            posts = activity['posts']
            if not posts:
                continue
            
            # Calculate metrics
            avg_score = activity['total_score'] / len(posts) if posts else 0
            avg_comments = activity['total_comments'] / len(posts) if posts else 0
            speculative_ratio = activity['speculative_count'] / len(posts) if posts else 0
            
            # Recent activity (last hour)
            recent_posts = [
                p for p in posts 
                if (time.time() - p['timestamp']) < 3600
            ]
            
            insights[subreddit] = {
                'total_posts': len(posts),
                'avg_score': round(avg_score, 2),
                'avg_comments': round(avg_comments, 2),
                'speculative_ratio': round(speculative_ratio, 3),
                'recent_activity': len(recent_posts),
                'category': self._get_subreddit_category(subreddit)
            }
        
        return insights
    
    def _get_subreddit_category(self, subreddit: str) -> str:
        """Get category for a subreddit"""
        for category, subreddits in MonitoringConfig.SUBREDDITS.items():
            if subreddit.lower() in [s.lower() for s in subreddits]:
                return category
        return 'other'
    
    def export_for_analysis(self) -> Dict:
        """Export data in format suitable for upper-level analysis"""
        # Clean old data first
        self._cleanup_old_data()
        
        export_data = {
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'total_posts': len(self.posts_buffer),
                'data_window_hours': DataConfig.DATA_RETENTION_HOURS,
                'monitoring_interval': {
                    'hot_posts': MonitoringConfig.HOT_POSTS_INTERVAL,
                    'new_posts': MonitoringConfig.NEW_POSTS_INTERVAL,
                    'rising_posts': MonitoringConfig.RISING_POSTS_INTERVAL
                }
            },
            'trending_tickers': dict(self.get_trending_tickers(20)),
            'subreddit_insights': self.get_subreddit_insights(),
            'recent_priority_posts': self._get_recent_priority_posts(),
            'sentiment_analysis': self._get_sentiment_summary(),
            'activity_summary': self._get_activity_summary()
        }
        
        return export_data
    
    def _cleanup_old_data(self):
        """Remove data older than retention period"""
        cutoff_time = time.time() - (DataConfig.DATA_RETENTION_HOURS * 3600)
        
        # Clean posts buffer
        self.posts_buffer = [
            post for post in self.posts_buffer 
            if post.timestamp_collected > cutoff_time
        ]
        
        # Clean subreddit activity
        for subreddit, activity in self.subreddit_activity.items():
            activity['posts'] = [
                post for post in activity['posts']
                if post['timestamp'] > cutoff_time
            ]
    
    def _get_recent_priority_posts(self) -> List[Dict]:
        """Get recent high-priority posts"""
        cutoff_time = time.time() - 3600  # Last hour
        recent_posts = [
            post for post in self.posts_buffer
            if post.timestamp_collected > cutoff_time
        ]
        
        priority_posts = self.filter_priority_posts(recent_posts)
        
        return [
            {
                'id': post.id,
                'title': post.title,
                'subreddit': post.subreddit,
                'score': post.score,
                'comments': post.num_comments,
                'url': post.url,
                'created_utc': post.created_utc,
                'category': post.category,
                'sentiment': self.sentiment_scores.get(post.id, 0),
                'is_speculative': self.is_speculative_post(post)
            }
            for post in priority_posts[:50]  # Limit to top 50
        ]
    
    def _get_sentiment_summary(self) -> Dict:
        """Get overall sentiment analysis summary"""
        if not self.sentiment_scores:
            return {'average': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
        
        sentiments = list(self.sentiment_scores.values())
        positive = len([s for s in sentiments if s > 0.1])
        negative = len([s for s in sentiments if s < -0.1])
        neutral = len(sentiments) - positive - negative
        
        return {
            'average': round(sum(sentiments) / len(sentiments), 3),
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'total': len(sentiments)
        }
    
    def _get_activity_summary(self) -> Dict:
        """Get overall activity summary"""
        total_posts = len(self.posts_buffer)
        total_speculative = sum(
            1 for post in self.posts_buffer 
            if self.is_speculative_post(post)
        )
        
        # Calculate posting rate (posts per hour)
        if self.posts_buffer:
            oldest_post = min(self.posts_buffer, key=lambda p: p.timestamp_collected)
            time_span = time.time() - oldest_post.timestamp_collected
            posting_rate = (total_posts / max(time_span / 3600, 1)) if time_span > 0 else 0
        else:
            posting_rate = 0
        
        return {
            'total_posts': total_posts,
            'speculative_posts': total_speculative,
            'speculative_ratio': round(total_speculative / total_posts, 3) if total_posts > 0 else 0,
            'posting_rate_per_hour': round(posting_rate, 2),
            'active_subreddits': len(self.subreddit_activity),
            'unique_tickers_mentioned': len(self.ticker_mentions)
        }
    
    async def save_export_data(self, data: Dict, filename: str):
        """Save export data to file asynchronously"""
        filepath = os.path.join(DataConfig.EXPORTS_DIR, filename)
        
        try:
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
            
            self.logger.info(f"Data exported successfully to {filepath}")
            
            # Also save a latest.json for easy access
            latest_path = os.path.join(DataConfig.EXPORTS_DIR, 'latest.json')
            async with aiofiles.open(latest_path, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
                
        except Exception as e:
            self.logger.error(f"Failed to save export data: {e}")
    
    def get_stats(self) -> Dict:
        """Get current processing statistics"""
        return {
            'posts_in_buffer': len(self.posts_buffer),
            'unique_tickers': len(self.ticker_mentions),
            'posts_with_sentiment': len(self.sentiment_scores),
            'active_subreddits': len(self.subreddit_activity),
            'top_ticker': self.ticker_mentions.most_common(1)[0] if self.ticker_mentions else None
        }