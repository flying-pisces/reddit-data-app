# 🔗 Live Backend Deployment Guide

## Architecture Overview

**Frontend**: GitHub Pages (Static) → **Backend**: Render.com (Flask API)

Your setup:
- **GitHub Pages**: `https://flying-pisces.github.io/reddit-data/`
- **Render Backend**: `https://your-app-name.onrender.com` (will be created)

## 🚀 Step 1: Deploy Flask Backend to Render

### 1. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Connect your `reddit-data` repository

### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your `flying-pisces/reddit-data` repository
3. Configure settings:

```
Name: reddit-data-engine-api
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: cd gui/web_app && gunicorn --bind 0.0.0.0:$PORT app:app
```

### 3. Set Environment Variables
In Render dashboard, add these environment variables:

```bash
# Required Reddit API credentials
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=reddit-data-engine:v1.0:production

# Flask configuration
FLASK_ENV=production
PYTHONPATH=.
```

### 4. Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Your backend URL will be: `https://reddit-data-engine-api.onrender.com`

## 🔧 Step 2: Connect GitHub Pages Frontend

### Update Backend URL
Edit `docs/assets/js/live-demo.js`, line 6:

```javascript
const CONFIG = {
    // Replace with your actual Render URL
    API_BASE_URL: 'https://reddit-data-engine-api.onrender.com',
    // ... rest of config
};
```

### Push Changes to GitHub
```bash
git add .
git commit -m "Connect GitHub Pages to live Render backend 🔗"
git push origin main
```

## 🎯 Step 3: Test Live Integration

### 1. Visit Your GitHub Pages Site
```
https://flying-pisces.github.io/reddit-data/
```

### 2. Expected Behavior
- **Connection Status**: Should show "🟢 Live Backend" (instead of "🎮 Demo Mode")
- **Start Monitoring**: Click button to begin live Reddit monitoring
- **Real Data**: Posts and tickers update with actual Reddit data
- **Live Updates**: Data refreshes every 30 seconds automatically

### 3. Fallback Behavior
If backend is unavailable:
- Status shows "🎮 Demo Mode"
- Uses sample data for demonstration
- No functionality is lost

## 🔄 How It Works

### Frontend (GitHub Pages)
```javascript
// Tries to connect to live backend
const response = await fetch('https://your-backend.onrender.com/api/status');

if (response.ok) {
    // Use live data from Flask API
    loadLiveData();
} else {
    // Fallback to demo mode
    loadDemoData();
}
```

### Backend (Render.com)
```python
# Flask API endpoints available:
GET  /api/status      # Monitor status
GET  /api/posts       # Live Reddit posts  
GET  /api/tickers     # Trending tickers
POST /api/start_monitoring  # Start live monitoring
POST /api/stop_monitoring   # Stop monitoring
```

### CORS Configuration
```python
# Allows GitHub Pages to access Render backend
CORS(app, origins=["https://flying-pisces.github.io"])
```

## ⚡ Benefits of This Setup

### ✅ **Professional**
- Live backend with real Reddit data
- Professional URLs and hosting
- No "localhost" limitations

### ✅ **Free**
- GitHub Pages: Free static hosting
- Render: Free tier for backend APIs
- Total cost: $0/month

### ✅ **Scalable**
- Render auto-scales with traffic
- GitHub Pages handles global CDN
- Backend can be upgraded if needed

### ✅ **Reliable**
- Automatic fallback to demo mode
- No single point of failure
- Both platforms have 99.9% uptime

## 🛠️ Advanced Configuration

### Custom Domain (Optional)
1. **Frontend**: Configure custom domain in GitHub Pages settings
2. **Backend**: Add custom domain in Render dashboard
3. **Update CORS**: Add your domain to allowed origins

### Environment-Specific Config
```javascript
const CONFIG = {
    API_BASE_URL: process.env.NODE_ENV === 'production' 
        ? 'https://reddit-data-engine-api.onrender.com'
        : 'http://localhost:5000',
    // ...
};
```

### Database Integration
If you add database later:
1. Use Render's PostgreSQL add-on (free tier available)
2. Update `config/database.json` with Render database URL
3. Backend automatically persists data

## 🚨 Important Notes

### Render Free Tier Limitations
- **Cold starts**: App sleeps after 15 minutes of inactivity
- **Wake-up time**: 30-60 seconds for first request
- **Monthly hours**: 750 hours/month (enough for most usage)

### Reddit API Setup Required
Backend needs your Reddit API credentials:
1. Get credentials from https://reddit.com/prefs/apps
2. Add to Render environment variables
3. Keep credentials secure (never commit to git)

### Monitoring
- **Backend logs**: Available in Render dashboard
- **Frontend errors**: Check browser console
- **API status**: Monitor `/api/status` endpoint

## 🎯 Testing Checklist

- [ ] Backend deployed successfully to Render
- [ ] Environment variables configured
- [ ] GitHub Pages updated with backend URL
- [ ] Connection status shows "Live Backend"
- [ ] Start/Stop monitoring works
- [ ] Real Reddit data displays
- [ ] URLs are clickable and functional
- [ ] Graceful fallback to demo mode if needed

## 🎉 Success!

Once complete, you'll have:
- **Professional live demo** at `https://flying-pisces.github.io/reddit-data/`
- **Real-time Reddit monitoring** powered by live Flask backend
- **Zero hosting costs** with enterprise-grade reliability
- **Impressive presentation** for sponsors and contributors

This setup showcases your project as a **production-ready application** rather than just a GitHub repository, significantly increasing sponsorship and contribution potential! 🚀