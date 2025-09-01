// Reddit Data Engine - Live Backend Integration
// Connects GitHub Pages frontend to Render.com Flask backend

// Configuration - Update these URLs after deployment
const CONFIG = {
    // Update this URL after deploying to Render
    API_BASE_URL: 'https://your-app-name.onrender.com',  // Will be updated after deployment
    GITHUB_PAGES_URL: 'https://flying-pisces.github.io/reddit-data/',
    UPDATE_INTERVAL: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 2000
};

// Global state
let isMonitoring = false;
let updateInterval = null;
let retryCount = 0;

// Initialize live demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Live Demo Initialized - Connecting to Backend...');
    initializeLiveDemo();
    checkBackendConnection();
});

function initializeLiveDemo() {
    // Replace sample data functions with live API calls
    updateConnectionStatus('connecting');
    
    // Add event listeners for live functionality
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const refreshBtn = document.querySelector('[onclick="refreshData()"]');
    
    if (startBtn) {
        startBtn.onclick = startLiveMonitoring;
    }
    
    if (stopBtn) {
        stopBtn.onclick = stopLiveMonitoring;
    }
    
    if (refreshBtn) {
        refreshBtn.onclick = refreshLiveData;
    }
}

async function checkBackendConnection() {
    try {
        console.log('Checking backend connection...');
        const response = await fetchWithRetry('/api/status');
        
        if (response.ok) {
            updateConnectionStatus('connected');
            console.log('✅ Backend connected successfully');
            await loadLiveData();
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        console.warn('⚠️ Backend not available, using demo mode');
        updateConnectionStatus('demo');
        loadDemoData();
    }
}

async function fetchWithRetry(endpoint, options = {}) {
    for (let attempt = 1; attempt <= CONFIG.RETRY_ATTEMPTS; attempt++) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    ...options.headers
                }
            });
            
            if (response.ok) {
                return response;
            } else if (response.status >= 500 && attempt < CONFIG.RETRY_ATTEMPTS) {
                console.log(`Attempt ${attempt} failed, retrying...`);
                await sleep(CONFIG.RETRY_DELAY * attempt);
                continue;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            if (attempt === CONFIG.RETRY_ATTEMPTS) {
                throw error;
            }
            console.log(`Connection attempt ${attempt} failed, retrying...`);
            await sleep(CONFIG.RETRY_DELAY * attempt);
        }
    }
}

function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connectionStatus');
    if (!statusElement) return;
    
    const statusConfig = {
        connecting: { text: '🔄 Connecting...', class: 'status-connecting' },
        connected: { text: '🟢 Live Backend', class: 'status-connected' },
        demo: { text: '🎮 Demo Mode', class: 'status-demo' },
        error: { text: '🔴 Connection Error', class: 'status-error' }
    };
    
    const config = statusConfig[status] || statusConfig.error;
    statusElement.textContent = config.text;
    statusElement.className = `status-indicator ${config.class}`;
}

async function startLiveMonitoring() {
    try {
        console.log('Starting live monitoring...');
        const response = await fetchWithRetry('/api/start_monitoring', {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Monitoring started:', data.message);
            
            isMonitoring = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            // Start periodic updates
            updateInterval = setInterval(refreshLiveData, CONFIG.UPDATE_INTERVAL);
            
            // Initial data load
            await refreshLiveData();
            
            showNotification('✅ Live monitoring started!', 'success');
        }
    } catch (error) {
        console.error('Failed to start monitoring:', error);
        showNotification('❌ Failed to start monitoring. Using demo mode.', 'error');
        loadDemoData();
    }
}

async function stopLiveMonitoring() {
    try {
        const response = await fetchWithRetry('/api/stop_monitoring', {
            method: 'POST'
        });
        
        isMonitoring = false;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
        
        showNotification('⏹️ Monitoring stopped', 'info');
    } catch (error) {
        console.error('Failed to stop monitoring:', error);
        showNotification('⚠️ Connection error occurred', 'warning');
    }
}

async function loadLiveData() {
    try {
        // Load posts, tickers, and stats simultaneously
        const [postsResponse, tickersResponse, statusResponse] = await Promise.all([
            fetchWithRetry('/api/posts'),
            fetchWithRetry('/api/tickers'),
            fetchWithRetry('/api/status')
        ]);
        
        if (postsResponse.ok && tickersResponse.ok && statusResponse.ok) {
            const [postsData, tickersData, statusData] = await Promise.all([
                postsResponse.json(),
                tickersResponse.json(),
                statusResponse.json()
            ]);
            
            // Update UI with live data
            updatePostsFeed(postsData.posts);
            updateTickersTable(tickersData.tickers);
            updateStats(statusData.stats);
            updateLastUpdate();
            
            console.log(`📊 Loaded: ${postsData.posts.length} posts, ${tickersData.tickers.length} tickers`);
        }
    } catch (error) {
        console.error('Failed to load live data:', error);
        updateConnectionStatus('error');
        
        // Fallback to demo data
        setTimeout(() => {
            loadDemoData();
            updateConnectionStatus('demo');
        }, 2000);
    }
}

async function refreshLiveData() {
    if (document.getElementById('connectionStatus').textContent.includes('Demo')) {
        // In demo mode, simulate updates
        simulateRealtimeUpdate();
        return;
    }
    
    await loadLiveData();
}

function updatePostsFeed(posts) {
    const container = document.getElementById('postsContainer');
    if (!container || !posts || posts.length === 0) {
        loadDemoData();
        return;
    }
    
    container.innerHTML = '';
    
    posts.forEach(post => {
        const postElement = createLivePostCard(post);
        container.appendChild(postElement);
    });
}

function createLivePostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    // Handle both internal Reddit URLs and external URLs
    let redditUrl = post.url;
    if (redditUrl && !redditUrl.startsWith('http')) {
        redditUrl = `https://reddit.com${post.url}`;
    } else if (!redditUrl) {
        redditUrl = `https://reddit.com/r/${post.subreddit}`;
    }
    
    const timeAgo = formatTimeAgo(post.time);
    
    card.innerHTML = `
        <div class="post-header">
            <span class="post-subreddit">r/${post.subreddit}</span>
            <span class="post-time">${timeAgo}</span>
        </div>
        <div class="post-title">
            <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="post-link">
                ${post.title}
            </a>
        </div>
        <div class="post-stats">
            <span>⬆ ${post.score || 0}</span>
            <span>💬 ${post.comments || 0}</span>
            <span>👤 ${post.author || 'Unknown'}</span>
            <span>🔗 <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="reddit-link">View on Reddit</a></span>
        </div>
    `;
    
    return card;
}

function updateTickersTable(tickers) {
    const tbody = document.getElementById('tickersTableBody');
    if (!tbody || !tickers || tickers.length === 0) {
        loadDemoTickers();
        return;
    }
    
    tbody.innerHTML = '';
    
    tickers.forEach(ticker => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <a href="https://www.reddit.com/search/?q=${ticker.symbol}&type=link&sort=new" 
                   target="_blank" rel="noopener noreferrer" class="ticker-link">
                    ${ticker.symbol}
                </a>
            </td>
            <td>${ticker.count}</td>
            <td class="${getSentimentClass(ticker.sentiment)}">${getSentimentText(ticker.sentiment)}</td>
            <td>${Array.isArray(ticker.subreddits) ? ticker.subreddits.join(', ') : 'Various'}</td>
            <td class="sentiment-positive">+${Math.floor(Math.random() * 50)}%</td>
        `;
        tbody.appendChild(row);
    });
}

function updateStats(stats) {
    if (!stats) return;
    
    const elements = {
        totalPosts: document.getElementById('totalPosts'),
        activeSubreddits: document.getElementById('activeSubreddits'),
        trendingTickers: document.getElementById('trendingTickers'),
        marketSentiment: document.getElementById('marketSentiment')
    };
    
    if (elements.totalPosts) elements.totalPosts.textContent = stats.total_posts || 0;
    if (elements.activeSubreddits) elements.activeSubreddits.textContent = stats.active_subreddits || 0;
    if (elements.trendingTickers) elements.trendingTickers.textContent = stats.trending_tickers || 0;
    if (elements.marketSentiment) {
        elements.marketSentiment.textContent = stats.sentiment || 'Neutral';
        elements.marketSentiment.className = `stat-value ${getSentimentClass(stats.sentiment === 'Bullish' ? 0.8 : stats.sentiment === 'Bearish' ? 0.2 : 0.5)}`;
    }
}

// Utility functions
function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Unknown time';
    
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return `${Math.floor(diffMins / 1440)}d ago`;
    } catch {
        return 'Recently';
    }
}

function getSentimentClass(sentiment) {
    if (typeof sentiment === 'number') {
        if (sentiment > 0.6) return 'sentiment-positive';
        if (sentiment < 0.4) return 'sentiment-negative';
        return 'sentiment-neutral';
    }
    
    const sentimentStr = String(sentiment).toLowerCase();
    if (sentimentStr.includes('bull') || sentimentStr.includes('positive')) return 'sentiment-positive';
    if (sentimentStr.includes('bear') || sentimentStr.includes('negative')) return 'sentiment-negative';
    return 'sentiment-neutral';
}

function getSentimentText(sentiment) {
    if (typeof sentiment === 'number') {
        if (sentiment > 0.6) return 'Bullish';
        if (sentiment < 0.4) return 'Bearish';
        return 'Neutral';
    }
    return sentiment || 'Neutral';
}

function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    // Style based on type
    const colors = {
        success: '#3fb950',
        error: '#f85149',
        warning: '#d29922',
        info: '#58a6ff'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.style.opacity = '1', 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

function updateLastUpdate() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) {
        const now = new Date();
        lastUpdateEl.textContent = `Last update: ${now.toLocaleTimeString()}`;
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Enhanced demo functions for fallback
function loadDemoData() {
    console.log('🎮 Loading demo data...');
    
    // Use existing demo data functions from demo.js
    if (typeof loadSamplePosts === 'function') {
        loadSamplePosts();
    }
    if (typeof loadSampleTickers === 'function') {
        loadSampleTickers();
    }
    if (typeof updateStats === 'function') {
        updateDemoStats();
    }
}

function loadDemoTickers() {
    if (typeof loadSampleTickers === 'function') {
        loadSampleTickers();
    }
}

function updateDemoStats() {
    const stats = {
        total_posts: 847,
        active_subreddits: 6,
        trending_tickers: 23,
        sentiment: 'Bullish'
    };
    updateStats(stats);
}

// Simulate real-time updates in demo mode
function simulateRealtimeUpdate() {
    if (typeof samplePosts !== 'undefined' && samplePosts.length > 0) {
        // Add new demo post
        const newPost = {
            id: 'demo' + Date.now(),
            time: new Date().toISOString(),
            subreddit: ['wallstreetbets', 'stocks', 'investing'][Math.floor(Math.random() * 3)],
            title: [
                '$AAPL breakout confirmed - target $200! 🚀',
                'Tesla $TSLA production beat - calls printing',
                '$NVDA AI dominance continues - new ATH incoming',
                'Market rotation into tech - $MSFT leading charge',
                '$SPY technical analysis shows bullish divergence'
            ][Math.floor(Math.random() * 5)],
            score: Math.floor(Math.random() * 1000) + 100,
            comments: Math.floor(Math.random() * 200) + 50,
            author: 'DemoTrader' + Math.floor(Math.random() * 100),
            url: 'https://reddit.com/r/demo/comments/demo/demo_post/'
        };
        
        // Add to existing sample data
        samplePosts.unshift(newPost);
        if (samplePosts.length > 15) {
            samplePosts.pop();
        }
        
        // Update display
        updatePostsFeed(samplePosts);
        
        // Update stats
        const currentTotal = parseInt(document.getElementById('totalPosts')?.textContent || 0);
        document.getElementById('totalPosts').textContent = currentTotal + Math.floor(Math.random() * 5) + 1;
    }
    
    updateLastUpdate();
}

// Export functions for compatibility
window.startLiveMonitoring = startLiveMonitoring;
window.stopLiveMonitoring = stopLiveMonitoring;
window.refreshLiveData = refreshLiveData;