#!/usr/bin/env python3
"""
Reddit Data Engine - Main Entry Point
Fast real-time Reddit data collection and analysis for investment subreddits
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

from monitor import RedditMonitor
from api_interface import AnalysisAPI, SimpleAPI, get_reddit_insights
from reddit_client import RedditClient
from config import MonitoringConfig

def setup_logging(level: str = 'INFO'):
    """Setup logging configuration"""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('reddit_engine.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def run_monitor():
    """Run the real-time monitoring system"""
    print("🚀 Starting Reddit Data Engine - Real-time Monitor")
    print(f"📊 Monitoring {len(MonitoringConfig.ALL_SUBREDDITS)} subreddits:")
    for category, subreddits in MonitoringConfig.SUBREDDITS.items():
        print(f"  {category}: {', '.join(subreddits)}")
    print()
    
    monitor = RedditMonitor()
    await monitor.start_monitoring()

async def test_connection():
    """Test Reddit API connection"""
    print("🔗 Testing Reddit API connection...")
    try:
        client = RedditClient()
        
        # Test basic connection
        print("✅ Reddit client initialized")
        
        # Test subreddit access - try multiple subreddits
        test_subreddits = ['python', 'programming', 'technology']
        successful_fetches = 0
        total_posts = 0
        
        for subreddit in test_subreddits:
            posts = client.get_hot_posts(subreddit, limit=5)
            if posts:
                successful_fetches += 1
                total_posts += len(posts)
                print(f"✅ Fetched {len(posts)} posts from r/{subreddit}")
                
                # Show sample from first successful fetch
                if successful_fetches == 1:
                    sample_post = posts[0]
                    print(f"\n📄 Sample post: '{sample_post.title[:60]}...'")
                    print(f"   Score: {sample_post.score}, Comments: {sample_post.num_comments}")
            else:
                print(f"⚠️  Could not fetch posts from r/{subreddit}")
        
        if successful_fetches > 0:
            print(f"\n🎉 Connection test successful!")
            print(f"📊 Fetched {total_posts} posts from {successful_fetches}/{len(test_subreddits)} subreddits")
            return True
        else:
            print("\n❌ Connection test failed: Could not fetch posts from any subreddit")
            print("Please check:")
            print("  1. Your Reddit API credentials in .env file")
            print("  2. Client ID and Secret are correct")
            print("  3. The app type is 'script' in Reddit settings")
            return False
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def show_current_insights():
    """Display current market insights from Reddit"""
    print("📈 Fetching current Reddit market insights...\n")
    
    try:
        insights = await get_reddit_insights()
        
        # Trending tickers
        print("🔥 TRENDING TICKERS:")
        tickers = insights.get('trending_tickers', [])
        if tickers:
            for i, ticker_data in enumerate(tickers[:5], 1):
                ticker = ticker_data['ticker']
                mentions = ticker_data['mentions']
                print(f"  {i}. ${ticker} ({mentions} mentions)")
        else:
            print("  No trending tickers found")
        
        print()
        
        # Market sentiment
        print("💭 MARKET SENTIMENT:")
        sentiment = insights.get('market_sentiment', {})
        if sentiment:
            mood = sentiment.get('mood', 'neutral')
            avg = sentiment.get('average', 0)
            total = sentiment.get('total', 0)
            print(f"  Overall mood: {mood.upper()}")
            print(f"  Sentiment score: {avg:.3f}")
            print(f"  Posts analyzed: {total}")
        else:
            print("  No sentiment data available")
        
        print()
        
        # Priority posts
        print("⚡ RECENT PRIORITY POSTS:")
        priority_posts = insights.get('priority_posts', [])
        if priority_posts:
            for i, post in enumerate(priority_posts[:3], 1):
                title = post['title'][:60] + '...' if len(post['title']) > 60 else post['title']
                print(f"  {i}. r/{post['subreddit']}: {title}")
                print(f"     Score: {post['score']}, Comments: {post['comments']}")
        else:
            print("  No priority posts found")
        
    except Exception as e:
        print(f"❌ Error fetching insights: {e}")

async def export_custom_data(subreddits: list, hours: int):
    """Export custom data for specific subreddits"""
    print(f"📤 Exporting data for subreddits: {', '.join(subreddits)}")
    print(f"⏰ Time window: {hours} hours")
    
    api = AnalysisAPI()
    
    try:
        data = await api.export_custom_data(
            subreddits=subreddits,
            hours_back=hours,
            min_engagement=10
        )
        
        if 'error' in data:
            print(f"❌ Export failed: {data['error']}")
            return
        
        # Save to file
        timestamp = data['metadata']['timestamp'].replace(':', '-').split('.')[0]
        filename = f"custom_export_{timestamp}.json"
        
        import json
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Data exported to {filename}")
        print(f"📊 Total posts: {data['metadata']['total_posts']}")
        
        if 'trending_tickers' in data:
            print("🔥 Top tickers in export:")
            for ticker, count in list(data['trending_tickers'].items())[:5]:
                print(f"  ${ticker}: {count} mentions")
    
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Reddit Data Engine - Real-time market sentiment analysis'
    )
    parser.add_argument(
        'command',
        choices=['monitor', 'test', 'insights', 'export'],
        help='Command to run'
    )
    parser.add_argument(
        '--subreddits',
        nargs='+',
        default=['stocks', 'investing'],
        help='Subreddits to monitor/export (for export command)'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of data to export (for export command)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    try:
        if args.command == 'monitor':
            asyncio.run(run_monitor())
        elif args.command == 'test':
            asyncio.run(test_connection())
        elif args.command == 'insights':
            asyncio.run(show_current_insights())
        elif args.command == 'export':
            asyncio.run(export_custom_data(args.subreddits, args.hours))
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()