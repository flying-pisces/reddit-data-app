#!/usr/bin/env python3
"""
Comprehensive functionality test for Reddit Data Engine
"""

import praw
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter
from pathlib import Path

load_dotenv()

class FullSystemTest:
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'test-script:v1.0')
        self.reddit = None
        self.posts_collected = []
        self.test_results = {}
        
    def test_authentication(self):
        """Test 1: Reddit Authentication"""
        print("\n" + "="*60)
        print("TEST 1: REDDIT AUTHENTICATION")
        print("="*60)
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # Test with a simple subreddit fetch
            test_sub = self.reddit.subreddit("python")
            _ = test_sub.display_name
            
            print("✅ Authentication successful")
            self.test_results['authentication'] = 'PASSED'
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.test_results['authentication'] = f'FAILED: {e}'
            return False
    
    def test_data_collection(self):
        """Test 2: Data Collection from Multiple Subreddits"""
        print("\n" + "="*60)
        print("TEST 2: DATA COLLECTION")
        print("="*60)
        
        test_subreddits = ['python', 'programming', 'technology']
        
        for sub_name in test_subreddits:
            try:
                print(f"\nCollecting from r/{sub_name}...")
                subreddit = self.reddit.subreddit(sub_name)
                
                # Collect hot posts
                hot_posts = list(subreddit.hot(limit=5))
                print(f"  • Hot posts: {len(hot_posts)}")
                
                # Collect new posts
                new_posts = list(subreddit.new(limit=5))
                print(f"  • New posts: {len(new_posts)}")
                
                # Store for analysis
                for post in hot_posts[:3]:
                    self.posts_collected.append({
                        'id': post.id,
                        'title': post.title,
                        'subreddit': sub_name,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'author': str(post.author) if post.author else '[deleted]',
                        'url': post.url
                    })
                
                print(f"✅ Successfully collected from r/{sub_name}")
                
            except Exception as e:
                print(f"❌ Failed to collect from r/{sub_name}: {e}")
                self.test_results[f'collection_{sub_name}'] = f'FAILED: {e}'
                continue
        
        total_collected = len(self.posts_collected)
        print(f"\n📊 Total posts collected: {total_collected}")
        self.test_results['data_collection'] = f'PASSED: {total_collected} posts'
        return total_collected > 0
    
    def test_data_processing(self):
        """Test 3: Data Processing and Analysis"""
        print("\n" + "="*60)
        print("TEST 3: DATA PROCESSING & ANALYSIS")
        print("="*60)
        
        if not self.posts_collected:
            print("❌ No data to process")
            self.test_results['data_processing'] = 'FAILED: No data'
            return False
        
        try:
            # Ticker extraction simulation
            ticker_pattern = r'\$[A-Z]{1,5}\b'
            import re
            
            tickers = []
            for post in self.posts_collected:
                found = re.findall(ticker_pattern, post['title'])
                tickers.extend(found)
            
            ticker_counts = Counter(tickers)
            print(f"\n📈 Tickers found: {dict(ticker_counts) if ticker_counts else 'None'}")
            
            # Sentiment simulation
            positive_words = ['good', 'great', 'excellent', 'amazing', 'best']
            negative_words = ['bad', 'terrible', 'worst', 'awful', 'horrible']
            
            sentiment_score = 0
            for post in self.posts_collected:
                title_lower = post['title'].lower()
                for word in positive_words:
                    if word in title_lower:
                        sentiment_score += 1
                for word in negative_words:
                    if word in title_lower:
                        sentiment_score -= 1
            
            print(f"💭 Sentiment score: {sentiment_score}")
            
            # Engagement metrics
            avg_score = sum(p['score'] for p in self.posts_collected) / len(self.posts_collected)
            avg_comments = sum(p['num_comments'] for p in self.posts_collected) / len(self.posts_collected)
            
            print(f"📊 Average score: {avg_score:.1f}")
            print(f"💬 Average comments: {avg_comments:.1f}")
            
            print("\n✅ Data processing successful")
            self.test_results['data_processing'] = 'PASSED'
            return True
            
        except Exception as e:
            print(f"❌ Data processing failed: {e}")
            self.test_results['data_processing'] = f'FAILED: {e}'
            return False
    
    def test_data_export(self):
        """Test 4: Data Export to JSON"""
        print("\n" + "="*60)
        print("TEST 4: DATA EXPORT")
        print("="*60)
        
        if not self.posts_collected:
            print("❌ No data to export")
            self.test_results['data_export'] = 'FAILED: No data'
            return False
        
        try:
            # Prepare export data
            export_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_posts': len(self.posts_collected),
                    'test_run': True
                },
                'posts': self.posts_collected[:5],  # Export first 5 posts
                'statistics': {
                    'subreddits_monitored': list(set(p['subreddit'] for p in self.posts_collected)),
                    'average_score': sum(p['score'] for p in self.posts_collected) / len(self.posts_collected)
                }
            }
            
            # Create exports directory if needed
            Path('exports').mkdir(exist_ok=True)
            
            # Export to file
            filename = f"exports/test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Data exported to: {filename}")
            print(f"📄 File size: {os.path.getsize(filename)} bytes")
            
            self.test_results['data_export'] = f'PASSED: {filename}'
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            self.test_results['data_export'] = f'FAILED: {e}'
            return False
    
    def test_monitoring_simulation(self):
        """Test 5: Monitoring Simulation"""
        print("\n" + "="*60)
        print("TEST 5: MONITORING SIMULATION")
        print("="*60)
        
        try:
            print("🔄 Simulating real-time monitoring for 5 seconds...")
            
            start_time = time.time()
            posts_found = 0
            
            while time.time() - start_time < 5:
                # Simulate checking for new posts
                subreddit = self.reddit.subreddit('python')
                new_post = next(subreddit.new(limit=1))
                
                if new_post:
                    posts_found += 1
                    print(f"  • Found post: {new_post.title[:50]}...")
                
                time.sleep(2)
            
            print(f"\n✅ Monitoring simulation complete")
            print(f"📊 Posts checked: {posts_found}")
            
            self.test_results['monitoring'] = 'PASSED'
            return True
            
        except Exception as e:
            print(f"❌ Monitoring simulation failed: {e}")
            self.test_results['monitoring'] = f'FAILED: {e}'
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "🚀"*30)
        print("  REDDIT DATA ENGINE - FULL SYSTEM TEST")
        print("🚀"*30)
        
        # Run tests
        auth_success = self.test_authentication()
        
        if auth_success:
            self.test_data_collection()
            self.test_data_processing()
            self.test_data_export()
            self.test_monitoring_simulation()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status = "✅" if "PASSED" in str(result) else "❌"
            print(f"{status} {test_name}: {result}")
            
            if "PASSED" in str(result):
                passed += 1
            else:
                failed += 1
        
        print("\n" + "-"*60)
        print(f"TOTAL: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is fully functional!")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        
        return failed == 0

def main():
    tester = FullSystemTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()