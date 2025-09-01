#!/usr/bin/env python3
"""
Generate sample data for GitHub Pages demonstration
Creates realistic Reddit data that shows past hour activity
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate_realistic_posts(hours_back=1):
    """Generate realistic Reddit posts for the past hour"""
    posts = []
    now = datetime.now()
    
    # Realistic subreddits and their typical activity levels
    subreddit_weights = {
        'wallstreetbets': 0.35,
        'stocks': 0.20,
        'investing': 0.15,
        'options': 0.10,
        'pennystocks': 0.08,
        'StockMarket': 0.06,
        'SecurityAnalysis': 0.03,
        'ValueInvesting': 0.03
    }
    
    # Sample realistic post titles with tickers
    post_templates = [
        ("$AAPL earnings beat expectations by 15% - calls printing! 🚀", "wallstreetbets", 1200, 340),
        ("Tesla $TSLA production numbers exceed Q4 estimates", "stocks", 890, 187),
        ("NVIDIA $NVDA announces next-gen AI chip breakthrough", "investing", 756, 134),
        ("Microsoft $MSFT cloud revenue up 32% YoY - bullish outlook", "stocks", 623, 89),
        ("$GME short interest drops to lowest level since 2021", "wallstreetbets", 2847, 891),
        ("Amazon $AMZN logistics expansion into rural markets", "investing", 445, 67),
        ("Google $GOOGL AI integration across all products", "stocks", 578, 123),
        ("PayPal $PYPL crypto integration drives user adoption", "investing", 334, 78),
        ("$TSLA Cybertruck production ramp exceeding targets", "wallstreetbets", 1456, 412),
        ("Netflix $NFLX content spending reaches new highs", "stocks", 267, 45),
        ("Advanced Micro Devices $AMD server chip market share", "investing", 389, 91),
        ("Salesforce $CRM enterprise AI solutions launch", "stocks", 234, 56),
        ("$NVDA datacenter revenue guidance raised 25%", "wallstreetbets", 987, 234),
        ("Meta $META VR headset sales double in Q4", "investing", 456, 87),
        ("Intel $INTC manufacturing expansion announced", "stocks", 345, 67)
    ]
    
    # Generate posts for the past hour
    total_posts = random.randint(45, 85)  # Realistic hourly volume
    
    for i in range(total_posts):
        # Random timestamp within the past hour
        minutes_ago = random.randint(0, 60)
        post_time = now - timedelta(minutes=minutes_ago)
        
        # Select random post template
        title, subreddit, base_score, base_comments = random.choice(post_templates)
        
        # Add some variation to scores and comments
        score_variation = random.uniform(0.7, 1.8)
        comment_variation = random.uniform(0.6, 2.1)
        
        post = {
            'id': f'sample{i+1}_{int(post_time.timestamp())}',
            'title': title,
            'subreddit': subreddit,
            'author': f'TraderUser{random.randint(1, 999)}',
            'score': max(1, int(base_score * score_variation)),
            'num_comments': max(0, int(base_comments * comment_variation)),
            'created_utc': int(post_time.timestamp()),
            'url': f'https://reddit.com/r/{subreddit}/comments/sample{i+1}/post/',
            'selftext': f'Discussion about {title[:30]}...',
            'timestamp': post_time.isoformat()
        }
        
        posts.append(post)
    
    # Sort by timestamp (most recent first)
    posts.sort(key=lambda x: x['created_utc'], reverse=True)
    return posts

def extract_tickers_from_posts(posts):
    """Extract ticker mentions from posts"""
    import re
    ticker_counts = {}
    
    for post in posts:
        # Extract tickers from title
        tickers = re.findall(r'\$([A-Z]{1,5})\b', post['title'])
        for ticker in tickers:
            ticker_symbol = f'${ticker}'
            if ticker_symbol not in ticker_counts:
                ticker_counts[ticker_symbol] = 0
            ticker_counts[ticker_symbol] += 1
    
    # Add some additional realistic tickers
    additional_tickers = {
        '$SPY': random.randint(15, 25),
        '$QQQ': random.randint(8, 15),
        '$IWM': random.randint(3, 8),
        '$VTI': random.randint(2, 6),
        '$ARKK': random.randint(5, 12)
    }
    
    for ticker, count in additional_tickers.items():
        if ticker not in ticker_counts:
            ticker_counts[ticker] = count
        else:
            ticker_counts[ticker] += count
    
    return ticker_counts

def generate_market_analysis(posts, tickers):
    """Generate realistic market analysis"""
    total_posts = len(posts)
    high_activity_posts = [p for p in posts if p['score'] > 500]
    
    # Determine sentiment based on post titles
    bullish_keywords = ['beat', 'exceed', 'up', 'high', 'growth', 'bull', '🚀', 'moon']
    bearish_keywords = ['miss', 'down', 'drop', 'fall', 'bear', 'crash', 'sell']
    
    sentiment_score = 0
    for post in posts:
        title_lower = post['title'].lower()
        bullish_count = sum(1 for word in bullish_keywords if word in title_lower)
        bearish_count = sum(1 for word in bearish_keywords if word in title_lower)
        sentiment_score += (bullish_count - bearish_count) * (post['score'] / 100)
    
    if sentiment_score > 5:
        overall_sentiment = 'Bullish'
    elif sentiment_score < -5:
        overall_sentiment = 'Bearish' 
    else:
        overall_sentiment = 'Neutral'
    
    # Generate insights
    insights = []
    
    if tickers:
        top_ticker = max(tickers.items(), key=lambda x: x[1])
        insights.append(f"🔥 {top_ticker[0]} is trending with {top_ticker[1]} mentions in the past hour")
    
    if len(high_activity_posts) > 3:
        insights.append(f"📊 {len(high_activity_posts)} posts with 500+ upvotes indicate high market interest")
    
    if total_posts > 60:
        insights.append(f"⚡ High activity detected: {total_posts} posts in the past hour")
    
    insights.append(f"💭 Overall sentiment: {overall_sentiment} based on {total_posts} posts")
    
    # Add time-specific insights
    current_hour = datetime.now().hour
    if 9 <= current_hour <= 16:
        insights.append("🕘 US market hours - increased trading activity expected")
    elif 18 <= current_hour <= 23:
        insights.append("🌃 Evening discussion period - earnings and news analysis")
    else:
        insights.append("🌙 After hours - international market focus")
    
    return {
        'overall_sentiment': overall_sentiment,
        'sentiment_score': sentiment_score,
        'insights': insights,
        'high_activity_count': len(high_activity_posts),
        'analysis_timestamp': datetime.now().isoformat()
    }

def generate_hourly_history():
    """Generate 24 hours of historical data"""
    history = []
    now = datetime.now()
    
    for i in range(24):
        hour_time = now - timedelta(hours=i)
        hour_num = hour_time.hour
        
        # Realistic activity patterns
        if 9 <= hour_num <= 16:  # Market hours
            base_posts = random.randint(60, 120)
            base_tickers = random.randint(20, 35)
        elif 18 <= hour_num <= 23:  # Evening
            base_posts = random.randint(40, 80)
            base_tickers = random.randint(15, 25)
        else:  # Night/early morning
            base_posts = random.randint(15, 45)
            base_tickers = random.randint(8, 18)
        
        sentiment_options = ['Bullish', 'Neutral', 'Bearish']
        weights = [0.4, 0.35, 0.25] if 9 <= hour_num <= 16 else [0.3, 0.4, 0.3]
        
        history.append({
            'timestamp': hour_time.isoformat(),
            'total_posts': base_posts,
            'total_tickers': base_tickers,
            'top_ticker': random.choice(['$AAPL', '$TSLA', '$NVDA', '$GME', '$MSFT']),
            'top_subreddit': random.choice(['wallstreetbets', 'stocks', 'investing']),
            'sentiment': random.choices(sentiment_options, weights=weights)[0]
        })
    
    return list(reversed(history))  # Chronological order

def generate_subreddit_stats(posts):
    """Generate subreddit statistics"""
    subreddit_counts = {}
    
    for post in posts:
        subreddit = post['subreddit']
        if subreddit not in subreddit_counts:
            subreddit_counts[subreddit] = 0
        subreddit_counts[subreddit] += 1
    
    return subreddit_counts

def main():
    """Generate all sample data files"""
    print("🎲 Generating realistic sample data...")
    
    # Create data directory
    data_dir = Path("docs/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate posts for past hour
    posts = generate_realistic_posts(hours_back=1)
    print(f"📰 Generated {len(posts)} realistic posts")
    
    # Extract tickers
    tickers = extract_tickers_from_posts(posts)
    print(f"💹 Extracted {len(tickers)} unique tickers")
    
    # Generate analysis
    analysis = generate_market_analysis(posts, tickers)
    print(f"📈 Generated market analysis: {analysis['overall_sentiment']} sentiment")
    
    # Generate history
    history = generate_hourly_history()
    print(f"📊 Generated {len(history)} hours of historical data")
    
    # Generate subreddit stats
    subreddit_stats = generate_subreddit_stats(posts)
    
    # Create metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'total_posts': len(posts),
        'total_tickers': len(tickers),
        'subreddits_monitored': len(subreddit_stats),
        'data_source': 'Generated Sample Data (Realistic)',
        'update_frequency': 'Hourly',
        'time_period': 'Past 1 Hour'
    }
    
    # Save all files
    files_to_save = {
        'posts.json': posts,
        'tickers.json': tickers,
        'analysis.json': analysis,
        'history.json': history,
        'stats.json': {
            'subreddit_stats': subreddit_stats,
            'metadata': metadata
        }
    }
    
    for filename, data in files_to_save.items():
        filepath = data_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {filename}")
    
    # Main combined file
    main_data = {
        'posts': posts,
        'tickers': tickers,
        'subreddit_stats': subreddit_stats,
        'metadata': metadata
    }
    
    with open(data_dir / 'reddit_data.json', 'w') as f:
        json.dump(main_data, f, indent=2)
    print(f"💾 Saved reddit_data.json")
    
    print("✅ Sample data generation complete!")
    print(f"📊 Files saved to: {data_dir}")
    print(f"🕐 Data represents activity from: {datetime.now() - timedelta(hours=1)} to {datetime.now()}")

if __name__ == "__main__":
    main()