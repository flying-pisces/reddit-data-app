# Reddit Insight App 🚀

**Modern, AI-powered Reddit content discovery with TikTok-style swipe interface**

Transform your Reddit experience into a fast, personalized, and intelligent news discovery platform.

## ✨ Key Features

### 🎯 **Smart User Experience**
- **TikTok-style Interface**: Swipe through curated content effortlessly
- **One-Sentence Summaries**: Complex posts → Simple insights
- **Visual Data Charts**: Every story includes relevant visualizations  
- **Personalized Feed**: AI learns from your preferences

### 🤖 **AI-Powered Intelligence**
- **Advanced Summarization**: Long posts → Digestible insights
- **Multi-dimensional Scoring**: Relevance, sentiment, engagement analysis
- **Smart Categorization**: Auto-categorizes content by interest
- **Real-time Learning**: Adapts to your swipe patterns

### 📱 **Modern App Design**
- **Cross-platform**: Desktop app (Windows, Mac, Linux)
- **Responsive Design**: Works on any screen size
- **Beautiful UI**: Gradient themes with smooth animations
- **Touch-friendly**: Optimized for swipe gestures

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/flying-pisces/reddit-data-app.git
cd reddit-data-app

# Run the setup script
python setup_app_demo.py
```

### Method 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Setup Reddit API credentials
cp .env.example .env
# Edit .env with your Reddit API credentials

# Start the app
npm run electron-dev  # Desktop app
# OR
npm start            # Web version
```

## 🎮 How to Use

### **Swipe Gestures**
- **➡️ Swipe Right**: Save interesting content
- **⬅️ Swipe Left**: Not interested (less similar content)
- **⬆️ Swipe Up**: Get more details and full context
- **⬇️ Swipe Down**: Skip this category temporarily

### **First-Time Setup**
1. **Authentication**: Sign in with Google/Apple/Email
2. **Interest Selection**: Choose topics you care about
3. **Personalization**: App learns from your interactions
4. **Enjoy**: Start discovering relevant content!

## 🎯 Supported Content Categories

| **Category** | **Example Subreddits** | **Content Type** |
|--------------|------------------------|------------------|
| 💰 **Finance** | r/stocks, r/investing, r/wallstreetbets | Market analysis, stock discussions |
| 💻 **Technology** | r/technology, r/programming | Tech news, development trends |
| 🏃 **Lifestyle** | r/productivity, r/fitness | Life tips, health advice |
| 🎮 **Gaming** | r/gaming, r/pcgaming | Game news, reviews |
| 💼 **Business** | r/entrepreneur, r/startup | Business insights, career advice |

## 🔧 Advanced Configuration

### **AI Enhancement**
Add OpenAI API key to `.env` for premium summarization:
```bash
OPENAI_API_KEY=your_api_key_here
```

### **Custom Subreddits**
Edit `config.json` to monitor specific communities:
```json
{
  "monitoring": {
    "subreddits": ["your_custom_subreddit", "another_one"],
    "refresh_interval": 30
  }
}
```

### **Personalization Settings**
The app automatically learns from your behavior:
- Swipe patterns influence future content
- Time spent reading affects relevance scores
- Category preferences are continuously updated

## 📊 Technical Architecture

### **Frontend (React + Electron)**
- Modern React with hooks and context
- Framer Motion for smooth animations  
- Chart.js for data visualizations
- Styled Components for theming

### **Backend (Python)**
- Enhanced Reddit data engine
- AI-powered content processing
- Real-time personalization engine
- Multi-dimensional content scoring

### **Intelligence Layer**
```python
# Example: AI Summarization
summarizer = ContentSummarizer(model_type='openai')
summary = await summarizer.summarize_post(reddit_post)
# Returns: one-sentence summary + key points + sentiment
```

## 🔄 Development Workflow

### **Available Scripts**
```bash
# Development
npm run electron-dev    # Start Electron in dev mode
npm start              # Start React dev server
python main.py monitor # Start Python backend only

# Building
npm run build          # Build React app
npm run electron-build # Build Electron app
npm run dist          # Create distributable

# Testing
python main.py test    # Test Reddit API connection
python full_test.py    # Run full test suite
```

### **Project Structure**
```
reddit-data-app/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── context/           # React context
│   └── utils/             # Utilities
├── electron/              # Electron main process
├── backend/               # Python backend
│   ├── intelligence/      # AI services
│   └── personalization/   # Recommendation engine
├── public/                # Static assets
└── package.json          # Dependencies
```

## 🎨 UI/UX Innovation

### **Card-Based Design**
Each news item is presented as a beautiful card with:
- **Header**: Category and source information
- **Summary**: One-sentence AI-generated insight
- **Visualization**: Relevant chart or graph
- **Metrics**: Sentiment, relevance, engagement scores
- **Actions**: Quick access to original content

### **Swipe Feedback System**
- **Visual Indicators**: Clear feedback for each swipe direction
- **Haptic Feedback**: Physical response on supported devices
- **Learning Animations**: Show how your preferences are being learned

### **Personalization Dashboard**
- **Interest Evolution**: See how your interests change over time
- **Content Analytics**: Understand your reading patterns
- **Recommendation Tuning**: Fine-tune the AI recommendations

## 🚀 Deployment Options

### **Desktop App Distribution**
```bash
# Build for multiple platforms
npm run dist                    # Current platform
npm run dist -- --mac         # macOS
npm run dist -- --win         # Windows  
npm run dist -- --linux       # Linux
```

### **Web Deployment**
```bash
# Build for web hosting
npm run build
# Deploy the build/ directory to your hosting provider
```

### **Cloud Backend**
The Python backend can be deployed to:
- **Heroku**: `Procfile` included
- **AWS Lambda**: Serverless deployment
- **Docker**: `Dockerfile` for containerization

## 📈 Performance & Scalability

### **Optimization Features**
- **Smart Caching**: Reduces API calls and improves speed
- **Lazy Loading**: Load content as needed
- **Background Processing**: AI summarization runs in background
- **Memory Management**: Efficient handling of large datasets

### **Metrics & Analytics**
- Real-time performance monitoring
- User engagement tracking
- Content relevance scoring
- Recommendation accuracy metrics

## 🛡️ Privacy & Security

- **Local Storage**: User preferences stored locally
- **No Data Collection**: We don't collect personal information
- **API Security**: Secure Reddit API integration
- **Open Source**: Full transparency in code

## 🤝 Contributing

We welcome contributions! Areas for improvement:

1. **New AI Models**: Integrate additional summarization models
2. **UI Enhancements**: Improve the swipe interface
3. **Content Sources**: Support additional platforms beyond Reddit
4. **Mobile App**: React Native version
5. **Browser Extension**: Chrome/Firefox extension

## 📜 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- **Original Engine**: Built upon the robust Reddit data engine
- **UI Inspiration**: Modern mobile app design patterns
- **AI Integration**: OpenAI for advanced text processing
- **Community**: Reddit for providing access to community data

---

## 🌟 Transform Your Reddit Experience Today!

**From overwhelming information → To personalized insights**

Stop scrolling endlessly through Reddit. Let AI curate the most relevant content for you in a beautiful, swipe-friendly interface.

[Download the App](https://github.com/flying-pisces/reddit-data-app/releases) | [Try Web Version](https://flying-pisces.github.io/reddit-data-app) | [Read the Docs](docs/)