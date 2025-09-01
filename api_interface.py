"""
API Interface for Upper-Level Analysis Integration
"""
import json
import asyncio
import aiofiles
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from data_processor import DataProcessor
from reddit_client import RedditClient, AsyncRedditClient
from config import DataConfig, MonitoringConfig

class AnalysisAPI:
    """API interface for external analysis systems"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processor = DataProcessor()
        self.sync_client = RedditClient()
        
    async def get_latest_data(self) -> Optional[Dict]:
        """Get the most recent exported data"""
        try:
            latest_file = Path(DataConfig.EXPORTS_DIR) / 'latest.json'
            if latest_file.exists():
                async with aiofiles.open(latest_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            return None
        except Exception as e:
            self.logger.error(f"Error reading latest data: {e}")
            return None
    
    async def get_trending_tickers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get currently trending stock tickers"""
        data = await self.get_latest_data()
        if not data or 'trending_tickers' not in data:
            return []
        
        tickers = data['trending_tickers']
        return [
            {
                'ticker': ticker,
                'mentions': count,
                'rank': idx + 1
            }
            for idx, (ticker, count) in enumerate(
                sorted(tickers.items(), key=lambda x: x[1], reverse=True)[:limit]
            )
        ]
    
    async def get_subreddit_activity(self, subreddit: Optional[str] = None) -> Dict[str, Any]:
        """Get activity data for specific subreddit or all subreddits"""
        data = await self.get_latest_data()
        if not data or 'subreddit_insights' not in data:
            return {}
        
        insights = data['subreddit_insights']
        
        if subreddit:
            return insights.get(subreddit, {})
        
        return insights
    
    async def get_priority_posts(self, 
                                category: Optional[str] = None,
                                limit: int = 20) -> List[Dict[str, Any]]:
        """Get high-priority posts, optionally filtered by category"""
        data = await self.get_latest_data()
        if not data or 'recent_priority_posts' not in data:
            return []
        
        posts = data['recent_priority_posts']
        
        if category:
            posts = [post for post in posts if post.get('category') == category]
        
        return posts[:limit]
    
    async def get_speculative_signals(self) -> Dict[str, Any]:
        """Get signals indicating speculative trading activity"""
        data = await self.get_latest_data()
        if not data:
            return {}
        
        # Extract speculative indicators
        activity = data.get('activity_summary', {})
        priority_posts = data.get('recent_priority_posts', [])
        
        speculative_posts = [
            post for post in priority_posts 
            if post.get('is_speculative', False)
        ]
        
        # Get most active speculative subreddits
        subreddit_insights = data.get('subreddit_insights', {})
        speculative_subreddits = [
            {
                'subreddit': name,
                'speculative_ratio': info.get('speculative_ratio', 0),
                'recent_activity': info.get('recent_activity', 0)
            }
            for name, info in subreddit_insights.items()
            if info.get('speculative_ratio', 0) > 0.1
        ]
        
        return {
            'total_speculative_posts': activity.get('speculative_posts', 0),
            'speculative_ratio': activity.get('speculative_ratio', 0),
            'recent_speculative_posts': speculative_posts[:10],
            'active_speculative_subreddits': sorted(
                speculative_subreddits,
                key=lambda x: x['speculative_ratio'],
                reverse=True
            )[:5]
        }
    
    async def get_sentiment_overview(self) -> Dict[str, Any]:
        """Get overall market sentiment from Reddit posts"""
        data = await self.get_latest_data()
        if not data or 'sentiment_analysis' not in data:
            return {}
        
        sentiment = data['sentiment_analysis']
        
        # Add interpretation
        avg_sentiment = sentiment.get('average', 0)
        if avg_sentiment > 0.2:
            mood = 'bullish'
        elif avg_sentiment < -0.2:
            mood = 'bearish'
        else:
            mood = 'neutral'
        
        return {
            **sentiment,
            'mood': mood,
            'confidence': abs(avg_sentiment)
        }
    
    async def get_real_time_feed(self, 
                                categories: Optional[List[str]] = None,
                                min_score: int = 50) -> List[Dict[str, Any]]:
        """Get real-time feed of posts matching criteria"""
        try:
            # Get fresh data from Reddit
            posts = []
            target_subreddits = MonitoringConfig.ALL_SUBREDDITS
            
            if categories:
                target_subreddits = []
                for category in categories:
                    if category in MonitoringConfig.SUBREDDITS:
                        target_subreddits.extend(MonitoringConfig.SUBREDDITS[category])
            
            # Fetch recent posts
            for subreddit in target_subreddits[:5]:  # Limit to prevent rate limiting
                try:
                    subreddit_posts = self.sync_client.get_hot_posts(subreddit, limit=10)
                    filtered_posts = [
                        post for post in subreddit_posts
                        if post.score >= min_score and post.is_recent(2)  # Last 2 hours
                    ]
                    posts.extend(filtered_posts)
                except Exception as e:
                    self.logger.warning(f"Error fetching from r/{subreddit}: {e}")
            
            # Convert to API format
            return [
                {
                    'id': post.id,
                    'title': post.title,
                    'subreddit': post.subreddit,
                    'author': post.author,
                    'score': post.score,
                    'comments': post.num_comments,
                    'url': post.url,
                    'created_utc': post.created_utc,
                    'category': post.category,
                    'upvote_ratio': post.upvote_ratio
                }
                for post in sorted(posts, key=lambda x: x.score, reverse=True)[:20]
            ]
            
        except Exception as e:
            self.logger.error(f"Error in real-time feed: {e}")
            return []
    
    async def export_custom_data(self, 
                                subreddits: List[str],
                                hours_back: int = 24,
                                min_engagement: int = 10) -> Dict[str, Any]:
        """Export custom dataset based on specific criteria"""
        try:
            all_posts = []
            
            async with AsyncRedditClient() as client:
                tasks = []
                for subreddit in subreddits:
                    # Get multiple post types for comprehensive data
                    tasks.extend([
                        client.get_hot_posts(subreddit, limit=50),
                        client.get_new_posts(subreddit, limit=100),
                        client.get_rising_posts(subreddit, limit=25)
                    ])
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        all_posts.extend(result)
            
            # Filter posts
            filtered_posts = []
            for post in all_posts:
                if (post.is_recent(hours_back) and 
                    post.score >= min_engagement and
                    post.id not in [p.id for p in filtered_posts]):  # Deduplicate
                    filtered_posts.append(post)
            
            # Process through data processor for analysis
            self.data_processor.add_posts(filtered_posts)
            
            return {
                'metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'subreddits_requested': subreddits,
                    'hours_back': hours_back,
                    'min_engagement': min_engagement,
                    'total_posts': len(filtered_posts)
                },
                'posts': [
                    {
                        'id': post.id,
                        'title': post.title,
                        'subreddit': post.subreddit,
                        'score': post.score,
                        'comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'url': post.url,
                        'selftext': post.selftext[:500] if post.selftext else '',
                        'category': post.category,
                        'is_speculative': self.data_processor.is_speculative_post(post)
                    }
                    for post in sorted(filtered_posts, key=lambda x: x.score, reverse=True)
                ],
                'trending_tickers': dict(self.data_processor.get_trending_tickers(10)),
                'summary': {
                    'total_posts': len(filtered_posts),
                    'speculative_posts': sum(
                        1 for post in filtered_posts 
                        if self.data_processor.is_speculative_post(post)
                    ),
                    'avg_score': sum(post.score for post in filtered_posts) / len(filtered_posts) if filtered_posts else 0,
                    'subreddit_distribution': dict(Counter(post.subreddit for post in filtered_posts))
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in custom export: {e}")
            return {'error': str(e)}

class SimpleAPI:
    """Simplified API for quick data access"""
    
    def __init__(self):
        self.api = AnalysisAPI()
    
    async def get_hot_tickers(self, limit: int = 5) -> List[str]:
        """Get list of hottest ticker symbols"""
        tickers = await self.api.get_trending_tickers(limit)
        return [ticker['ticker'] for ticker in tickers]
    
    async def get_market_mood(self) -> str:
        """Get simple market mood indicator"""
        sentiment = await self.api.get_sentiment_overview()
        return sentiment.get('mood', 'neutral')
    
    async def get_yolo_activity(self) -> Dict[str, int]:
        """Get YOLO/meme stock activity level"""
        activity = await self.api.get_subreddit_activity('wallstreetbets')
        return {
            'recent_posts': activity.get('recent_activity', 0),
            'speculative_ratio': int(activity.get('speculative_ratio', 0) * 100)
        }
    
    async def alert_check(self) -> Dict[str, Any]:
        """Check for alert-worthy conditions"""
        signals = await self.api.get_speculative_signals()
        sentiment = await self.api.get_sentiment_overview()
        
        alerts = []
        
        # High speculative activity
        if signals.get('speculative_ratio', 0) > 0.3:
            alerts.append({
                'type': 'high_speculation',
                'message': f"High speculative activity: {signals['speculative_ratio']:.1%}",
                'severity': 'warning'
            })
        
        # Extreme sentiment
        if abs(sentiment.get('average', 0)) > 0.5:
            mood = 'very bullish' if sentiment['average'] > 0 else 'very bearish'
            alerts.append({
                'type': 'extreme_sentiment',
                'message': f"Market sentiment is {mood}",
                'severity': 'info'
            })
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'alerts': alerts,
            'alert_count': len(alerts)
        }

# Convenience function for external integration
async def get_reddit_insights() -> Dict[str, Any]:
    """Quick function to get current Reddit market insights"""
    api = AnalysisAPI()
    
    return {
        'trending_tickers': await api.get_trending_tickers(10),
        'market_sentiment': await api.get_sentiment_overview(),
        'speculative_signals': await api.get_speculative_signals(),
        'priority_posts': await api.get_priority_posts(limit=10)
    }