#!/usr/bin/env python3
"""
GitHub Actions Reddit Data Fetcher
Fetches Reddit data every hour and saves to static JSON files
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import praw
    print("✅ PRAW imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PRAW: {e}")
    sys.exit(1)

# For GitHub Actions, we'll use PRAW directly instead of our custom client
def create_reddit_client():
    """Create Reddit client using environment variables"""
    reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET') 
    reddit_user_agent = os.getenv('REDDIT_USER_AGENT')
    
    if not all([reddit_client_id, reddit_client_secret, reddit_user_agent]):
        print("❌ Missing Reddit API credentials in environment variables")
        return None
    
    try:
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
        
        # Test the connection
        reddit.user.me()  # This will fail if credentials are wrong
        return reddit
        
    except Exception as e:
        print(f"❌ Failed to create Reddit client: {e}")
        return None

def ensure_data_directory():
    """Create docs/data directory if it doesn't exist"""
    data_dir = Path("docs/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def fetch_reddit_data():
    """Fetch fresh Reddit data from multiple subreddits"""
    print("🚀 Starting Reddit data fetch...")
    
    # Initialize Reddit client
    reddit = create_reddit_client()
    if not reddit:
        return None
    
    print("✅ Reddit client initialized")
    
    # Subreddits to monitor
    subreddits = [
        'wallstreetbets',
        'stocks', 
        'investing',
        'options',
        'pennystocks',
        'StockMarket',
        'SecurityAnalysis',
        'ValueInvesting'
    ]
    
    all_posts = []
    ticker_mentions = Counter()
    subreddit_stats = defaultdict(int)
    
    print(f"📡 Fetching from {len(subreddits)} subreddits...")
    
    for subreddit in subreddits:
        try:
            print(f"  📊 Processing r/{subreddit}...")
            
            # Fetch hot posts using PRAW
            subreddit_obj = reddit.subreddit(subreddit)
            posts = list(subreddit_obj.hot(limit=25))
            
            for post in posts:
                # Convert post to dict for JSON serialization
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'subreddit': post.subreddit,
                    'author': str(post.author) if post.author else '[deleted]',
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'created_utc': post.created_utc,
                    'url': post.url,
                    'selftext': post.selftext[:500] if post.selftext else '',  # Limit text length
                    'timestamp': datetime.now().isoformat()
                }
                
                all_posts.append(post_data)
                
                # Extract tickers from title and text
                text_to_analyze = f"{post.title} {post.selftext}"
                tickers = re.findall(r'\$([A-Z]{1,5})\b', text_to_analyze)
                
                for ticker in tickers:
                    ticker_mentions[f"${ticker}"] += 1
                
                subreddit_stats[subreddit] += 1
            
            print(f"    ✅ Found {len(posts)} posts")
            
        except Exception as e:
            print(f"    ❌ Error fetching r/{subreddit}: {e}")
            continue
    
    # Sort posts by score (popularity)
    all_posts.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit to top 100 posts to keep file size reasonable
    all_posts = all_posts[:100]
    
    print(f"✅ Collected {len(all_posts)} posts total")
    print(f"📈 Found {len(ticker_mentions)} unique tickers")
    
    return {
        'posts': all_posts,
        'tickers': dict(ticker_mentions.most_common(50)),  # Top 50 tickers
        'subreddit_stats': dict(subreddit_stats),
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'total_tickers': len(ticker_mentions),
            'subreddits_monitored': len(subreddits),
            'data_source': 'GitHub Actions',
            'update_frequency': 'Hourly'
        }
    }

def calculate_trending_analysis(data):
    """Calculate trending analysis and insights"""
    posts = data['posts']
    tickers = data['tickers']
    
    # Market sentiment analysis
    bullish_keywords = ['bull', 'moon', 'rocket', 'calls', 'buy', 'long', 'bullish', '🚀', '📈']
    bearish_keywords = ['bear', 'crash', 'puts', 'sell', 'short', 'bearish', '📉', '💩']
    
    sentiment_score = 0
    total_sentiment_posts = 0
    
    for post in posts:
        text = (post['title'] + ' ' + post.get('selftext', '')).lower()
        
        bull_count = sum(1 for keyword in bullish_keywords if keyword in text)
        bear_count = sum(1 for keyword in bearish_keywords if keyword in text)
        
        if bull_count > 0 or bear_count > 0:
            sentiment_score += (bull_count - bear_count) * post['score']
            total_sentiment_posts += 1
    
    # Calculate overall sentiment
    if total_sentiment_posts > 0:
        avg_sentiment = sentiment_score / total_sentiment_posts
        if avg_sentiment > 10:
            overall_sentiment = 'Bullish'
        elif avg_sentiment < -10:
            overall_sentiment = 'Bearish'
        else:
            overall_sentiment = 'Neutral'
    else:
        overall_sentiment = 'Neutral'
    
    # Top trending analysis
    insights = []
    
    if tickers:
        top_ticker = max(tickers.items(), key=lambda x: x[1])
        insights.append(f"🔥 {top_ticker[0]} is trending with {top_ticker[1]} mentions")
    
    high_activity_posts = [p for p in posts if p['score'] > 1000]
    if high_activity_posts:
        insights.append(f"📊 {len(high_activity_posts)} posts with 1000+ upvotes indicate high market interest")
    
    if overall_sentiment != 'Neutral':
        insights.append(f"💭 Overall sentiment: {overall_sentiment} based on {total_sentiment_posts} posts")
    
    return {
        'overall_sentiment': overall_sentiment,
        'sentiment_score': sentiment_score,
        'insights': insights,
        'high_activity_count': len(high_activity_posts),
        'analysis_timestamp': datetime.now().isoformat()
    }

def save_data_files(data, data_dir):
    """Save data to multiple JSON files"""
    timestamp = datetime.now()
    
    # Main data file
    main_file = data_dir / 'reddit_data.json'
    with open(main_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved main data to {main_file}")
    
    # Individual component files for faster loading
    components = {
        'posts.json': data['posts'],
        'tickers.json': data['tickers'],
        'stats.json': {
            'subreddit_stats': data['subreddit_stats'],
            'metadata': data['metadata']
        }
    }
    
    for filename, component_data in components.items():
        file_path = data_dir / filename
        with open(file_path, 'w') as f:
            json.dump(component_data, f, indent=2)
        print(f"💾 Saved {filename}")
    
    # Trending analysis
    analysis = calculate_trending_analysis(data)
    analysis_file = data_dir / 'analysis.json'
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"💾 Saved analysis to {analysis_file}")
    
    # Historical summary (keep last 24 hours)
    history_file = data_dir / 'history.json'
    
    # Load existing history
    history_data = []
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        except:
            history_data = []
    
    # Add current snapshot
    snapshot = {
        'timestamp': timestamp.isoformat(),
        'total_posts': len(data['posts']),
        'total_tickers': len(data['tickers']),
        'top_ticker': max(data['tickers'].items(), key=lambda x: x[1])[0] if data['tickers'] else None,
        'top_subreddit': max(data['subreddit_stats'].items(), key=lambda x: x[1])[0] if data['subreddit_stats'] else None,
        'sentiment': analysis['overall_sentiment']
    }
    
    history_data.append(snapshot)
    
    # Keep only last 24 hours
    cutoff_time = timestamp - timedelta(hours=24)
    history_data = [
        h for h in history_data 
        if datetime.fromisoformat(h['timestamp']) > cutoff_time
    ]
    
    with open(history_file, 'w') as f:
        json.dump(history_data, f, indent=2)
    print(f"💾 Saved history ({len(history_data)} entries)")

def main():
    """Main execution function"""
    print("🤖 GitHub Actions Reddit Data Fetcher")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these as GitHub repository secrets")
        sys.exit(1)
    
    # Create data directory
    data_dir = ensure_data_directory()
    
    # Fetch data
    data = fetch_reddit_data()
    
    if not data:
        print("❌ Failed to fetch Reddit data")
        sys.exit(1)
    
    # Save data files
    save_data_files(data, data_dir)
    
    print("=" * 50)
    print("✅ Reddit data fetch completed successfully!")
    print(f"📊 Data saved to: docs/data/")
    print(f"🕐 Next update: {datetime.now() + timedelta(hours=1)}")

if __name__ == "__main__":
    main()