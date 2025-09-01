"""
Real-time Reddit Post Monitoring System
"""
import asyncio
import logging
import time
from typing import List, Dict, Set
from collections import defaultdict, deque
from datetime import datetime, timezone
import signal
import sys

from reddit_client import AsyncRedditClient, RedditPost
from data_processor import DataProcessor
from config import MonitoringConfig, DataConfig

class RedditMonitor:
    """Real-time monitoring system for Reddit posts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processor = DataProcessor()
        self.seen_post_ids: Set[str] = set()
        self.post_buffer: deque = deque(maxlen=10000)  # Ring buffer for recent posts
        self.subreddit_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_posts': 0,
            'hot_posts': 0,
            'speculative_posts': 0,
            'last_activity': 0
        })
        self.running = False
        self.tasks: List[asyncio.Task] = []
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        self.logger.info("Starting Reddit monitoring system...")
        self.running = True
        
        async with AsyncRedditClient() as reddit_client:
            try:
                # Create monitoring tasks
                self.tasks = [
                    asyncio.create_task(self._monitor_hot_posts(reddit_client)),
                    asyncio.create_task(self._monitor_new_posts(reddit_client)),
                    asyncio.create_task(self._monitor_rising_posts(reddit_client)),
                    asyncio.create_task(self._periodic_export()),
                    asyncio.create_task(self._stats_reporter())
                ]
                
                # Wait for all tasks to complete
                await asyncio.gather(*self.tasks, return_exceptions=True)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring system: {e}")
            finally:
                await self._cleanup()
    
    async def _monitor_hot_posts(self, reddit_client: AsyncRedditClient):
        """Monitor hot posts across all subreddits"""
        self.logger.info("Starting hot posts monitoring...")
        
        while self.running:
            try:
                tasks = []
                for subreddit in MonitoringConfig.ALL_SUBREDDITS:
                    task = reddit_client.get_hot_posts(subreddit, limit=25)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, list):
                        subreddit = MonitoringConfig.ALL_SUBREDDITS[i]
                        await self._process_posts(result, 'hot', subreddit)
                    else:
                        self.logger.error(f"Error fetching hot posts: {result}")
                
                await asyncio.sleep(MonitoringConfig.HOT_POSTS_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in hot posts monitoring: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _monitor_new_posts(self, reddit_client: AsyncRedditClient):
        """Monitor new posts across all subreddits"""
        self.logger.info("Starting new posts monitoring...")
        
        while self.running:
            try:
                tasks = []
                for subreddit in MonitoringConfig.ALL_SUBREDDITS:
                    task = reddit_client.get_new_posts(subreddit, limit=50)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, list):
                        subreddit = MonitoringConfig.ALL_SUBREDDITS[i]
                        await self._process_posts(result, 'new', subreddit)
                    else:
                        self.logger.error(f"Error fetching new posts: {result}")
                
                await asyncio.sleep(MonitoringConfig.NEW_POSTS_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in new posts monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_rising_posts(self, reddit_client: AsyncRedditClient):
        """Monitor rising posts across all subreddits"""
        self.logger.info("Starting rising posts monitoring...")
        
        while self.running:
            try:
                tasks = []
                for subreddit in MonitoringConfig.ALL_SUBREDDITS:
                    task = reddit_client.get_rising_posts(subreddit, limit=25)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, list):
                        subreddit = MonitoringConfig.ALL_SUBREDDITS[i]
                        await self._process_posts(result, 'rising', subreddit)
                    else:
                        self.logger.error(f"Error fetching rising posts: {result}")
                
                await asyncio.sleep(MonitoringConfig.RISING_POSTS_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in rising posts monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _process_posts(self, posts: List[RedditPost], post_type: str, subreddit: str):
        """Process and filter posts"""
        new_posts = []
        
        for post in posts:
            # Skip if we've already seen this post
            if post.id in self.seen_post_ids:
                continue
            
            # Apply filtering criteria
            if not post.is_recent(MonitoringConfig.MAX_AGE_HOURS):
                continue
            
            if not post.meets_criteria(
                MonitoringConfig.MIN_SCORE,
                MonitoringConfig.MIN_COMMENTS
            ):
                continue
            
            # Add to seen set and buffer
            self.seen_post_ids.add(post.id)
            self.post_buffer.append(post)
            new_posts.append(post)
            
            # Update stats
            self.subreddit_stats[subreddit]['total_posts'] += 1
            self.subreddit_stats[subreddit]['last_activity'] = time.time()
            
            if post_type == 'hot':
                self.subreddit_stats[subreddit]['hot_posts'] += 1
            
            # Check for speculative content
            if self.data_processor.is_speculative_post(post):
                self.subreddit_stats[subreddit]['speculative_posts'] += 1
                self.logger.info(f"Speculative post detected in r/{subreddit}: {post.title[:50]}...")
        
        # Process batch of new posts
        if new_posts:
            await self._handle_new_posts(new_posts, post_type)
    
    async def _handle_new_posts(self, posts: List[RedditPost], post_type: str):
        """Handle newly detected posts"""
        # Analyze posts for priority signals
        priority_posts = self.data_processor.filter_priority_posts(posts)
        
        if priority_posts:
            self.logger.info(f"Found {len(priority_posts)} priority {post_type} posts")
            
            # Log high-priority posts immediately
            for post in priority_posts:
                self.logger.warning(
                    f"HIGH PRIORITY: r/{post.subreddit} - {post.title[:80]}... "
                    f"(Score: {post.score}, Comments: {post.num_comments})"
                )
        
        # Add to data processor for aggregation
        self.data_processor.add_posts(posts)
    
    async def _periodic_export(self):
        """Periodically export data for upper-level analysis"""
        self.logger.info("Starting periodic data export...")
        
        while self.running:
            try:
                # Export current data
                export_data = self.data_processor.export_for_analysis()
                
                if export_data:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"reddit_data_{timestamp}.json"
                    
                    await self.data_processor.save_export_data(export_data, filename)
                    self.logger.info(f"Data exported to {filename}")
                
                await asyncio.sleep(DataConfig.EXPORT_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic export: {e}")
                await asyncio.sleep(60)
    
    async def _stats_reporter(self):
        """Report monitoring statistics"""
        self.logger.info("Starting stats reporter...")
        
        while self.running:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                total_posts = sum(stats['total_posts'] for stats in self.subreddit_stats.values())
                total_speculative = sum(stats['speculative_posts'] for stats in self.subreddit_stats.values())
                
                self.logger.info(
                    f"Stats: {total_posts} total posts, {total_speculative} speculative, "
                    f"{len(self.seen_post_ids)} unique posts seen, "
                    f"{len(self.post_buffer)} in buffer"
                )
                
                # Report top active subreddits
                active_subreddits = sorted(
                    self.subreddit_stats.items(),
                    key=lambda x: x[1]['total_posts'],
                    reverse=True
                )[:5]
                
                self.logger.info("Top active subreddits:")
                for subreddit, stats in active_subreddits:
                    self.logger.info(f"  r/{subreddit}: {stats['total_posts']} posts")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in stats reporter: {e}")
    
    async def _cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up monitoring system...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Final data export
        try:
            export_data = self.data_processor.export_for_analysis()
            if export_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reddit_data_final_{timestamp}.json"
                await self.data_processor.save_export_data(export_data, filename)
                self.logger.info(f"Final data exported to {filename}")
        except Exception as e:
            self.logger.error(f"Error in final export: {e}")

async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('reddit_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Reddit Data Engine...")
    
    monitor = RedditMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Reddit Data Engine stopped")