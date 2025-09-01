#!/usr/bin/env python3
"""
Reddit Data Engine - Web Dashboard
Flask-based web interface for monitoring Reddit data
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from reddit_client import RedditClient
from data_processor import DataProcessor
from api_interface import AnalysisAPI

app = Flask(__name__)
# Allow CORS for GitHub Pages domain
CORS(app, origins=["https://flying-pisces.github.io", "http://localhost:3000", "http://localhost:8000"])

# Global data storage
monitor_data = {
    'posts': [],
    'tickers': {},
    'stats': {
        'total_posts': 0,
        'active_subreddits': 0,
        'trending_tickers': 0,
        'sentiment': 'Neutral',
        'posts_per_minute': 0
    },
    'monitoring': False,
    'last_update': None
}

# Background monitoring thread
monitor_thread = None
reddit_client = None

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current monitoring status"""
    return jsonify({
        'monitoring': monitor_data['monitoring'],
        'last_update': monitor_data['last_update'],
        'stats': monitor_data['stats']
    })

@app.route('/api/posts')
def get_posts():
    """Get recent posts"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'posts': monitor_data['posts'][:limit],
        'total': len(monitor_data['posts'])
    })

@app.route('/api/tickers')
def get_tickers():
    """Get trending tickers"""
    # Sort tickers by mention count
    sorted_tickers = sorted(
        monitor_data['tickers'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    return jsonify({
        'tickers': [
            {
                'symbol': ticker,
                'count': data['count'],
                'sentiment': data.get('sentiment', 0),
                'subreddits': data.get('subreddits', [])
            }
            for ticker, data in sorted_tickers[:20]
        ]
    })

@app.route('/api/insights')
def get_insights():
    """Get market insights"""
    insights = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_posts': monitor_data['stats']['total_posts'],
            'unique_tickers': len(monitor_data['tickers']),
            'top_ticker': None,
            'market_sentiment': monitor_data['stats']['sentiment']
        },
        'recommendations': []
    }
    
    # Get top ticker
    if monitor_data['tickers']:
        top_ticker = max(monitor_data['tickers'].items(), key=lambda x: x[1]['count'])
        insights['summary']['top_ticker'] = {
            'symbol': top_ticker[0],
            'mentions': top_ticker[1]['count']
        }
    
    # Generate recommendations
    if monitor_data['stats']['total_posts'] > 100:
        insights['recommendations'].append("High activity detected - monitor for volatility")
    
    if len(monitor_data['tickers']) > 10:
        insights['recommendations'].append("Multiple tickers trending - diversification opportunity")
    
    return jsonify(insights)

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start Reddit monitoring"""
    global monitor_thread, reddit_client
    
    if not monitor_data['monitoring']:
        monitor_data['monitoring'] = True
        reddit_client = RedditClient()
        
        # Start background monitoring
        monitor_thread = threading.Thread(target=monitor_reddit_background, daemon=True)
        monitor_thread.start()
        
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    
    return jsonify({'status': 'error', 'message': 'Already monitoring'})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop Reddit monitoring"""
    monitor_data['monitoring'] = False
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/export', methods=['POST'])
def export_data():
    """Export current data to JSON"""
    try:
        data = request.json
        subreddits = data.get('subreddits', [])
        hours = data.get('hours', 24)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"exports/web_export_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'Web Dashboard',
                'subreddits': subreddits,
                'hours_back': hours
            },
            'posts': monitor_data['posts'],
            'tickers': monitor_data['tickers'],
            'statistics': monitor_data['stats']
        }
        
        # Save file
        Path('exports').mkdir(exist_ok=True)
        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'posts_exported': len(monitor_data['posts']),
            'tickers_exported': len(monitor_data['tickers'])
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update settings"""
    if request.method == 'GET':
        # Return current settings
        return jsonify({
            'refresh_interval': 30,
            'max_posts': 25,
            'subreddits': [
                'wallstreetbets', 'stocks', 'investing',
                'options', 'pennystocks', 'StockMarket'
            ]
        })
    
    elif request.method == 'POST':
        # Update settings
        settings = request.json
        # Save settings (implement as needed)
        return jsonify({'status': 'success', 'message': 'Settings updated'})

def monitor_reddit_background():
    """Background function to monitor Reddit"""
    global monitor_data
    
    subreddits = [
        'wallstreetbets', 'stocks', 'investing',
        'options', 'pennystocks', 'StockMarket'
    ]
    
    while monitor_data['monitoring']:
        try:
            for subreddit in subreddits:
                if not monitor_data['monitoring']:
                    break
                
                # Fetch posts
                posts = reddit_client.get_hot_posts(subreddit, limit=10)
                
                for post in posts:
                    # Add to posts list
                    post_data = {
                        'id': post.id,
                        'time': datetime.now().isoformat(),
                        'subreddit': post.subreddit,
                        'title': post.title,
                        'score': post.score,
                        'comments': post.num_comments,
                        'author': post.author,
                        'url': post.url
                    }
                    
                    # Add to beginning of list
                    monitor_data['posts'].insert(0, post_data)
                    
                    # Limit stored posts
                    if len(monitor_data['posts']) > 500:
                        monitor_data['posts'] = monitor_data['posts'][:500]
                    
                    # Extract tickers
                    import re
                    tickers = re.findall(r'\$[A-Z]{1,5}\b', post.title)
                    for ticker in tickers:
                        if ticker not in monitor_data['tickers']:
                            monitor_data['tickers'][ticker] = {
                                'count': 0,
                                'sentiment': 0,
                                'subreddits': set()
                            }
                        monitor_data['tickers'][ticker]['count'] += 1
                        monitor_data['tickers'][ticker]['subreddits'].add(post.subreddit)
                
                # Update stats
                monitor_data['stats']['total_posts'] = len(monitor_data['posts'])
                monitor_data['stats']['trending_tickers'] = len(monitor_data['tickers'])
                
                # Count unique subreddits
                unique_subs = set(p['subreddit'] for p in monitor_data['posts'])
                monitor_data['stats']['active_subreddits'] = len(unique_subs)
                
                monitor_data['last_update'] = datetime.now().isoformat()
            
            # Wait before next iteration
            time.sleep(30)
            
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # For production (Render), use PORT from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)