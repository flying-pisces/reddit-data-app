# 📱 Reddit Insight App - Complete Usage Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Python 3.8+ installed
- Apple Developer Account ($99/year) for App Store
- Reddit API credentials (in .env file)

### Installation
```bash
# Clone the repository
git clone git@github.com:flying-pisces/reddit-data-app.git
cd reddit-data-app

# Install dependencies
npm install
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your Reddit API credentials to .env
```

## 🎯 Running the Application

### Web Version (Development)
```bash
# Start the web application
npm start
# Opens at http://localhost:3000
```

### Mobile Development
```bash
# Navigate to mobile app directory
cd RedditInsightMobile

# Install dependencies
npm install

# iOS Simulator
npx expo run:ios

# Android Emulator
npx expo run:android

# Using Expo Go app (recommended for testing)
npx expo start --tunnel
# Scan QR code with Expo Go app
```

### Backend API
```bash
# Start the Python backend
cd backend
python api.py
# API runs at http://localhost:8000
```

### Serverless Deployment
```bash
# Deploy to Vercel
cd serverless
vercel deploy

# Deploy to AWS Lambda
serverless deploy
```

## 📊 Features & Usage

### 1. Authentication
- **Google Sign-In**: Click "Sign in with Google"
- **Apple Sign-In**: Click "Sign in with Apple"
- **Email**: Enter email and password

### 2. Onboarding (First-time users)
- Select interests: Finance, Technology, Crypto, etc.
- Choose specific subreddits to monitor
- Set notification preferences

### 3. TikTok-Style Feed
**Swipe Gestures:**
- **Swipe Right** → Save content to favorites
- **Swipe Left** → Mark as not interested
- **Swipe Up** → View detailed analysis
- **Swipe Down** → Skip category for 2 hours

### 4. Subscription Tiers
- **FREE**: 20 insights/day
- **PRO ($4.99/month)**: Unlimited insights
- **PREMIUM ($9.99/month)**: AI predictions + API access

## 🧪 Testing

### Run All Tests
```bash
# Frontend tests
npm test

# Backend tests
python -m pytest tests/

# End-to-end tests
npm run test:e2e
```

### Test Specific Components
```bash
# Test authentication
npm test -- --testPathPattern=Auth

# Test swipe functionality
npm test -- --testPathPattern=FeedScreen

# Test subscription management
npm test -- --testPathPattern=Subscription
```

### Manual Testing Checklist
- [ ] Authentication flow works
- [ ] Onboarding completes successfully
- [ ] Swipe gestures respond correctly
- [ ] Daily limit enforced for free users
- [ ] Subscription upgrade flow works
- [ ] Content loads from Reddit API
- [ ] AI summaries generate correctly
- [ ] Offline mode shows cached content

## 💰 Monetization Setup

### 1. Configure RevenueCat
```javascript
// In App.js
import Purchases from 'react-native-purchases';

Purchases.configure({
  apiKey: "YOUR_REVENUECAT_API_KEY"
});
```

### 2. Set Up In-App Purchases
1. Log in to App Store Connect
2. Go to "My Apps" → Your App → "Features" → "In-App Purchases"
3. Create subscriptions:
   - `reddit_insight_pro_monthly` - $4.99
   - `reddit_insight_premium_monthly` - $9.99

### 3. Configure Affiliate Links
```javascript
// In ContentCard.js
const affiliateLinks = {
  'TSLA': 'https://robinhood.com/signup?ref=your_code',
  'AAPL': 'https://etrade.com/signup?ref=your_code'
};
```

## 🚢 Deployment

### App Store Submission
```bash
# Build for production
cd ios
xcodebuild -scheme RedditInsight -configuration Release

# Archive in Xcode
# Product → Archive → Upload to App Store Connect
```

### Google Play Store
```bash
# Build APK
cd android
./gradlew assembleRelease

# Build AAB for Play Store
./gradlew bundleRelease
```

### Web Deployment
```bash
# Build production bundle
npm run build

# Deploy to Vercel
vercel --prod

# Deploy to Netlify
netlify deploy --prod
```

## 📁 Project Structure
```
reddit-data-app/
├── src/                    # React frontend code
│   ├── components/         # UI components
│   ├── screens/           # Screen components
│   └── services/          # API services
├── backend/               # Python backend
│   ├── api.py            # FastAPI server
│   └── intelligence/     # AI processing
├── serverless/           # Serverless functions
│   └── api/feed.py      # Feed generation
├── mobile/              # React Native app
│   ├── App.tsx         # Main app file
│   └── src/           # Mobile components
├── monetization/       # Revenue code
│   └── SubscriptionManager.js
└── tests/             # Test suites
```

## 🔧 Configuration Files

### .env (Environment Variables)
```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=RedditInsight/1.0

# OpenAI API (for summaries)
OPENAI_API_KEY=your_openai_key

# RevenueCat (for subscriptions)
REVENUECAT_API_KEY=your_revenuecat_key

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Firebase (for auth)
FIREBASE_API_KEY=your_firebase_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
```

### app.json (Expo Configuration)
```json
{
  "expo": {
    "name": "Reddit Insight",
    "slug": "reddit-insight",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.yourcompany.redditinsight",
      "buildNumber": "1.0.0"
    },
    "android": {
      "package": "com.yourcompany.redditinsight",
      "versionCode": 1
    }
  }
}
```

## 📈 Analytics & Monitoring

### Track Key Metrics
```javascript
// Track user engagement
AnalyticsService.trackEvent('content_swipe', {
  direction: 'right',
  category: 'finance',
  subscription_tier: 'FREE'
});

// Track revenue
AnalyticsService.trackRevenue('subscription_purchased', {
  tier: 'PRO',
  amount: 4.99,
  currency: 'USD'
});
```

### Monitor Performance
- **Sentry**: Crash reporting
- **Firebase Analytics**: User behavior
- **RevenueCat**: Subscription metrics
- **Mixpanel**: Custom events

## 🐛 Troubleshooting

### Common Issues

**Metro bundler errors:**
```bash
npx react-native start --reset-cache
```

**CocoaPods issues:**
```bash
cd ios && pod deintegrate && pod install
```

**Node modules issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Build failures:**
```bash
cd ios && xcodebuild clean
cd android && ./gradlew clean
```

## 📞 Support & Resources

- **Documentation**: [Full Docs](https://github.com/flying-pisces/reddit-data-app/wiki)
- **Issues**: [GitHub Issues](https://github.com/flying-pisces/reddit-data-app/issues)
- **Discord**: [Join Community](https://discord.gg/redditinsight)
- **Email**: support@redditinsight.app

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Credits

Built with:
- React Native & Expo
- Python & FastAPI
- Reddit API
- OpenAI API
- Firebase Auth
- RevenueCat

---

**Ready to launch? Follow the App Store submission guide in APP_STORE_SUBMISSION.md**