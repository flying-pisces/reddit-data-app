// GitHub Pages Static Data Integration
// Loads data from GitHub Actions generated JSON files

const GITHUB_DATA_CONFIG = {
    BASE_PATH: './data/',  // Relative path to data files
    FILES: {
        posts: 'posts.json',
        tickers: 'tickers.json', 
        stats: 'stats.json',
        analysis: 'analysis.json',
        history: 'history.json'
    },
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutes cache
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
};

// Data cache
let dataCache = {
    posts: null,
    tickers: null,
    stats: null,
    analysis: null,
    history: null,
    lastUpdated: null
};

// Initialize GitHub data system
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 GitHub Data System Initialized');
    initializeGitHubData();
    
    // Initialize charts after a small delay to ensure DOM is ready
    setTimeout(() => {
        initializeEnhancedCharts();
    }, 1000);
    
    // Set up periodic refresh (every 5 minutes to check for new data)
    setInterval(checkForDataUpdates, 5 * 60 * 1000);
});

async function initializeGitHubData() {
    updateConnectionStatus('github-loading');
    
    try {
        // Load all data files
        await loadAllGitHubData();
        updateConnectionStatus('github-connected');
        
        // Display the data
        displayGitHubData();
        
        console.log('✅ GitHub data loaded successfully');
    } catch (error) {
        console.warn('⚠️ GitHub data not available, using demo mode');
        updateConnectionStatus('demo');
        loadDemoData();
    }
}

async function loadAllGitHubData() {
    const promises = Object.entries(GITHUB_DATA_CONFIG.FILES).map(async ([key, filename]) => {
        try {
            const data = await fetchGitHubFile(filename);
            dataCache[key] = data;
            return { key, data, success: true };
        } catch (error) {
            console.warn(`Failed to load ${filename}:`, error.message);
            return { key, data: null, success: false };
        }
    });
    
    const results = await Promise.all(promises);
    
    // Check if we have essential data
    const essentialFiles = ['posts', 'stats'];
    const hasEssentialData = essentialFiles.every(key => 
        results.find(r => r.key === key)?.success
    );
    
    if (!hasEssentialData) {
        throw new Error('Essential data files not available');
    }
    
    dataCache.lastUpdated = new Date();
    console.log('📊 Loaded GitHub data:', results.filter(r => r.success).map(r => r.key));
}

async function fetchGitHubFile(filename) {
    const url = `${GITHUB_DATA_CONFIG.BASE_PATH}${filename}`;
    
    for (let attempt = 1; attempt <= GITHUB_DATA_CONFIG.RETRY_ATTEMPTS; attempt++) {
        try {
            const response = await fetch(url, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });
            
            if (!response.ok) {
                if (response.status === 404 && attempt === GITHUB_DATA_CONFIG.RETRY_ATTEMPTS) {
                    throw new Error(`Data file ${filename} not found - GitHub Actions may not have run yet`);
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            if (attempt === GITHUB_DATA_CONFIG.RETRY_ATTEMPTS) {
                throw error;
            }
            await sleep(GITHUB_DATA_CONFIG.RETRY_DELAY * attempt);
        }
    }
}

function displayGitHubData() {
    if (dataCache.posts) {
        displayGitHubPosts(dataCache.posts);
    }
    
    if (dataCache.tickers) {
        displayGitHubTickers(dataCache.tickers);
    }
    
    if (dataCache.stats) {
        displayGitHubStats(dataCache.stats);
    }
    
    if (dataCache.analysis) {
        displayGitHubAnalysis(dataCache.analysis);
    }
    
    updateDataTimestamp();
}

function displayGitHubPosts(posts) {
    const container = document.getElementById('postsContainer');
    if (!container || !posts || posts.length === 0) {
        console.warn('No posts data available');
        return;
    }
    
    container.innerHTML = '';
    
    // Sort by score and take top posts for display
    const sortedPosts = [...posts].sort((a, b) => b.score - a.score).slice(0, 20);
    
    sortedPosts.forEach(post => {
        const postElement = createGitHubPostCard(post);
        container.appendChild(postElement);
    });
    
    console.log(`📰 Displayed ${sortedPosts.length} posts`);
}

function createGitHubPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    // Handle URLs (internal Reddit URLs vs external URLs)
    let redditUrl = post.url;
    if (redditUrl && !redditUrl.startsWith('http')) {
        redditUrl = `https://reddit.com${post.url}`;
    } else if (!redditUrl) {
        redditUrl = `https://reddit.com/r/${post.subreddit}/comments/${post.id}/`;
    }
    
    // Format timestamp
    const timeAgo = formatGitHubTimestamp(post.created_utc || post.timestamp);
    
    // Truncate long titles
    const displayTitle = post.title.length > 100 ? 
        post.title.substring(0, 100) + '...' : 
        post.title;
    
    card.innerHTML = `
        <div class="post-header">
            <span class="post-subreddit">r/${post.subreddit}</span>
            <span class="post-time">${timeAgo}</span>
            <span class="post-live-badge">🔄 Live Data</span>
        </div>
        <div class="post-title">
            <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="post-link">
                ${displayTitle}
            </a>
        </div>
        <div class="post-stats">
            <span>⬆ ${formatNumber(post.score)}</span>
            <span>💬 ${formatNumber(post.num_comments || post.comments || 0)}</span>
            <span>👤 ${post.author}</span>
            <span>🔗 <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="reddit-link">View on Reddit</a></span>
        </div>
    `;
    
    return card;
}

function displayGitHubTickers(tickers) {
    const tbody = document.getElementById('tickersTableBody');
    if (!tbody || !tickers) {
        console.warn('No tickers data available');
        return;
    }
    
    tbody.innerHTML = '';
    
    // Convert to array and sort by mentions
    const tickerArray = Object.entries(tickers)
        .map(([symbol, count]) => ({ symbol, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 20);
    
    tickerArray.forEach(ticker => {
        const row = document.createElement('tr');
        
        // Generate mock sentiment for display (in real app, this would come from analysis)
        const mockSentiment = Math.random();
        const trendChange = (Math.random() * 100 - 50).toFixed(1);
        const trendClass = trendChange >= 0 ? 'sentiment-positive' : 'sentiment-negative';
        const trendSymbol = trendChange >= 0 ? '+' : '';
        
        row.innerHTML = `
            <td>
                <a href="https://www.reddit.com/search/?q=${encodeURIComponent(ticker.symbol)}&type=link&sort=new" 
                   target="_blank" rel="noopener noreferrer" class="ticker-link">
                    ${ticker.symbol}
                </a>
            </td>
            <td><strong>${ticker.count}</strong></td>
            <td class="${getSentimentClass(mockSentiment)}">${getSentimentText(mockSentiment)}</td>
            <td>Multiple</td>
            <td class="${trendClass}">${trendSymbol}${trendChange}%</td>
        `;
        
        tbody.appendChild(row);
    });
    
    console.log(`💹 Displayed ${tickerArray.length} tickers`);
}

function displayGitHubStats(statsData) {
    if (!statsData) return;
    
    const metadata = statsData.metadata || {};
    const subredditStats = statsData.subreddit_stats || {};
    
    // Update main stats cards
    const elements = {
        totalPosts: document.getElementById('totalPosts'),
        activeSubreddits: document.getElementById('activeSubreddits'), 
        trendingTickers: document.getElementById('trendingTickers'),
        marketSentiment: document.getElementById('marketSentiment')
    };
    
    if (elements.totalPosts) {
        elements.totalPosts.textContent = metadata.total_posts || 0;
    }
    
    if (elements.activeSubreddits) {
        elements.activeSubreddits.textContent = Object.keys(subredditStats).length || 0;
    }
    
    if (elements.trendingTickers) {
        elements.trendingTickers.textContent = metadata.total_tickers || 0;
    }
    
    // Set default sentiment (will be updated by analysis if available)
    if (elements.marketSentiment && !dataCache.analysis) {
        elements.marketSentiment.textContent = 'Active';
        elements.marketSentiment.className = 'stat-value sentiment-neutral';
    }
}

function displayGitHubAnalysis(analysis) {
    if (!analysis) return;
    
    // Update market sentiment
    const sentimentElement = document.getElementById('marketSentiment');
    if (sentimentElement) {
        sentimentElement.textContent = analysis.overall_sentiment || 'Neutral';
        sentimentElement.className = `stat-value ${getSentimentClass(analysis.overall_sentiment)}`;
    }
    
    // Update insights if there's an insights container
    const insightsContainer = document.getElementById('insightsContent');
    if (insightsContainer && analysis.insights) {
        const insightsHtml = `
            <h4>📈 Live Market Analysis</h4>
            <p><em>Based on ${dataCache.stats?.metadata?.total_posts || 0} Reddit posts from the last hour</em></p>
            ${analysis.insights.map(insight => `<p>• ${insight}</p>`).join('')}
            <p><strong>Analysis updated:</strong> ${formatGitHubTimestamp(analysis.analysis_timestamp)}</p>
        `;
        insightsContainer.innerHTML = insightsHtml;
    }
}

async function checkForDataUpdates() {
    // Check if it's time to refresh data
    if (!dataCache.lastUpdated || 
        Date.now() - dataCache.lastUpdated.getTime() > GITHUB_DATA_CONFIG.CACHE_DURATION) {
        
        console.log('🔄 Checking for data updates...');
        
        try {
            await loadAllGitHubData();
            displayGitHubData();
            showGitHubNotification('📊 Data updated with latest Reddit activity', 'success');
        } catch (error) {
            console.warn('Failed to update data:', error);
        }
    }
}

function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connectionStatus');
    if (!statusElement) return;
    
    const statusConfig = {
        'github-loading': { text: '📊 Loading GitHub Data...', class: 'status-connecting' },
        'github-connected': { text: '📊 GitHub Data Live', class: 'status-connected' },
        'demo': { text: '🎮 Demo Mode', class: 'status-demo' },
        'error': { text: '❌ Data Error', class: 'status-error' }
    };
    
    const config = statusConfig[status] || statusConfig.error;
    statusElement.textContent = config.text;
    statusElement.className = `status-indicator ${config.class}`;
}

function updateDataTimestamp() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    const dataTimestamp = document.getElementById('dataTimestamp');
    
    if (dataCache.stats?.metadata?.last_updated) {
        const updateTime = new Date(dataCache.stats.metadata.last_updated);
        const timeString = `${updateTime.toLocaleDateString()} ${updateTime.toLocaleTimeString()}`;
        
        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Last update: ${timeString} (GitHub Actions)`;
        }
        
        if (dataTimestamp) {
            dataTimestamp.textContent = `Last updated: ${timeString}`;
        }
    }
}

// Placeholder functions for demo buttons
function startMonitoring() {
    showGitHubNotification('📊 GitHub Actions handles monitoring automatically every hour', 'info');
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
}

function stopMonitoring() {
    showGitHubNotification('ℹ️ Monitoring continues via GitHub Actions schedule', 'info');
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
}

function refreshData() {
    showGitHubNotification('🔄 Checking for latest GitHub Actions data...', 'info');
    checkForDataUpdates();
}

// Utility functions
function formatGitHubTimestamp(timestamp) {
    if (!timestamp) return 'Unknown time';
    
    try {
        let date;
        if (typeof timestamp === 'number') {
            // Unix timestamp
            date = new Date(timestamp * 1000);
        } else {
            // ISO string
            date = new Date(timestamp);
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / (1000 * 60));
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return `${Math.floor(diffMins / 1440)}d ago`;
    } catch {
        return 'Recently';
    }
}

function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
}

function getSentimentClass(sentiment) {
    if (typeof sentiment === 'number') {
        if (sentiment > 0.6) return 'sentiment-positive';
        if (sentiment < 0.4) return 'sentiment-negative';
        return 'sentiment-neutral';
    }
    
    const sentimentStr = String(sentiment).toLowerCase();
    if (sentimentStr.includes('bull') || sentimentStr === 'bullish') return 'sentiment-positive';
    if (sentimentStr.includes('bear') || sentimentStr === 'bearish') return 'sentiment-negative';
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

function showGitHubNotification(message, type = 'info') {
    // Create notification
    const toast = document.createElement('div');
    toast.className = `github-toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">📊</span>
            <span class="toast-message">${message}</span>
        </div>
    `;
    
    // Style the notification
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        max-width: 300px;
    `;
    
    const colors = {
        success: '#3fb950',
        info: '#58a6ff',
        warning: '#d29922',
        error: '#f85149'
    };
    
    toast.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.style.opacity = '1', 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Enhanced demo fallback functions
function loadDemoData() {
    console.log('🎮 Loading demo data as fallback...');
    
    // Use existing demo functions if available
    if (typeof loadSamplePosts === 'function') {
        loadSamplePosts();
    }
    if (typeof loadSampleTickers === 'function') {
        loadSampleTickers();
    }
    
    // Set demo stats
    const demoStats = {
        total_posts: 847,
        active_subreddits: 8,
        trending_tickers: 23
    };
    
    displayGitHubStats({ metadata: demoStats, subreddit_stats: {} });
}

// Enhanced chart initialization
function initializeEnhancedCharts() {
    console.log('📈 Initializing enhanced charts...');
    try {
        initializeActivityChart();
        initializeTickersChart(); 
        console.log('✅ Charts initialized successfully');
    } catch (error) {
        console.warn('⚠️ Chart initialization failed:', error);
        // Fallback to basic charts
        setTimeout(() => {
            if (typeof initializeCharts === 'function') {
                initializeCharts();
            }
        }, 500);
    }
}

// Global chart instances to prevent recreation
let activityChartInstance = null;
let tickersChartInstance = null;

function initializeActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) {
        console.warn('Activity chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (activityChartInstance) {
        activityChartInstance.destroy();
    }
    
    // Use real data if available, otherwise generate realistic sample data
    const historyData = dataCache.history || generateExtendedSampleHistory();
    
    const labels = [];
    const postCounts = [];
    
    // Generate last 24 hours of data (longer timespan to avoid blanks)
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
        const hour = new Date(now.getTime() - i * 60 * 60 * 1000);
        labels.push(hour.getHours().toString().padStart(2, '0') + ':00');
        
        // Use real data or generate realistic sample
        if (historyData && historyData.length > i) {
            postCounts.push(historyData[historyData.length - 1 - i]?.total_posts || 0);
        } else {
            // Generate realistic activity pattern (higher during US trading hours)
            const hourNum = hour.getHours();
            let baseActivity = 15;
            if (hourNum >= 9 && hourNum <= 16) baseActivity = 70; // Trading hours
            if (hourNum >= 18 && hourNum <= 23) baseActivity = 45; // Evening activity
            if (hourNum >= 0 && hourNum <= 6) baseActivity = 8;   // Late night/early morning
            postCounts.push(baseActivity + Math.floor(Math.random() * 25));
        }
    }
    
    // Ensure we always have data - add fallback minimum values
    const safePostCounts = postCounts.map(count => Math.max(count, 5));
    
    activityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Posts per Hour',
                data: safePostCounts,
                borderColor: '#58a6ff',
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#58a6ff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#f0f6fc',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(13, 17, 23, 0.9)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#8b949e',
                    borderColor: '#30363d',
                    borderWidth: 1
                },
                // Add empty state plugin
                emptyState: {
                    enabled: true,
                    message: 'Activity data loading...',
                    color: '#8b949e'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: Math.max(...safePostCounts) + 20,
                    ticks: {
                        color: '#8b949e',
                        font: {
                            size: 11
                        },
                        stepSize: 20
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.8)',
                        drawBorder: false,
                        lineWidth: 1
                    },
                    title: {
                        display: true,
                        text: 'Posts per Hour',
                        color: '#8b949e',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    ticks: {
                        color: '#8b949e',
                        font: {
                            size: 11
                        },
                        maxTicksLimit: 12
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)',
                        drawBorder: false
                    },
                    title: {
                        display: true,
                        text: 'Time (24 Hour Period)',
                        color: '#8b949e',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            // Prevent animation flickering
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    console.log('📈 Activity chart initialized with', safePostCounts.length, 'data points');
}

function initializeTickersChart() {
    const ctx = document.getElementById('tickersChart');
    if (!ctx) {
        console.warn('Tickers chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (tickersChartInstance) {
        tickersChartInstance.destroy();
    }
    
    // Use real data if available
    const tickersData = dataCache.tickers || {
        '$GME': 156, '$AAPL': 87, '$TSLA': 64, '$NVDA': 52, '$MSFT': 41, '$AMD': 38
    };
    
    const topTickers = Object.entries(tickersData)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 6);
    
    // Ensure we always have data
    const labels = topTickers.length > 0 ? topTickers.map(([ticker]) => ticker) : ['$SPY', '$QQQ', '$AAPL'];
    const data = topTickers.length > 0 ? topTickers.map(([, count]) => count) : [100, 75, 50];
    const colors = [
        '#58a6ff', '#3fb950', '#d29922', '#f85149', '#a5a5a5', '#7c3aed'
    ];
    
    tickersChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#21262d',
                hoverBorderWidth: 3,
                hoverBorderColor: '#f0f6fc'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f0f6fc',
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(13, 17, 23, 0.9)',
                    titleColor: '#f0f6fc',
                    bodyColor: '#8b949e',
                    borderColor: '#30363d',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} mentions (${percentage}%)`;
                        }
                    }
                }
            },
            // Prevent animation flickering
            animation: {
                duration: 500,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    console.log('💹 Tickers chart initialized with', labels.length, 'tickers');
}

function generateSampleHistory() {
    const history = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
        const hour = timestamp.getHours();
        
        // Generate realistic activity pattern
        let baseActivity = 15;
        if (hour >= 9 && hour <= 16) baseActivity = 60; // Trading hours
        if (hour >= 18 && hour <= 23) baseActivity = 35; // Evening activity
        
        history.push({
            timestamp: timestamp.toISOString(),
            total_posts: baseActivity + Math.floor(Math.random() * 30),
            total_tickers: Math.floor(Math.random() * 10) + 15,
            top_ticker: ['$GME', '$AAPL', '$TSLA', '$NVDA'][Math.floor(Math.random() * 4)],
            sentiment: ['Bullish', 'Neutral', 'Bearish'][Math.floor(Math.random() * 3)]
        });
    }
    
    return history;
}

function generateExtendedSampleHistory() {
    const history = [];
    const now = new Date();
    
    // Generate 48 hours of data for more stability
    for (let i = 47; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
        const hour = timestamp.getHours();
        const dayOfWeek = timestamp.getDay(); // 0 = Sunday, 6 = Saturday
        
        // Generate realistic activity pattern with weekend adjustments
        let baseActivity = 15;
        
        // Weekday patterns
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {
            if (hour >= 9 && hour <= 16) baseActivity = 80; // Trading hours
            if (hour >= 6 && hour <= 9) baseActivity = 40;  // Pre-market
            if (hour >= 16 && hour <= 20) baseActivity = 60; // After-market
            if (hour >= 20 && hour <= 23) baseActivity = 35; // Evening
            if (hour >= 0 && hour <= 6) baseActivity = 8;    // Late night
        } else {
            // Weekend patterns - lower overall activity
            baseActivity = Math.floor(baseActivity * 0.6);
            if (hour >= 10 && hour <= 18) baseActivity = 25; // Weekend day activity
        }
        
        // Add some random variation
        const randomVariation = Math.floor(Math.random() * 20) - 10;
        const finalActivity = Math.max(baseActivity + randomVariation, 3);
        
        history.push({
            timestamp: timestamp.toISOString(),
            total_posts: finalActivity,
            total_tickers: Math.floor(Math.random() * 8) + 12,
            top_ticker: ['$SPY', '$QQQ', '$AAPL', '$TSLA', '$NVDA', '$GME'][Math.floor(Math.random() * 6)],
            sentiment: ['Bullish', 'Neutral', 'Bearish'][Math.floor(Math.random() * 3)]
        });
    }
    
    return history;
}

// Export for global access
window.initializeGitHubData = initializeGitHubData;
window.checkForDataUpdates = checkForDataUpdates;
window.startMonitoring = startMonitoring;
window.stopMonitoring = stopMonitoring;
window.refreshData = refreshData;
window.initializeEnhancedCharts = initializeEnhancedCharts;