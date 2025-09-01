// Reddit Data Engine - Dashboard JavaScript

// Global variables
let currentData = {
    posts: [],
    tickers: {},
    stats: {},
    analysis: {},
    history: []
};

// Tab Management
function showTab(tabName) {
    // Hide all tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab panel
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load specific tab content
    switch(tabName) {
        case 'tickers':
            loadTickersTable();
            break;
        case 'insights':
            loadInsights();
            break;
    }
}

// Data Loading Functions
async function loadData() {
    try {
        console.log('📊 Loading dashboard data...');
        
        // Load all data files
        const [postsData, tickersData, statsData, analysisData, historyData] = await Promise.all([
            fetch('data/posts.json').then(r => r.json()),
            fetch('data/tickers.json').then(r => r.json()),
            fetch('data/stats.json').then(r => r.json()),
            fetch('data/analysis.json').then(r => r.json()),
            fetch('data/history.json').then(r => r.json())
        ]);
        
        currentData = {
            posts: postsData,
            tickers: tickersData,
            stats: statsData,
            analysis: analysisData,
            history: historyData
        };
        
        console.log('✅ Data loaded successfully');
        
        // Update dashboard
        updateStatsCards();
        loadLiveFeed();
        updateTimestamp();
        
    } catch (error) {
        console.error('❌ Failed to load data:', error);
        // Show fallback content
        document.getElementById('connectionStatus').textContent = '❌ Data Load Failed';
    }
}

// Update Stats Cards
function updateStatsCards() {
    if (!currentData.stats) return;
    
    document.getElementById('totalPosts').textContent = currentData.stats.metadata?.total_posts || '0';
    document.getElementById('activeSubreddits').textContent = currentData.stats.metadata?.subreddits_monitored || '0';
    document.getElementById('trendingTickers').textContent = currentData.stats.metadata?.total_tickers || '0';
    document.getElementById('marketSentiment').textContent = currentData.analysis?.overall_sentiment || 'Neutral';
    
    // Update about section
    document.getElementById('aboutTotalPosts').textContent = currentData.stats.metadata?.total_posts || '0';
}

// Load Live Feed
function loadLiveFeed() {
    const container = document.getElementById('postsContainer');
    container.innerHTML = '';
    
    if (!currentData.posts || currentData.posts.length === 0) {
        container.innerHTML = '<p>No posts available</p>';
        return;
    }
    
    // Take first 20 posts for display
    const postsToShow = currentData.posts.slice(0, 20);
    
    postsToShow.forEach(post => {
        const postCard = createPostCard(post);
        container.appendChild(postCard);
    });
}

// Create Post Card
function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    const timeAgo = getTimeAgo(new Date(post.timestamp));
    
    card.innerHTML = `
        <div class="post-header">
            <span class="post-subreddit">r/${post.subreddit}</span>
            <span class="post-time">${timeAgo}</span>
        </div>
        <div class="post-title">
            <a href="${post.url}" target="_blank" class="post-link">${post.title}</a>
        </div>
        <div class="post-stats">
            <span>📈 ${post.score}</span>
            <span>💬 ${post.comments}</span>
            <span>👤 ${post.author}</span>
        </div>
    `;
    
    return card;
}

// Get Time Ago
function getTimeAgo(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

// Load Tickers Table
function loadTickersTable() {
    const tbody = document.getElementById('tickersTableBody');
    tbody.innerHTML = '';
    
    if (!currentData.tickers) return;
    
    // Convert tickers object to array and sort by count
    const tickersArray = Object.entries(currentData.tickers)
        .map(([symbol, count]) => ({ symbol, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 20);
    
    tickersArray.forEach(ticker => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="ticker-symbol">${ticker.symbol}</span></td>
            <td>${ticker.count}</td>
            <td><span class="sentiment-neutral">Neutral</span></td>
            <td>Multiple</td>
            <td>📈</td>
        `;
        tbody.appendChild(row);
    });
}

// Load Insights
function loadInsights() {
    const container = document.getElementById('insightsContent');
    
    if (currentData.analysis && currentData.analysis.insights) {
        const insights = currentData.analysis.insights.join('\n\n');
        container.textContent = insights;
    } else {
        container.textContent = 'Insights data not available. Please check back later.';
    }
}

// Update Timestamp
function updateTimestamp() {
    const timestamp = currentData.stats?.metadata?.last_updated || 
                     currentData.analysis?.analysis_timestamp ||
                     new Date().toISOString();
    
    const date = new Date(timestamp);
    const timeString = date.toLocaleString();
    
    document.getElementById('dataTimestamp').textContent = timeString;
    document.getElementById('lastUpdate').textContent = `Last update: ${timeString}`;
}

// Filter Posts by Subreddit
function filterPosts() {
    const filter = document.getElementById('subredditFilter').value;
    loadLiveFeed(filter);
}

// Refresh Data
function refreshData() {
    document.getElementById('connectionStatus').textContent = '🔄 Refreshing...';
    loadData();
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Reddit Data Engine Dashboard...');
    
    // Load initial data
    loadData();
    
    // Setup subreddit filter
    const subredditFilter = document.getElementById('subredditFilter');
    if (subredditFilter) {
        subredditFilter.addEventListener('change', filterPosts);
    }
    
    // Initialize charts after a delay
    setTimeout(() => {
        if (typeof initializeEnhancedCharts === 'function') {
            initializeEnhancedCharts();
        }
    }, 1000);
    
    console.log('✅ Dashboard initialized');
});