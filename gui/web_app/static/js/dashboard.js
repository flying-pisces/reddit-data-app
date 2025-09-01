// Reddit Data Engine - Dashboard JavaScript

let monitoring = false;
let updateInterval = null;
let activityChart = null;
let tickersChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    updateStatus();
    setInterval(updateTime, 1000);
    
    // Setup slider listeners
    document.getElementById('refreshInterval').addEventListener('input', function(e) {
        document.getElementById('refreshValue').textContent = e.target.value;
    });
    
    document.getElementById('maxPosts').addEventListener('input', function(e) {
        document.getElementById('maxPostsValue').textContent = e.target.value;
    });
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Refresh data for specific tabs
    if (tabName === 'tickers') {
        updateTickers();
    } else if (tabName === 'insights') {
        // Insights loaded on demand
    }
}

// Monitoring Controls
async function startMonitoring() {
    try {
        const response = await fetch('/api/start_monitoring', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            monitoring = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('connectionStatus').innerHTML = '🟢 Connected';
            document.getElementById('connectionStatus').style.color = '#4caf50';
            
            // Start auto-refresh
            updateInterval = setInterval(refreshData, 5000);
            refreshData();
            
            showNotification('Monitoring started successfully!', 'success');
        }
    } catch (error) {
        console.error('Error starting monitoring:', error);
        showNotification('Failed to start monitoring', 'error');
    }
}

async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop_monitoring', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            monitoring = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('connectionStatus').innerHTML = '⚫ Disconnected';
            document.getElementById('connectionStatus').style.color = '#ff9800';
            
            // Stop auto-refresh
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
            
            showNotification('Monitoring stopped', 'info');
        }
    } catch (error) {
        console.error('Error stopping monitoring:', error);
        showNotification('Failed to stop monitoring', 'error');
    }
}

// Data Refresh
async function refreshData() {
    await Promise.all([
        updateStatus(),
        updatePosts(),
        updateCharts()
    ]);
}

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update stats cards
        document.getElementById('totalPosts').textContent = data.stats.total_posts || '0';
        document.getElementById('activeSubreddits').textContent = data.stats.active_subreddits || '0';
        document.getElementById('trendingTickers').textContent = data.stats.trending_tickers || '0';
        document.getElementById('marketSentiment').textContent = data.stats.sentiment || 'Neutral';
        
        // Update last update time
        if (data.last_update) {
            const time = new Date(data.last_update).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = `Last update: ${time}`;
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

async function updatePosts() {
    try {
        const response = await fetch('/api/posts?limit=50');
        const data = await response.json();
        
        const container = document.getElementById('postsContainer');
        container.innerHTML = '';
        
        // Filter by selected subreddit
        const filter = document.getElementById('subredditFilter').value;
        let posts = data.posts;
        
        if (filter !== 'all') {
            posts = posts.filter(post => post.subreddit === filter);
        }
        
        // Display posts
        posts.forEach(post => {
            const postCard = createPostCard(post);
            container.appendChild(postCard);
        });
        
        if (posts.length === 0) {
            container.innerHTML = '<div class="no-data">No posts available</div>';
        }
    } catch (error) {
        console.error('Error updating posts:', error);
    }
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    
    const time = new Date(post.time).toLocaleTimeString();
    const redditUrl = post.url || `https://reddit.com/r/${post.subreddit}`;
    
    card.innerHTML = `
        <div class="post-header">
            <span class="post-subreddit">r/${post.subreddit}</span>
            <span class="post-time">${time}</span>
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

async function updateTickers() {
    try {
        const response = await fetch('/api/tickers');
        const data = await response.json();
        
        const tbody = document.getElementById('tickersTableBody');
        tbody.innerHTML = '';
        
        data.tickers.forEach(ticker => {
            const row = document.createElement('tr');
            
            const sentimentClass = ticker.sentiment > 0 ? 'sentiment-positive' : 
                                  ticker.sentiment < 0 ? 'sentiment-negative' : 
                                  'sentiment-neutral';
            
            const sentimentText = ticker.sentiment > 0 ? 'Bullish' :
                                 ticker.sentiment < 0 ? 'Bearish' :
                                 'Neutral';
            
            const tickerSearchUrl = `https://www.reddit.com/search/?q=${ticker.symbol}&type=link&sort=new`;
            
            row.innerHTML = `
                <td class="ticker-symbol">
                    <a href="${tickerSearchUrl}" target="_blank" rel="noopener noreferrer" class="ticker-link">
                        ${ticker.symbol}
                    </a>
                </td>
                <td>${ticker.count}</td>
                <td class="${sentimentClass}">${sentimentText}</td>
                <td>${ticker.subreddits.join(', ')}</td>
                <td>↑</td>
            `;
            
            tbody.appendChild(row);
        });
        
        if (data.tickers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No tickers found</td></tr>';
        }
    } catch (error) {
        console.error('Error updating tickers:', error);
    }
}

// Charts
function initializeCharts() {
    // Activity Chart
    const activityCtx = document.getElementById('activityChart').getContext('2d');
    activityChart = new Chart(activityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Posts per Minute',
                data: [],
                borderColor: '#007acc',
                backgroundColor: 'rgba(0, 122, 204, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#3e3e42'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                },
                x: {
                    grid: {
                        color: '#3e3e42'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                }
            }
        }
    });
    
    // Tickers Chart
    const tickersCtx = document.getElementById('tickersChart').getContext('2d');
    tickersChart = new Chart(tickersCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Mentions',
                data: [],
                backgroundColor: '#4caf50'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#3e3e42'
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#cccccc'
                    }
                }
            }
        }
    });
}

async function updateCharts() {
    // Update activity chart with random data for demo
    const now = new Date().toLocaleTimeString();
    
    if (activityChart.data.labels.length > 10) {
        activityChart.data.labels.shift();
        activityChart.data.datasets[0].data.shift();
    }
    
    activityChart.data.labels.push(now);
    activityChart.data.datasets[0].data.push(Math.floor(Math.random() * 10) + 1);
    activityChart.update();
    
    // Update tickers chart
    try {
        const response = await fetch('/api/tickers');
        const data = await response.json();
        
        const topTickers = data.tickers.slice(0, 5);
        
        tickersChart.data.labels = topTickers.map(t => t.symbol);
        tickersChart.data.datasets[0].data = topTickers.map(t => t.count);
        tickersChart.update();
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

// Insights
async function generateInsights() {
    const content = document.getElementById('insightsContent');
    content.innerHTML = '<div class="loading"></div> Generating insights...';
    
    try {
        const response = await fetch('/api/insights');
        const data = await response.json();
        
        let insightsText = `Market Insights - ${new Date(data.timestamp).toLocaleString()}\n`;
        insightsText += '═'.repeat(60) + '\n\n';
        
        insightsText += '📊 SUMMARY\n';
        insightsText += `Total posts analyzed: ${data.summary.total_posts}\n`;
        insightsText += `Unique tickers found: ${data.summary.unique_tickers}\n`;
        
        if (data.summary.top_ticker) {
            insightsText += `Top ticker: ${data.summary.top_ticker.symbol} (${data.summary.top_ticker.mentions} mentions)\n`;
        }
        
        insightsText += `Market sentiment: ${data.summary.market_sentiment}\n\n`;
        
        if (data.recommendations && data.recommendations.length > 0) {
            insightsText += '📈 RECOMMENDATIONS\n';
            data.recommendations.forEach(rec => {
                insightsText += `• ${rec}\n`;
            });
        }
        
        content.textContent = insightsText;
        
    } catch (error) {
        console.error('Error generating insights:', error);
        content.innerHTML = 'Failed to generate insights. Please try again.';
    }
}

// Export
async function exportData() {
    const subreddits = document.getElementById('exportSubreddits').value.split(',').map(s => s.trim());
    const hours = parseInt(document.getElementById('exportHours').value);
    
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subreddits: subreddits,
                hours: hours
            })
        });
        
        const data = await response.json();
        
        const log = document.getElementById('exportLog');
        const timestamp = new Date().toLocaleTimeString();
        
        if (data.status === 'success') {
            log.innerHTML += `[${timestamp}] Export successful: ${data.filename}<br>`;
            log.innerHTML += `  - Posts exported: ${data.posts_exported}<br>`;
            log.innerHTML += `  - Tickers exported: ${data.tickers_exported}<br><br>`;
            
            showNotification('Data exported successfully!', 'success');
        } else {
            log.innerHTML += `[${timestamp}] Export failed: ${data.message}<br><br>`;
            showNotification('Export failed', 'error');
        }
        
        log.scrollTop = log.scrollHeight;
        
    } catch (error) {
        console.error('Error exporting data:', error);
        showNotification('Export failed', 'error');
    }
}

// Settings
async function saveSettings() {
    const settings = {
        refresh_interval: parseInt(document.getElementById('refreshInterval').value),
        max_posts: parseInt(document.getElementById('maxPosts').value),
        subreddits: document.getElementById('monitoredSubreddits').value.split('\n').filter(s => s.trim())
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Settings saved successfully!', 'success');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Failed to save settings', 'error');
    }
}

// Utility Functions
function updateTime() {
    // Update time in footer if needed
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#4caf50',
        error: '#f44336',
        info: '#007acc',
        warning: '#ff9800'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .no-data {
        text-align: center;
        padding: 40px;
        color: #666;
        font-style: italic;
    }
`;
document.head.appendChild(style);