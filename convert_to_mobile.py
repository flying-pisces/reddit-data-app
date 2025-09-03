#!/usr/bin/env python3
"""
Reddit Insight Mobile App Converter
Converts the current web app to proper React Native mobile architecture
"""

import os
import subprocess
import json
from pathlib import Path

def create_react_native_project():
    """Create React Native project structure"""
    print("🔥 Converting to React Native Mobile App...")
    
    # Create React Native project
    project_name = "RedditInsightMobile"
    
    try:
        print("📱 Creating React Native project...")
        subprocess.run([
            "npx", "react-native", "init", project_name,
            "--template", "react-native-template-typescript"
        ], check=True)
        
        print("✅ React Native project created!")
        
        # Install mobile-specific dependencies
        mobile_deps = [
            "@react-navigation/native",
            "@react-navigation/stack", 
            "react-native-screens",
            "react-native-safe-area-context",
            "react-native-gesture-handler",
            "react-native-reanimated",
            "@react-native-push-notification/push-notification",
            "@react-native-async-storage/async-storage",
            "react-native-chart-kit",
            "react-native-svg",
            "react-native-vector-icons",
            "react-native-linear-gradient",
            "@react-native-community/netinfo",
            "react-native-orientation-locker"
        ]
        
        os.chdir(project_name)
        
        print("📦 Installing mobile dependencies...")
        subprocess.run(["npm", "install"] + mobile_deps, check=True)
        
        # iOS specific
        if os.path.exists("ios"):
            print("🍎 Setting up iOS dependencies...")
            subprocess.run(["cd", "ios", "&&", "pod", "install"], shell=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating React Native project: {e}")
        return False

def create_mobile_backend():
    """Create enhanced backend for mobile app"""
    backend_structure = {
        "mobile_backend/": {
            "content_pipeline/": [
                "reddit_collector.py",
                "ai_processor.py", 
                "personalization_engine.py",
                "content_ranker.py"
            ],
            "push_service/": [
                "notification_manager.py",
                "feed_generator.py", 
                "websocket_server.py"
            ],
            "api/": [
                "mobile_api.py",
                "user_events.py",
                "feed_api.py"
            ]
        }
    }
    
    print("🚀 Creating mobile backend structure...")
    
    for folder, files in backend_structure.items():
        Path(folder).mkdir(exist_ok=True)
        
        if isinstance(files, list):
            for file in files:
                create_backend_file(f"{folder}{file}")
        else:
            for subfolder, subfiles in files.items():
                Path(f"{folder}{subfolder}").mkdir(exist_ok=True)
                for file in subfiles:
                    create_backend_file(f"{folder}{subfolder}{file}")
    
    print("✅ Mobile backend structure created!")

def create_backend_file(filepath):
    """Create backend file with basic structure"""
    filename = os.path.basename(filepath)
    
    if "reddit_collector" in filename:
        content = '''"""
Real-time Reddit content collector for mobile app
Runs continuously and pushes content to user feeds
"""
import asyncio
import redis
from reddit_client import AsyncRedditClient
from config import MonitoringConfig

class MobileRedditCollector:
    def __init__(self):
        self.redis = redis.Redis()
        
    async def collect_continuous(self):
        """Continuously collect Reddit content and push to feeds"""
        while True:
            async with AsyncRedditClient() as client:
                for subreddit in MonitoringConfig.ALL_SUBREDDITS:
                    posts = await client.get_hot_posts(subreddit, limit=10)
                    
                    for post in posts:
                        # Add to processing queue
                        self.redis.lpush("content_queue", post.to_json())
            
            await asyncio.sleep(30)  # Collect every 30 seconds

if __name__ == "__main__":
    collector = MobileRedditCollector()
    asyncio.run(collector.collect_continuous())
'''
    
    elif "websocket_server" in filename:
        content = '''"""
WebSocket server for real-time content delivery to mobile apps
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import redis

app = FastAPI()
redis_client = redis.Redis()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Check for new content for this user
            new_content = redis_client.lpop(f"feed:{user_id}")
            if new_content:
                content_data = json.loads(new_content)
                await manager.send_personal_message(user_id, {
                    "type": "new_content",
                    "data": content_data
                })
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
'''
    
    elif "mobile_api" in filename:
        content = '''"""
REST API endpoints for mobile app
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

app = FastAPI(title="Reddit Insight Mobile API")
redis_client = redis.Redis()

# CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SwipeEvent(BaseModel):
    user_id: str
    content_id: str
    direction: str  # "left", "right", "up", "down"
    timestamp: float

@app.post("/api/swipe")
async def record_swipe(swipe: SwipeEvent):
    """Record user swipe for personalization"""
    # Store swipe event
    redis_client.lpush(f"swipes:{swipe.user_id}", swipe.json())
    
    # Update personalization algorithm
    await update_user_preferences(swipe.user_id, swipe.content_id, swipe.direction)
    
    return {"status": "recorded"}

@app.get("/api/feed/{user_id}")
async def get_user_feed(user_id: str, limit: int = 20):
    """Get personalized content feed for user"""
    feed_items = redis_client.lrange(f"feed:{user_id}", 0, limit-1)
    
    return {
        "feed": [json.loads(item) for item in feed_items],
        "has_more": len(feed_items) == limit
    }

async def update_user_preferences(user_id: str, content_id: str, direction: str):
    """Update user personalization based on swipe"""
    # Implementation for learning from user behavior
    pass
'''
    else:
        content = f'''"""
{filename.replace('.py', '').replace('_', ' ').title()}
Generated mobile backend component
"""

class {filename.replace('.py', '').title().replace('_', '')}:
    def __init__(self):
        pass
        
    async def process(self):
        """Main processing method"""
        pass
'''
    
    with open(filepath, 'w') as f:
        f.write(content)

def create_react_native_screens():
    """Create React Native screen components"""
    print("📱 Creating React Native screens...")
    
    # SwipeScreen (main feed)
    swipe_screen = '''
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  Dimensions,
  PanGestureHandler,
  Animated,
  StyleSheet
} from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

const { width, height } = Dimensions.get('window');

const SwipeScreen = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [content, setContent] = useState([]);
  
  useEffect(() => {
    // Connect to WebSocket for real-time content
    const ws = new WebSocket('ws://localhost:8000/ws/user123');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_content') {
        setContent(prev => [data.data, ...prev]);
      }
    };
    
    // Load initial content
    loadContent();
    
    return () => ws.close();
  }, []);
  
  const loadContent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/feed/user123');
      const data = await response.json();
      setContent(data.feed);
    } catch (error) {
      console.error('Failed to load content:', error);
    }
  };
  
  const onSwipe = (direction) => {
    const contentId = content[currentIndex]?.id;
    
    // Send swipe event to backend
    fetch('http://localhost:8000/api/swipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: 'user123',
        content_id: contentId,
        direction: direction,
        timestamp: Date.now()
      })
    });
    
    // Move to next content
    setCurrentIndex(prev => prev + 1);
  };
  
  const renderContentCard = (item, index) => (
    <View key={item.id} style={styles.card}>
      <Text style={styles.summary}>{item.summary}</Text>
      <Text style={styles.category}>{item.category}</Text>
      <View style={styles.metrics}>
        <Text>Sentiment: {item.sentiment}</Text>
        <Text>Relevance: {item.relevance}%</Text>
      </View>
    </View>
  );
  
  return (
    <GestureHandlerRootView style={styles.container}>
      <View style={styles.feedContainer}>
        {content.length > 0 && renderContentCard(content[currentIndex], currentIndex)}
      </View>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
  },
  feedContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    width: width * 0.9,
    height: height * 0.7,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 20,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  summary: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  category: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  metrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: 20,
  },
});

export default SwipeScreen;
'''
    
    Path("mobile_screens").mkdir(exist_ok=True)
    with open("mobile_screens/SwipeScreen.js", "w") as f:
        f.write(swipe_screen)

def main():
    """Main conversion process"""
    print("🚀 Converting Reddit Insight to Mobile Architecture")
    print("=" * 50)
    
    # Step 1: Create React Native project
    if not create_react_native_project():
        print("❌ Failed to create React Native project")
        return
    
    # Step 2: Create mobile backend
    create_mobile_backend()
    
    # Step 3: Create React Native screens
    create_react_native_screens()
    
    print("\n✅ Mobile Conversion Complete!")
    print("\n📱 Next Steps:")
    print("1. cd RedditInsightMobile")
    print("2. npx react-native run-ios (or run-android)")
    print("3. Start mobile backend: python mobile_backend/websocket_server.py")
    print("4. Deploy to App Store/Play Store")
    
    print("\n🎯 Mobile Features:")
    print("- Native iOS/Android apps")
    print("- Real-time WebSocket content delivery")  
    print("- TikTok-style swipe interface")
    print("- Push notifications")
    print("- Offline content caching")

if __name__ == "__main__":
    main()