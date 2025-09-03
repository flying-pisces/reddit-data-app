# Reddit Insight App - Architecture Design

## Overview
Transform the existing Reddit data engine into a modern, user-centric news discovery app with TikTok-style interface and AI-powered content curation.

## Core Philosophy
- **Speed**: One sentence + one visual per story
- **Personalization**: Learn from user swipes and preferences  
- **Intelligence**: Multi-dimensional content scoring and ranking
- **Simplicity**: Complex data → Simple insights

## Technical Stack

### Frontend Options
**Option A: Cross-Platform Mobile (Recommended)**
- React Native + Expo
- Native iOS/Android apps
- Web version via React Native Web

**Option B: Desktop-First**
- Electron + React
- macOS/Windows/Linux support
- Mobile-responsive web view

### Backend Architecture (Enhanced Existing)
```python
# Enhanced Reddit Engine
reddit_engine/
├── collectors/          # Enhanced reddit_client.py
│   ├── reddit_collector.py
│   ├── content_processor.py  
│   └── real_time_monitor.py
├── intelligence/        # New AI layer
│   ├── summarizer.py
│   ├── sentiment_analyzer.py
│   └── content_scorer.py
├── personalization/     # New recommendation engine
│   ├── user_profiler.py
│   ├── interest_mapper.py
│   └── recommendation_engine.py
└── api/                # Enhanced API layer
    ├── auth_service.py
    ├── content_api.py
    └── user_api.py
```

## Data Models

### User Profile
```python
@dataclass
class UserProfile:
    user_id: str
    auth_provider: str  # google/apple/email
    interests: List[str]  # finance, tech, life, etc.
    subreddit_preferences: Dict[str, float]  # subreddit -> weight
    engagement_history: List[UserEngagement]
    content_preferences: ContentPreferences
```

### Processed Content
```python
@dataclass  
class ProcessedContent:
    content_id: str
    original_post_id: str
    subreddit: str
    category: str
    
    # AI-generated content
    summary_sentence: str
    visual_data: Dict  # chart/graph data
    key_insights: List[str]
    
    # Intelligence scores
    relevance_score: float
    sentiment_score: float
    engagement_score: float
    complexity_score: float
    
    # Source linking
    original_url: str
    related_posts: List[str]
```

### User Engagement
```python
@dataclass
class UserEngagement:
    content_id: str
    action: str  # swipe_right/left/up/down, save, share
    timestamp: datetime
    dwell_time: float
    interaction_depth: int  # 0=summary, 1=details, 2=full_post
```

## Core Features Implementation

### 1. Interest-Based Onboarding
```python
INTEREST_SUBREDDIT_MAPPING = {
    'finance': {
        'beginner': ['personalfinance', 'investing', 'stocks'],
        'advanced': ['SecurityAnalysis', 'ValueInvesting', 'options'],
        'speculative': ['wallstreetbets', 'pennystocks']
    },
    'technology': {
        'consumer': ['technology', 'gadgets', 'apple'],
        'developer': ['programming', 'webdev', 'MachineLearning'],
        'business': ['startups', 'entrepreneur', 'techindustry']
    },
    'life': {
        'productivity': ['productivity', 'getmotivated', 'lifehacks'],
        'health': ['fitness', 'nutrition', 'mentalhealth'],
        'relationships': ['relationships', 'dating_advice', 'socialskills']
    }
}
```

### 2. AI Summarization Pipeline
```python
class ContentProcessor:
    def __init__(self):
        self.summarizer = AITextSummarizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.visual_generator = DataVisualizationEngine()
    
    async def process_reddit_post(self, post: RedditPost) -> ProcessedContent:
        # Extract key information
        summary = await self.summarizer.one_sentence_summary(
            post.title + " " + post.selftext
        )
        
        # Generate visualization data
        visual_data = await self.visual_generator.create_insight_chart(post)
        
        # Calculate intelligence scores
        scores = await self.calculate_content_scores(post)
        
        return ProcessedContent(
            summary_sentence=summary,
            visual_data=visual_data,
            **scores
        )
```

### 3. Multi-Dimensional Scoring System
```python
class ContentScorer:
    def calculate_relevance_score(self, content: ProcessedContent, 
                                user: UserProfile) -> float:
        """Match content to user interests using weighted categories"""
        base_score = self._category_match_score(content, user)
        engagement_boost = self._engagement_history_boost(content, user)
        recency_factor = self._recency_weighting(content)
        
        return (base_score * 0.5) + (engagement_boost * 0.3) + (recency_factor * 0.2)
    
    def calculate_engagement_potential(self, post: RedditPost) -> float:
        """Predict how engaging content will be"""
        comment_velocity = post.num_comments / max(post.age_hours, 1)
        upvote_ratio_boost = post.upvote_ratio * 2 - 1
        subreddit_activity = self._get_subreddit_activity_score(post.subreddit)
        
        return min((comment_velocity * upvote_ratio_boost * subreddit_activity), 1.0)
```

### 4. Swipe-Based Learning Algorithm
```python
class PersonalizationEngine:
    def process_swipe_feedback(self, user_id: str, content_id: str, 
                             swipe_direction: str):
        """Learn from user swipe patterns"""
        if swipe_direction == "right":
            self._boost_similar_content(user_id, content_id, weight=1.2)
        elif swipe_direction == "left": 
            self._reduce_similar_content(user_id, content_id, weight=0.8)
        elif swipe_direction == "up":
            self._increase_complexity_preference(user_id, content_id)
        elif swipe_direction == "down":
            self._temporarily_filter_category(user_id, content_id)
```

## UI/UX Specifications

### Onboarding Flow
1. **Welcome Screen**: App introduction and value proposition
2. **Auth Screen**: Google/Apple/Email signup options
3. **Interest Selection**: Visual category picker with examples
4. **Subreddit Refinement**: Advanced users can customize specific communities
5. **Notification Preferences**: Push notification settings
6. **Tutorial**: Quick swipe gesture introduction

### Main Interface (Card-Based Feed)
```
┌─────────────────────────────┐
│ ◀ Finance                  ⚙│ <- Category indicator
├─────────────────────────────│
│                             │
│    📈 One Sentence Summary  │ <- AI-generated insight
│                             │
│  [Interactive Chart/Graph]  │ <- Data visualization
│                             │
│    Key Points:              │ <- Bullet highlights
│    • Point 1                │
│    • Point 2                │ 
│                             │
├─────────────────────────────│
│ r/investing • 2h ago • 🔗   │ <- Source + link
└─────────────────────────────┘
```

### Swipe Interactions
- **Right Swipe**: Green animation, "More like this"
- **Left Swipe**: Red animation, "Less like this" 
- **Up Swipe**: Blue animation, expand to full details
- **Down Swipe**: Gray animation, "Skip category"

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Set up React Native project structure
- Implement basic authentication (Firebase Auth)
- Create interest selection onboarding
- Enhanced backend API with user management

### Phase 2: Core Features (Weeks 3-4) 
- Build swipe-based card interface
- Implement basic AI summarization
- Create content scoring system
- Real-time Reddit data pipeline

### Phase 3: Intelligence (Weeks 5-6)
- Advanced personalization engine
- Multi-dimensional content ranking
- Visual data generation
- User feedback learning system

### Phase 4: Polish & Distribution (Weeks 7-8)
- Performance optimization
- App store preparation
- Beta testing and feedback
- Deployment and distribution

## Success Metrics
- **User Engagement**: Daily active users, session time
- **Content Relevance**: Swipe-right percentage, saved articles
- **Personalization Accuracy**: Improvement in relevance scores over time
- **User Satisfaction**: App store ratings, user retention

This architecture transforms your Reddit data engine into a modern, intelligent news discovery platform that learns from users and delivers personalized insights in a fast, digestible format.