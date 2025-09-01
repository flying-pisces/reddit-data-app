// Reddit Data Engine - GitHub Pages Demo JavaScript

// Sample data for demonstration
const samplePosts = [
    {
        id: '1n5jjnl',
        time: '2 minutes ago',
        subreddit: 'wallstreetbets',
        title: '$AAPL earnings beat expectations - calls printing! 🚀',
        score: 1247,
        comments: 312,
        author: 'DiamondHands420',
        url: 'https://reddit.com/r/wallstreetbets/comments/1n5jjnl/aapl_earnings_beat/'
    },
    {
        id: '1n5k8pm',
        time: '5 minutes ago',
        subreddit: 'stocks',
        title: 'Tesla $TSLA production numbers exceed Q4 guidance by 12%',
        score: 890,
        comments: 156,
        author: 'ElonFanboy',
        url: 'https://reddit.com/r/stocks/comments/1n5k8pm/tesla_production/'
    },
    {
        id: '1n5l2nd',
        time: '8 minutes ago',
        subreddit: 'investing',
        title: 'Microsoft $MSFT announces major AI partnership - thoughts?',
        score: 654,
        comments: 89,
        author: 'TechInvestor',
        url: 'https://reddit.com/r/investing/comments/1n5l2nd/msft_ai_partnership/'
    },
    {
        id: '1n5m5kj',
        time: '12 minutes ago',
        subreddit: 'wallstreetbets',
        title: 'YOLO $50k on $NVDA calls - nvidia to the moon! 🌙',
        score: 2103,
        comments: 445,
        author: 'YOLOWarrior',
        url: 'https://reddit.com/r/wallstreetbets/comments/1n5m5kj/nvda_yolo/'
    },
    {
        id: '1n5n8bw',
        time: '15 minutes ago',
        subreddit: 'stocks',
        title: 'Amazon $AMZN cloud revenue up 25% - bullish for tech sector',
        score: 567,
        comments: 78,
        author: 'CloudBull',
        url: 'https://reddit.com/r/stocks/comments/1n5n8bw/amzn_cloud_revenue/'
    },
    {
        id: '1n5o1ps',
        time: '18 minutes ago',
        subreddit: 'pennystocks',
        title: '$GME short interest still high - squeeze potential?',
        score: 1892,
        comments: 623,
        author: 'ApeStrong',
        url: 'https://reddit.com/r/pennystocks/comments/1n5o1ps/gme_squeeze/'
    }
];

const sampleTickers = [
    { symbol: '$AAPL', count: 156, sentiment: 0.8, subreddits: ['wallstreetbets', 'stocks'], trend: '+23%' },
    { symbol: '$TSLA', count: 134, sentiment: 0.6, subreddits: ['wallstreetbets', 'stocks', 'investing'], trend: '+18%' },
    { symbol: '$NVDA', count: 89, sentiment: 0.9, subreddits: ['wallstreetbets', 'investing'], trend: '+45%' },
    { symbol: '$MSFT', count: 67, sentiment: 0.7, subreddits: ['stocks', 'investing'], trend: '+12%' },
    { symbol: '$AMZN', count: 45, sentiment: 0.5, subreddits: ['stocks', 'investing'], trend: '+8%' },
    { symbol: '$GME', count: 234, sentiment: 0.3, subreddits: ['wallstreetbets', 'pennystocks'], trend: '+67%' },
    { symbol: '$AMD', count: 34, sentiment: 0.6, subreddits: ['stocks'], trend: '+15%' },
    { symbol: '$GOOGL', count: 28, sentiment: 0.4, subreddits: ['investing'], trend: '+5%' }
];

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeDemo();
    loadSamplePosts();
    loadSampleTickers();
    initializeCharts();
    updateLastUpdate();
    
    // Simulate real-time updates
    setInterval(simulateRealtimeUpdate, 30000); // Every 30 seconds
    setInterval(updateLastUpdate, 1000); // Every second
});

function initializeDemo() {
    console.log('🚀 Reddit Data Engine Demo Initialized');
    
    // Add click handlers for demo interactions
    const demoNotice = document.querySelector('.demo-notice');
    if (demoNotice) {
        demoNotice.addEventListener('click', function() {
            alert('📥 Download the full version from GitHub to connect to Reddit\'s live API!\n\nThis demo shows sample data to demonstrate the interface.');
        });
    }
}

function showTab(tabName) {
    // Hide all tab panels
    const panels = document.querySelectorAll('.tab-panel');
    panels.forEach(panel => panel.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));
    
    // Show selected panel and activate button
    const targetPanel = document.getElementById(tabName + '-tab');
    const targetButton = document.querySelector(`[onclick="showTab('${tabName}')"]`);
    
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    
    if (targetButton) {
        targetButton.classList.add('active');
    }
}

function loadSamplePosts() {
    const container = document.getElementById('postsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    samplePosts.forEach(post => {
        const postElement = createPostCard(post);
        container.appendChild(postElement);
    });
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    const redditUrl = post.url || `https://reddit.com/r/${post.subreddit}`;
    
    card.innerHTML = `
        <div class="post-header">
            <span class="post-subreddit">r/${post.subreddit}</span>
            <span class="post-time">${post.time}</span>
        </div>
        <div class="post-title">
            <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="post-link">
                ${post.title}
            </a>
        </div>
        <div class="post-stats">
            <span>⬆ ${post.score}</span>
            <span>💬 ${post.comments}</span>
            <span>👤 ${post.author}</span>
            <span>🔗 <a href="${redditUrl}" target="_blank" rel="noopener noreferrer" class="reddit-link">View on Reddit</a></span>
        </div>
    `;
    
    return card;
}

function loadSampleTickers() {
    const tbody = document.getElementById('tickersTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    sampleTickers.forEach(ticker => {
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
            <td>${ticker.subreddits.join(', ')}</td>
            <td class="sentiment-positive">${ticker.trend}</td>
        `;
        tbody.appendChild(row);
    });
}

function getSentimentClass(sentiment) {
    if (sentiment > 0.6) return 'sentiment-positive';
    if (sentiment < 0.4) return 'sentiment-negative';
    return 'sentiment-neutral';
}

function getSentimentText(sentiment) {
    if (sentiment > 0.6) return 'Bullish';
    if (sentiment < 0.4) return 'Bearish';
    return 'Neutral';
}

function initializeCharts() {
    initializeActivityChart();
    initializeTickersChart();
}

function initializeActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;
    
    // Generate sample hourly data
    const hours = [];
    const posts = [];
    const currentHour = new Date().getHours();
    
    for (let i = 11; i >= 0; i--) {
        const hour = (currentHour - i + 24) % 24;
        hours.push(`${hour}:00`);
        posts.push(Math.floor(Math.random() * 200) + 50);
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Posts per Hour',
                data: posts,
                borderColor: '#58a6ff',
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#f0f6fc'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#8b949e'
                    },
                    grid: {
                        color: '#30363d'
                    }
                },
                x: {
                    ticks: {
                        color: '#8b949e'
                    },
                    grid: {
                        color: '#30363d'
                    }
                }
            }
        }
    });
}

function initializeTickersChart() {
    const ctx = document.getElementById('tickersChart');
    if (!ctx) return;
    
    const topTickers = sampleTickers.slice(0, 6);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: topTickers.map(t => t.symbol),
            datasets: [{
                data: topTickers.map(t => t.count),
                backgroundColor: [
                    '#58a6ff',
                    '#3fb950',
                    '#d29922',
                    '#f85149',
                    '#a5a5a5',
                    '#7c3aed'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f0f6fc',
                        usePointStyle: true,
                        padding: 10
                    }
                }
            }
        }
    });
}

function simulateRealtimeUpdate() {
    // Simulate new post arrival
    const newPost = {
        id: 'new' + Date.now(),
        time: 'Just now',
        subreddit: ['wallstreetbets', 'stocks', 'investing'][Math.floor(Math.random() * 3)],
        title: [
            '$SPY looking strong today - bullish momentum continues',
            'Breaking: Major tech stock beats earnings expectations',
            'Market volatility creates buying opportunities',
            '$AAPL technical analysis shows breakout pattern',
            'Fed announcement impacts market sentiment'
        ][Math.floor(Math.random() * 5)],
        score: Math.floor(Math.random() * 500) + 100,
        comments: Math.floor(Math.random() * 100) + 20,
        author: 'DemoUser' + Math.floor(Math.random() * 100),
        url: 'https://reddit.com/r/demo/comments/demo/demo_post/'
    };
    
    // Add to beginning of posts array
    samplePosts.unshift(newPost);
    
    // Keep only last 10 posts
    if (samplePosts.length > 10) {
        samplePosts.pop();
    }
    
    // Update display
    loadSamplePosts();
    
    // Update stats
    updateStats();
}

function updateStats() {
    const totalPosts = document.getElementById('totalPosts');
    const activeSubreddits = document.getElementById('activeSubreddits');
    const trendingTickers = document.getElementById('trendingTickers');
    
    if (totalPosts) {
        const currentValue = parseInt(totalPosts.textContent);
        totalPosts.textContent = currentValue + Math.floor(Math.random() * 10) + 1;
    }
    
    if (activeSubreddits) {
        activeSubreddits.textContent = '6';
    }
    
    if (trendingTickers) {
        trendingTickers.textContent = sampleTickers.length;
    }
}

function updateLastUpdate() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) {
        const now = new Date();
        lastUpdateEl.textContent = `Last update: ${now.toLocaleTimeString()}`;
    }
}

// Add some interactive demo features
function generateInsights() {
    const insightsContent = document.getElementById('insightsContent');
    if (!insightsContent) return;
    
    const insights = [
        "📊 Real-time analysis shows increased bullish sentiment across tech stocks",
        "⚠️ High volume discussions detected around $GME - potential volatility ahead",
        "📈 $AAPL mentions surge 45% following earnings beat",
        "🎯 r/wallstreetbets showing 78% positive sentiment - historically bullish indicator",
        "💡 Cross-subreddit analysis suggests rotation from growth to value stocks"
    ];
    
    insightsContent.innerHTML = `
        <h4>🔄 Generating AI Insights...</h4>
        <div class="loading"></div>
    `;
    
    setTimeout(() => {
        const randomInsights = insights.sort(() => 0.5 - Math.random()).slice(0, 3);
        insightsContent.innerHTML = `
            <h4>📈 Current Market Analysis</h4>
            ${randomInsights.map(insight => `<p>• ${insight}</p>`).join('')}
            <p><em>Note: This is a demo with sample insights. The full version provides real AI-powered analysis.</em></p>
        `;
    }, 2000);
}

function exportData() {
    const exportLog = document.getElementById('exportLog');
    if (!exportLog) return;
    
    exportLog.innerHTML = 'Exporting demo data...';
    
    setTimeout(() => {
        exportLog.innerHTML = `
✅ Demo export complete!

📊 Sample Data Exported:
• Posts: ${samplePosts.length} items
• Tickers: ${sampleTickers.length} items  
• File: demo_export_${new Date().toISOString().slice(0,10)}.json

Note: This is a demonstration. The full version exports real monitoring data to JSON format for analysis.
        `;
    }, 1500);
}

function saveSettings() {
    alert('⚙️ Settings saved!\n\nNote: This is a demo interface. Download the full version to customize real monitoring settings.');
}

// Add smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href') && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Add some visual feedback for demo interactions
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('post-card') || e.target.closest('.post-card')) {
        const card = e.target.closest('.post-card') || e.target;
        card.style.transform = 'translateX(10px)';
        setTimeout(() => {
            card.style.transform = '';
        }, 200);
    }
});

// Expose functions globally for onclick handlers
window.showTab = showTab;
window.generateInsights = generateInsights;
window.exportData = exportData;
window.saveSettings = saveSettings;