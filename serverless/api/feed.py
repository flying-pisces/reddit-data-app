"""
Serverless API for Reddit Insight Mobile App
Database-less content distribution with real-time personalization
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import json
import redis
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from pydantic import BaseModel

# Import our existing Reddit engine
import sys
sys.path.append('../..')
from reddit_client import AsyncRedditClient
from backend.intelligence.summarizer import ContentSummarizer, batch_summarize
from config import MonitoringConfig

app = FastAPI(title="Reddit Insight Mobile API")

# CORS for mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching (serverless-friendly)
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

# Models
class SwipeEvent(BaseModel):
    user_id: str
    content_id: str
    direction: str
    timestamp: int

class FeedRequest(BaseModel):
    recent_interactions: List[Dict] = []
    timestamp: int

class PersonalizationProfile(BaseModel):
    liked_categories: Dict[str, float] = {}
    disliked_categories: Dict[str, float] = {}
    preferred_sentiment: str = 'neutral'
    engagement_patterns: Dict[str, float] = {}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/feed")
async def get_personalized_feed(
    user_id: str,
    interests: str = "finance,technology",
    subscription_tier: str = "FREE",
    offset: int = 0,
    limit: int = 20,
    feed_request: FeedRequest = FeedRequest()
):
    """
    Get personalized content feed for mobile app
    Database-less: Uses Redis for caching and real-time personalization
    """
    try:
        # Parse interests
        interest_list = interests.split(',')
        
        # Get user's personalization profile from interactions
        profile = await build_user_profile(user_id, feed_request.recent_interactions)
        
        # Check if we have cached personalized content
        cache_key = f"feed:{user_id}:{hash(interests)}:{offset}"
        cached_feed = redis_client.get(cache_key)
        
        if cached_feed and offset == 0:  # Use cache for initial load only
            return json.loads(cached_feed)
        
        # Generate fresh content
        fresh_content = await generate_personalized_content(
            interest_list, 
            profile, 
            subscription_tier, 
            limit
        )
        
        # Apply subscription limits
        if subscription_tier == "FREE":
            fresh_content = fresh_content[:20]  # Limit free users
        elif subscription_tier == "PRO":
            fresh_content = fresh_content[:50]
        # PREMIUM gets unlimited
        
        # Cache the result
        cache_data = {
            "feed": fresh_content,
            "generated_at": datetime.now().isoformat(),
            "user_profile": profile.dict()
        }
        
        # Cache for 30 minutes
        redis_client.setex(cache_key, 1800, json.dumps(cache_data))
        
        return cache_data
        
    except Exception as e:
        print(f"Feed generation error: {e}")
        # Fallback to cached content or mock data
        fallback_content = await get_fallback_content(interest_list, limit)
        return {"feed": fallback_content, "generated_at": datetime.now().isoformat()}

@app.post("/api/swipe")
async def record_swipe(swipe: SwipeEvent):
    """
    Record user swipe for real-time personalization
    Database-less: Updates Redis-based user profile immediately
    """
    try:
        # Store swipe event in Redis (temporary)
        swipe_key = f"swipes:{swipe.user_id}"
        swipe_data = swipe.dict()
        
        # Add to user's swipe history (keep last 1000)
        redis_client.lpush(swipe_key, json.dumps(swipe_data))
        redis_client.ltrim(swipe_key, 0, 999)  # Keep last 1000
        redis_client.expire(swipe_key, 2592000)  # 30 days
        
        # Update user personalization profile immediately
        await update_personalization_profile(swipe.user_id, swipe.direction, swipe.content_id)
        
        # Invalidate user's feed cache to force refresh
        pattern = f"feed:{swipe.user_id}:*"
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
        
        return {"status": "recorded", "profile_updated": True}
        
    except Exception as e:
        print(f"Swipe recording error: {e}")
        return {"status": "error", "message": str(e)}

async def build_user_profile(user_id: str, recent_interactions: List[Dict]) -> PersonalizationProfile:
    """
    Build user personalization profile from interactions
    Database-less: Uses Redis and real-time analysis
    """
    try:
        # Get stored profile
        profile_key = f"profile:{user_id}"
        stored_profile = redis_client.get(profile_key)
        
        if stored_profile:
            profile_data = json.loads(stored_profile)
            profile = PersonalizationProfile(**profile_data)
        else:
            profile = PersonalizationProfile()
        
        # Update profile with recent interactions
        for interaction in recent_interactions[-50:]:  # Last 50 interactions
            direction = interaction.get('direction', '')
            category = interaction.get('category', 'general')
            
            if direction == 'right':  # Liked
                profile.liked_categories[category] = profile.liked_categories.get(category, 0) + 1
            elif direction == 'left':  # Disliked
                profile.disliked_categories[category] = profile.disliked_categories.get(category, 0) + 1
        
        # Normalize scores
        total_liked = sum(profile.liked_categories.values())
        total_disliked = sum(profile.disliked_categories.values())
        
        if total_liked > 0:
            profile.liked_categories = {k: v/total_liked for k, v in profile.liked_categories.items()}
        if total_disliked > 0:
            profile.disliked_categories = {k: v/total_disliked for k, v in profile.disliked_categories.items()}
        
        # Save updated profile
        redis_client.setex(profile_key, 86400, json.dumps(profile.dict()))  # 24 hours
        
        return profile
        
    except Exception as e:
        print(f"Profile building error: {e}")
        return PersonalizationProfile()

async def generate_personalized_content(
    interests: List[str], 
    profile: PersonalizationProfile,
    subscription_tier: str,
    limit: int
) -> List[Dict]:
    """
    Generate personalized content using existing Reddit engine + AI
    """
    try:
        # Map interests to subreddits
        subreddit_mapping = {
            'finance': ['stocks', 'investing', 'wallstreetbets', 'personalfinance'],
            'technology': ['technology', 'programming', 'MachineLearning', 'startups'],
            'lifestyle': ['productivity', 'fitness', 'getmotivated', 'lifeprotips'],
            'gaming': ['gaming', 'pcgaming', 'nintendo', 'playstation'],
            'business': ['entrepreneur', 'smallbusiness', 'marketing']
        }
        
        # Get relevant subreddits
        relevant_subreddits = []
        for interest in interests:
            relevant_subreddits.extend(subreddit_mapping.get(interest.lower(), []))
        
        if not relevant_subreddits:
            relevant_subreddits = ['stocks', 'technology']  # Default
        
        # Collect Reddit posts
        all_posts = []
        async with AsyncRedditClient() as client:
            tasks = []
            for subreddit in relevant_subreddits[:5]:  # Limit to prevent rate limits
                tasks.append(client.get_hot_posts(subreddit, limit=10))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_posts.extend(result)
        
        # AI processing
        if all_posts:
            summarizer = ContentSummarizer()
            processed_content = await batch_summarize(
                [post.to_dict() for post in all_posts], 
                summarizer
            )
            
            # Convert to API format
            formatted_content = []
            for i, (post, summary) in enumerate(zip(all_posts, processed_content)):
                if hasattr(summary, 'summary_sentence'):  # Successful processing
                    content_item = {
                        "id": f"reddit_{post.id}_{int(datetime.now().timestamp())}",
                        "summary": summary.summary_sentence,
                        "category": post.category.title(),
                        "sentiment": summary.sentiment,
                        "relevance_score": calculate_relevance_score(summary, profile),
                        "engagement_score": summary.confidence * 100,
                        "chart_data": summary.chart_data,
                        "key_points": summary.key_points,
                        "tickers": summary.tickers_mentioned,
                        "original_url": f"https://reddit.com{post.url}" if hasattr(post, 'url') else f"https://reddit.com/r/{post.subreddit}",
                        "subreddit": post.subreddit,
                        "timestamp": post.created_utc
                    }
                    formatted_content.append(content_item)
            
            # Sort by relevance and engagement
            formatted_content.sort(
                key=lambda x: x['relevance_score'] * x['engagement_score'], 
                reverse=True
            )
            
            return formatted_content[:limit]
        
        # Fallback to mock data
        return await get_fallback_content(interests, limit)
        
    except Exception as e:
        print(f"Content generation error: {e}")
        return await get_fallback_content(interests, limit)

def calculate_relevance_score(summary, profile: PersonalizationProfile) -> float:
    """Calculate how relevant content is to user based on their profile"""
    base_score = 50.0  # Base relevance
    
    # Boost for liked categories
    category = summary.category.lower()
    if category in profile.liked_categories:
        base_score += profile.liked_categories[category] * 30
    
    # Penalize disliked categories  
    if category in profile.disliked_categories:
        base_score -= profile.disliked_categories[category] * 20
    
    # Sentiment preference
    if hasattr(summary, 'sentiment'):
        if summary.sentiment.lower() == profile.preferred_sentiment.lower():
            base_score += 10
    
    return min(max(base_score, 0), 100)  # Clamp between 0-100

async def update_personalization_profile(user_id: str, direction: str, content_id: str):
    """Update user's personalization profile based on swipe"""
    try:
        profile_key = f"profile:{user_id}"
        stored_profile = redis_client.get(profile_key)
        
        if stored_profile:
            profile_data = json.loads(stored_profile)
            
            # Simple learning algorithm
            if direction == 'right':
                profile_data['positive_signals'] = profile_data.get('positive_signals', 0) + 1
            elif direction == 'left':
                profile_data['negative_signals'] = profile_data.get('negative_signals', 0) + 1
            
            # Update preferred engagement time
            current_hour = datetime.now().hour
            profile_data['active_hours'] = profile_data.get('active_hours', {})
            profile_data['active_hours'][str(current_hour)] = profile_data['active_hours'].get(str(current_hour), 0) + 1
            
            # Save updated profile
            redis_client.setex(profile_key, 86400, json.dumps(profile_data))
            
    except Exception as e:
        print(f"Profile update error: {e}")

async def get_fallback_content(interests: List[str], limit: int) -> List[Dict]:
    """Fallback mock content when Reddit API fails"""
    mock_content = [
        {
            "id": f"mock_{i}_{int(datetime.now().timestamp())}",
            "summary": f"Sample content for {interest} - AI-powered insights from Reddit communities.",
            "category": interest.title(),
            "sentiment": "POSITIVE",
            "relevance_score": 85,
            "engagement_score": 92,
            "key_points": [f"{interest} discussion", "Community insights", "Trending topic"],
            "tickers": ["AAPL", "TSLA"] if interest == 'finance' else [],
            "original_url": "https://reddit.com/r/example",
            "subreddit": interest,
            "timestamp": datetime.now().timestamp(),
            "chart_data": {
                "title": f"{interest.title()} Activity",
                "labels": ["6h", "4h", "2h", "Now"],
                "data": [20, 35, 50, 70]
            }
        }
        for i, interest in enumerate(interests[:limit])
    ]
    
    return mock_content

# For serverless deployment (Vercel/Netlify/AWS Lambda)
handler = Mangum(app)