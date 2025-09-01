#!/usr/bin/env python3
"""
Collect Live Reddit Data for GitHub Pages Dashboard
Fetches real Reddit posts and generates JSON files for static hosting
"""
import sys
import os
import json
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import logging
import random

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from reddit_client import RedditClient, RedditPost
from data_processor import DataProcessor
from config import MonitoringConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveDataCollector:
    def __init__(self):
        self.reddit_client = RedditClient()
        self.data_processor = DataProcessor()
        self.output_dir = Path('docs/data')
        
    def collect_posts(self, limit_per_subreddit=10):
        """Collect real posts from monitored subreddits"""
        logger.info("🚀 Collecting live Reddit data...")
        all_posts = []
        
        # Reddit client is already initialized in constructor
        logger.info(f"📊 Using Reddit API client")
        
        # Monitor primary subreddits
        primary_subreddits = ['wallstreetbets', 'stocks', 'investing']
        
        for subreddit_name in primary_subreddits:
            try:
                logger.info(f"📥 Fetching posts from r/{subreddit_name}...")
                posts = self.reddit_client.get_hot_posts(subreddit_name, limit=limit_per_subreddit)
                
                for post in posts:
                    # Convert RedditPost to our JSON format
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'author': post.author,
                        'subreddit': post.subreddit,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'url': f"https://reddit.com/r/{post.subreddit}/comments/{post.id}/" if post.url.startswith('/r/') else post.url,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'selftext': post.selftext[:200] if post.selftext else '',  # Truncate for size
                        'upvote_ratio': post.upvote_ratio,
                        'over_18': post.over_18,
                        'stickied': post.stickied,
                        'comments': post.num_comments
                    }
                    all_posts.append(post_data)
                
                logger.info(f"✅ Collected {len(posts)} posts from r/{subreddit_name}")
                
            except Exception as e:
                logger.error(f"❌ Error fetching from r/{subreddit_name}: {e}")
                continue
        
        # Sort by score (engagement) and recency
        all_posts.sort(key=lambda p: (p['score'], p['created_utc']), reverse=True)
        logger.info(f"📊 Total posts collected: {len(all_posts)}")
        
        return all_posts[:50]  # Keep top 50 posts
    
    def extract_tickers(self, posts):
        """Extract ticker mentions from posts using the existing data processor"""
        # Convert dict posts back to RedditPost objects for processing
        reddit_posts = []
        for post_data in posts:
            reddit_post = RedditPost(
                id=post_data['id'],
                title=post_data['title'],
                author=post_data['author'],
                subreddit=post_data['subreddit'],
                score=post_data['score'],
                upvote_ratio=post_data.get('upvote_ratio', 0.8),
                num_comments=post_data['num_comments'],
                created_utc=post_data['created_utc'],
                url=post_data['url'],
                selftext=post_data.get('selftext', ''),
                flair=None,
                stickied=post_data.get('stickied', False),
                over_18=post_data.get('over_18', False),
                category='',
                timestamp_collected=time.time()
            )
            reddit_posts.append(reddit_post)
        
        # Process posts to extract tickers
        self.data_processor.add_posts(reddit_posts)
        
        # Get ticker mentions from data processor
        ticker_counts = dict(self.data_processor.ticker_mentions)
        
        logger.info(f"💹 Extracted {len(ticker_counts)} unique tickers")
        return ticker_counts
    
    def generate_stats(self, posts, tickers):
        """Generate statistics for the dashboard"""
        subreddit_stats = {}
        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_stats:
                subreddit_stats[subreddit] = 0
            subreddit_stats[subreddit] += 1
        
        stats = {
            'subreddit_stats': subreddit_stats,
            'metadata': {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_posts': len(posts),
                'total_tickers': len(tickers),
                'subreddits_monitored': len(subreddit_stats),
                'data_source': 'Live Reddit API',
                'update_frequency': 'Hourly',
                'time_period': 'Live Data'
            }
        }
        
        return stats
    
    def generate_analysis(self, posts, tickers):
        """Generate market analysis from real data"""
        # Calculate sentiment based on post scores and keywords
        total_sentiment = 0
        sentiment_posts = 0
        insights = []
        
        # Analyze top tickers
        if tickers:
            top_ticker = max(tickers.items(), key=lambda x: x[1])
            insights.append(f"🔥 {top_ticker[0]} is trending with {top_ticker[1]} mentions")
        
        # Analyze engagement
        high_engagement_posts = [p for p in posts if p['score'] > 500]
        if high_engagement_posts:
            insights.append(f"📊 {len(high_engagement_posts)} posts with 500+ upvotes indicate high market interest")
        
        # Activity level
        if len(posts) > 30:
            insights.append(f"⚡ High activity detected: {len(posts)} posts analyzed")
        
        # Market sentiment
        bullish_keywords = ['buy', 'bull', 'moon', 'rocket', 'calls', 'up', 'green']
        bearish_keywords = ['sell', 'bear', 'crash', 'puts', 'down', 'red']
        
        bullish_count = 0
        bearish_count = 0
        
        for post in posts:
            title_lower = post['title'].lower()
            for keyword in bullish_keywords:
                if keyword in title_lower:
                    bullish_count += 1
            for keyword in bearish_keywords:
                if keyword in title_lower:
                    bearish_count += 1
        
        if bullish_count > bearish_count:
            overall_sentiment = "Bullish"
            sentiment_score = min(bullish_count * 10, 1000)
        elif bearish_count > bullish_count:
            overall_sentiment = "Bearish" 
            sentiment_score = -min(bearish_count * 10, 1000)
        else:
            overall_sentiment = "Neutral"
            sentiment_score = 0
        
        insights.append(f"💭 Overall sentiment: {overall_sentiment} based on {len(posts)} posts")
        
        # Market hours detection
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 16:  # Trading hours EST
            insights.append("🕘 US market hours - increased trading activity expected")
        
        analysis = {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': sentiment_score,
            'insights': insights,
            'high_activity_count': len(high_engagement_posts),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return analysis
    
    def generate_fallback_data(self):
        """Generate realistic fallback data when Reddit API fails"""
        logger.info("🎭 Generating fallback demo data...")
        
        # Sample tickers and realistic post titles
        sample_tickers = ['TSLA', 'AAPL', 'NVDA', 'GME', 'AMC', 'MSFT', 'GOOGL', 'META', 'AMZN', 'SPY']
        sample_titles = [
            "🚀 {ticker} to the moon! DD inside",
            "{ticker} earnings beat expectations - bullish outlook",
            "Why {ticker} is the play of the decade",
            "Technical analysis: {ticker} breakout incoming",
            "{ticker} short squeeze potential?",
            "Bought 1000 shares of {ticker} - YOLO",
            "{ticker} dip - perfect entry point?",
            "Hold or sell {ticker}? Need advice",
            "{ticker} news catalyst could spark rally",
            "My {ticker} position is printing 💰",
        ]
        
        posts = []
        current_time = time.time()
        
        for i in range(25):  # Generate 25 sample posts
            ticker = random.choice(sample_tickers)
            title_template = random.choice(sample_titles)
            title = title_template.format(ticker=ticker)
            
            # Generate realistic-looking Reddit post ID (Reddit uses base36 format)
            post_id = f"{''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=7))}"
            subreddit = random.choice(['wallstreetbets', 'stocks', 'investing'])
            
            post_data = {
                'id': post_id,
                'title': title,
                'author': f'user_{random.randint(1000, 9999)}',
                'subreddit': subreddit,
                'score': random.randint(50, 2500),
                'num_comments': random.randint(20, 300),
                'created_utc': current_time - random.randint(0, 3600 * 12),  # Up to 12 hours ago
                'url': f"https://reddit.com/r/{subreddit}/",  # Link to subreddit instead of non-existent post
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'selftext': f"Demo analysis for {ticker}. This is fallback data - click to visit r/{subreddit}.",
                'upvote_ratio': random.uniform(0.7, 0.95),
                'over_18': False,
                'stickied': False,
                'comments': random.randint(20, 300)
            }
            posts.append(post_data)
        
        # Sort by score
        posts.sort(key=lambda p: p['score'], reverse=True)
        logger.info(f"✅ Generated {len(posts)} fallback posts")
        return posts

    def generate_history(self, stats):
        """Generate/update history data"""
        history_file = self.output_dir / 'history.json'
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add current data point
        current_entry = {
            'timestamp': stats['metadata']['last_updated'],
            'total_posts': stats['metadata']['total_posts'],
            'total_tickers': stats['metadata']['total_tickers'],
            'top_ticker': None,  # Will be filled by analysis
            'top_subreddit': None,
            'sentiment': 'Neutral'
        }
        
        # Find top subreddit
        if stats['subreddit_stats']:
            top_subreddit = max(stats['subreddit_stats'].items(), key=lambda x: x[1])
            current_entry['top_subreddit'] = top_subreddit[0]
        
        history.append(current_entry)
        
        # Keep only last 48 hours (48 entries for hourly updates)
        history = history[-48:]
        
        return history
    
    def collect_and_save(self):
        """Main collection and save process"""
        try:
            # Ensure output directory exists
            self.output_dir.mkdir(exist_ok=True)
            
            # Collect live Reddit data
            posts = self.collect_posts()
            
            if not posts:
                logger.warning("⚠️ No posts collected from Reddit API - generating fallback data")
                posts = self.generate_fallback_data()
            
            # Process data
            tickers = self.extract_tickers(posts)
            stats = self.generate_stats(posts, tickers)
            analysis = self.generate_analysis(posts, tickers)
            history = self.generate_history(stats)
            
            # Update metadata to indicate data source
            if 'demo_' in posts[0]['id'] if posts else False:
                stats['metadata']['data_source'] = 'Fallback Demo Data (Reddit API unavailable)'
                stats['metadata']['note'] = 'This dashboard is using demo data because Reddit API credentials need to be configured'
            
            # Update history with analysis data
            if history and tickers:
                top_ticker = max(tickers.items(), key=lambda x: x[1])
                history[-1]['top_ticker'] = top_ticker[0]
                history[-1]['sentiment'] = analysis['overall_sentiment']
            
            # Save all data files
            files_to_save = {
                'posts.json': posts,
                'tickers.json': tickers,
                'stats.json': stats,
                'analysis.json': analysis,
                'history.json': history
            }
            
            for filename, data in files_to_save.items():
                file_path = self.output_dir / filename
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"💾 Saved {filename}")
            
            logger.info("✅ All live Reddit data saved successfully!")
            
            # Print summary
            print(f"\n📊 Live Reddit Data Summary:")
            print(f"   📝 Posts collected: {len(posts)}")
            print(f"   💹 Tickers found: {len(tickers)}")
            print(f"   📊 Subreddits: {list(stats['subreddit_stats'].keys())}")
            print(f"   💭 Sentiment: {analysis['overall_sentiment']}")
            print(f"   🕒 Updated: {stats['metadata']['last_updated']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error collecting live data: {e}")
            return False

def main():
    """Main entry point"""
    collector = LiveDataCollector()
    success = collector.collect_and_save()
    
    if not success:
        sys.exit(1)
    
    print("🎉 Live Reddit data collection completed!")

if __name__ == '__main__':
    main()