"""
Web-based GUI for Reddit Data Engine using Flask
Real-time dashboard with WebSocket updates
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import asyncio
import threading
import time
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_interface import AnalysisAPI, SimpleAPI
from config import MonitoringConfig


class WebGUIServer:
    """Flask web server for Reddit Data Engine GUI"""
    
    def __init__(self, host='localhost', port=5000):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.config['SECRET_KEY'] = 'reddit_data_engine_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.host = host
        self.port = port
        
        # API interfaces
        self.api = AnalysisAPI()
        self.simple_api = SimpleAPI()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.current_data = {}
        
        self.setup_routes()
        self.setup_socketio_events()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html', 
                                 subreddits=MonitoringConfig.SUBREDDITS,
                                 categories=list(MonitoringConfig.SUBREDDITS.keys()))
        
        @self.app.route('/api/status')
        def get_status():
            """Get current monitoring status"""
            return jsonify({
                'monitoring': self.is_monitoring,
                'last_update': self.current_data.get('timestamp'),
                'data_available': bool(self.current_data)
            })
        
        @self.app.route('/api/data')
        def get_current_data():
            """Get current Reddit data"""
            return jsonify(self.current_data)
        
        @self.app.route('/api/start_monitoring', methods=['POST'])
        def start_monitoring():
            """Start monitoring endpoint"""
            if not self.is_monitoring:
                self.start_monitoring_thread()
                return jsonify({'status': 'started', 'message': 'Monitoring started'})
            return jsonify({'status': 'already_running', 'message': 'Monitoring already active'})
        
        @self.app.route('/api/stop_monitoring', methods=['POST'])
        def stop_monitoring():
            """Stop monitoring endpoint"""
            if self.is_monitoring:
                self.stop_monitoring_thread()
                return jsonify({'status': 'stopped', 'message': 'Monitoring stopped'})
            return jsonify({'status': 'not_running', 'message': 'Monitoring not active'})
        
        @self.app.route('/api/export')
        def export_data():
            """Export current data"""
            if not self.current_data:
                return jsonify({'error': 'No data available'}), 404
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reddit_data_export_{timestamp}.json'
            
            return jsonify({
                'filename': filename,
                'data': self.current_data,
                'timestamp': timestamp
            })
    
    def setup_socketio_events(self):
        """Setup WebSocket events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {request.sid}")
            # Send current data to newly connected client
            if self.current_data:
                emit('data_update', self.current_data)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_refresh')
        def handle_refresh_request():
            """Handle manual refresh request"""
            if not self.is_monitoring:
                # Perform single refresh
                refresh_thread = threading.Thread(target=self.single_refresh, daemon=True)
                refresh_thread.start()
    
    def start_monitoring_thread(self):
        """Start the monitoring thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Notify all clients
            self.socketio.emit('monitoring_status', {'status': 'started'})
    
    def stop_monitoring_thread(self):
        """Stop the monitoring thread"""
        if self.is_monitoring:
            self.is_monitoring = False
            
            # Notify all clients
            self.socketio.emit('monitoring_status', {'status': 'stopped'})
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Fetch data asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.fetch_and_update_data())
                loop.close()
                
                # Wait before next update (default 30 seconds)
                time.sleep(30)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                self.socketio.emit('error', {'message': str(e)})
                time.sleep(60)  # Wait longer on error
    
    def single_refresh(self):
        """Perform single data refresh"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.fetch_and_update_data())
            loop.close()
            
            self.socketio.emit('refresh_complete', {'status': 'success'})
            
        except Exception as e:
            print(f"Refresh error: {e}")
            self.socketio.emit('error', {'message': f'Refresh failed: {str(e)}'})
    
    async def fetch_and_update_data(self):
        """Fetch data from Reddit API and update clients"""
        try:
            # Fetch all data concurrently
            data = {
                'timestamp': datetime.now().isoformat(),
                'trending_tickers': await self.api.get_trending_tickers(limit=20),
                'sentiment': await self.api.get_sentiment_overview(),
                'priority_posts': await self.api.get_priority_posts(limit=30),
                'subreddit_activity': await self.api.get_subreddit_activity(),
                'speculative_signals': await self.api.get_speculative_signals(),
                'market_mood': await self.simple_api.get_market_mood(),
                'yolo_activity': await self.simple_api.get_yolo_activity()
            }
            
            self.current_data = data
            
            # Emit data update to all connected clients
            self.socketio.emit('data_update', data)
            
        except Exception as e:
            raise Exception(f"Data fetch failed: {e}")
    
    def run(self, debug=False):
        """Run the Flask server"""
        print(f"🌐 Starting Reddit Data Engine Web GUI")
        print(f"📍 Server: http://{self.host}:{self.port}")
        print(f"🔄 WebSocket support enabled")
        
        self.socketio.run(self.app, host=self.host, port=self.port, debug=debug)


def create_templates():
    """Create HTML templates for the web GUI"""
    
    # Create templates directory
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Main dashboard template
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Data Engine - Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {
            border-left: 4px solid #007bff;
        }
        .alert-container {
            max-height: 200px;
            overflow-y: auto;
        }
        .ticker-badge {
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }
        .monitoring-indicator {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        .monitoring-active {
            background-color: #28a745;
            animation: pulse 2s infinite;
        }
        .monitoring-inactive {
            background-color: #dc3545;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .post-title {
            cursor: pointer;
        }
        .post-title:hover {
            text-decoration: underline;
        }
        .speculative-indicator {
            color: #ff6b6b;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                📊 Reddit Data Engine Dashboard
            </span>
            <div class="d-flex align-items-center">
                <span id="monitoring-status" class="text-white me-3">
                    <span id="status-indicator" class="monitoring-indicator monitoring-inactive"></span>
                    <span id="status-text">Stopped</span>
                </span>
                <button id="start-btn" class="btn btn-success me-2">Start</button>
                <button id="stop-btn" class="btn btn-danger me-2" disabled>Stop</button>
                <button id="refresh-btn" class="btn btn-outline-light me-2">Refresh</button>
                <button id="export-btn" class="btn btn-outline-light">Export</button>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        <!-- Status Alert -->
        <div id="status-alert" class="alert alert-info" role="alert" style="display: none;">
            <span id="status-message"></span>
        </div>

        <!-- Key Metrics Row -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Market Mood</h5>
                        <h3 id="market-mood" class="text-primary">--</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Total Posts</h5>
                        <h3 id="total-posts" class="text-info">--</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Speculative Posts</h5>
                        <h3 id="speculative-posts" class="text-warning">--</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card">
                    <div class="card-body">
                        <h5 class="card-title">Active Subreddits</h5>
                        <h3 id="active-subreddits" class="text-success">--</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content Tabs -->
        <ul class="nav nav-tabs" id="mainTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="tickers-tab" data-bs-toggle="tab" data-bs-target="#tickers" type="button" role="tab">
                    🔥 Trending Tickers
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="sentiment-tab" data-bs-toggle="tab" data-bs-target="#sentiment" type="button" role="tab">
                    💭 Sentiment
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="posts-tab" data-bs-toggle="tab" data-bs-target="#posts" type="button" role="tab">
                    ⚡ Priority Posts
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="subreddits-tab" data-bs-toggle="tab" data-bs-target="#subreddits" type="button" role="tab">
                    📈 Subreddit Activity
                </button>
            </li>
        </ul>

        <div class="tab-content" id="mainTabsContent">
            <!-- Trending Tickers Tab -->
            <div class="tab-pane fade show active" id="tickers" role="tabpanel">
                <div class="row mt-3">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5>Top Trending Tickers</h5>
                            </div>
                            <div class="card-body">
                                <div id="tickers-list" class="row">
                                    <!-- Tickers will be populated here -->
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6>YOLO Activity</h6>
                            </div>
                            <div class="card-body">
                                <p>Recent Posts: <span id="yolo-posts" class="fw-bold">--</span></p>
                                <p>Speculative Ratio: <span id="yolo-ratio" class="fw-bold">--</span>%</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sentiment Tab -->
            <div class="tab-pane fade" id="sentiment" role="tabpanel">
                <div class="row mt-3">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">
                                <h5>Market Sentiment Analysis</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-2 text-center">
                                        <h6>Overall Mood</h6>
                                        <h4 id="sentiment-mood" class="text-primary">--</h4>
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <h6>Average Score</h6>
                                        <h4 id="sentiment-average">--</h4>
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <h6>Positive</h6>
                                        <h4 id="sentiment-positive" class="text-success">--</h4>
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <h6>Negative</h6>
                                        <h4 id="sentiment-negative" class="text-danger">--</h4>
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <h6>Neutral</h6>
                                        <h4 id="sentiment-neutral" class="text-secondary">--</h4>
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <h6>Total Analyzed</h6>
                                        <h4 id="sentiment-total">--</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Priority Posts Tab -->
            <div class="tab-pane fade" id="posts" role="tabpanel">
                <div class="card mt-3">
                    <div class="card-header d-flex justify-content-between">
                        <h5>High-Priority Posts</h5>
                        <small class="text-muted">Click title to view post</small>
                    </div>
                    <div class="card-body">
                        <div id="posts-list">
                            <!-- Posts will be populated here -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- Subreddit Activity Tab -->
            <div class="tab-pane fade" id="subreddits" role="tabpanel">
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>Subreddit Activity Breakdown</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Subreddit</th>
                                        <th>Total Posts</th>
                                        <th>Avg Score</th>
                                        <th>Speculative %</th>
                                        <th>Recent Activity</th>
                                    </tr>
                                </thead>
                                <tbody id="subreddits-tbody">
                                    <!-- Subreddit data will be populated here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Last Updated -->
        <div class="row mt-3">
            <div class="col-12 text-center">
                <small class="text-muted">Last updated: <span id="last-updated">Never</span></small>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // WebSocket connection
        const socket = io();
        
        // UI Elements
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const refreshBtn = document.getElementById('refresh-btn');
        const exportBtn = document.getElementById('export-btn');
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const statusAlert = document.getElementById('status-alert');
        const statusMessage = document.getElementById('status-message');
        
        // Button event listeners
        startBtn.addEventListener('click', () => {
            fetch('/api/start_monitoring', {method: 'POST'})
                .then(response => response.json())
                .then(data => showStatus(data.message, 'success'));
        });
        
        stopBtn.addEventListener('click', () => {
            fetch('/api/stop_monitoring', {method: 'POST'})
                .then(response => response.json())
                .then(data => showStatus(data.message, 'info'));
        });
        
        refreshBtn.addEventListener('click', () => {
            socket.emit('request_refresh');
            showStatus('Refreshing data...', 'info');
        });
        
        exportBtn.addEventListener('click', () => {
            fetch('/api/export')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showStatus(data.error, 'danger');
                    } else {
                        downloadJSON(data.data, data.filename);
                        showStatus('Data exported successfully', 'success');
                    }
                });
        });
        
        // WebSocket event handlers
        socket.on('connect', () => {
            console.log('Connected to server');
            checkStatus();
        });
        
        socket.on('data_update', (data) => {
            updateUI(data);
        });
        
        socket.on('monitoring_status', (data) => {
            updateMonitoringStatus(data.status === 'started');
        });
        
        socket.on('error', (data) => {
            showStatus(data.message, 'danger');
        });
        
        socket.on('refresh_complete', (data) => {
            showStatus('Data refreshed', 'success');
        });
        
        // Helper functions
        function updateMonitoringStatus(isActive) {
            if (isActive) {
                statusIndicator.className = 'monitoring-indicator monitoring-active';
                statusText.textContent = 'Active';
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                statusIndicator.className = 'monitoring-indicator monitoring-inactive';
                statusText.textContent = 'Stopped';
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
        
        function showStatus(message, type) {
            statusMessage.textContent = message;
            statusAlert.className = `alert alert-${type}`;
            statusAlert.style.display = 'block';
            setTimeout(() => {
                statusAlert.style.display = 'none';
            }, 5000);
        }
        
        function updateUI(data) {
            // Update key metrics
            document.getElementById('market-mood').textContent = 
                (data.market_mood || 'Unknown').toUpperCase();
            document.getElementById('total-posts').textContent = 
                data.sentiment?.total || '--';
            document.getElementById('speculative-posts').textContent = 
                data.speculative_signals?.total_speculative_posts || '--';
            document.getElementById('active-subreddits').textContent = 
                Object.keys(data.subreddit_activity || {}).length || '--';
            
            // Update tickers
            updateTickers(data.trending_tickers || []);
            
            // Update sentiment
            updateSentiment(data.sentiment || {});
            
            // Update posts
            updatePosts(data.priority_posts || []);
            
            // Update subreddits
            updateSubreddits(data.subreddit_activity || {});
            
            // Update YOLO activity
            updateYoloActivity(data.yolo_activity || {});
            
            // Update last updated time
            document.getElementById('last-updated').textContent = 
                new Date(data.timestamp).toLocaleTimeString();
        }
        
        function updateTickers(tickers) {
            const tickersContainer = document.getElementById('tickers-list');
            tickersContainer.innerHTML = '';
            
            tickers.forEach((ticker, index) => {
                const tickerElement = document.createElement('div');
                tickerElement.className = 'col-md-3 mb-2';
                tickerElement.innerHTML = `
                    <div class="card border-primary">
                        <div class="card-body text-center">
                            <h6 class="ticker-badge text-primary">$${ticker.ticker}</h6>
                            <p class="mb-0">${ticker.mentions} mentions</p>
                            <small class="text-muted">#${ticker.rank}</small>
                        </div>
                    </div>
                `;
                tickersContainer.appendChild(tickerElement);
            });
        }
        
        function updateSentiment(sentiment) {
            document.getElementById('sentiment-mood').textContent = 
                (sentiment.mood || 'Unknown').toUpperCase();
            document.getElementById('sentiment-average').textContent = 
                sentiment.average?.toFixed(3) || '--';
            document.getElementById('sentiment-positive').textContent = 
                sentiment.positive || '--';
            document.getElementById('sentiment-negative').textContent = 
                sentiment.negative || '--';
            document.getElementById('sentiment-neutral').textContent = 
                sentiment.neutral || '--';
            document.getElementById('sentiment-total').textContent = 
                sentiment.total || '--';
        }
        
        function updatePosts(posts) {
            const postsContainer = document.getElementById('posts-list');
            postsContainer.innerHTML = '';
            
            posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'mb-3 p-3 border rounded';
                postElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="post-title text-primary" onclick="openPost('${post.url}')">
                                ${post.title}
                            </h6>
                            <small class="text-muted">
                                r/${post.subreddit} • ${post.score} points • ${post.comments} comments
                                ${post.is_speculative ? '<span class="speculative-indicator">🔥 SPECULATIVE</span>' : ''}
                            </small>
                        </div>
                    </div>
                `;
                postsContainer.appendChild(postElement);
            });
        }
        
        function updateSubreddits(subredditData) {
            const tbody = document.getElementById('subreddits-tbody');
            tbody.innerHTML = '';
            
            Object.entries(subredditData).forEach(([subreddit, data]) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>r/${subreddit}</td>
                    <td>${data.total_posts || 0}</td>
                    <td>${(data.avg_score || 0).toFixed(1)}</td>
                    <td>${((data.speculative_ratio || 0) * 100).toFixed(1)}%</td>
                    <td>${data.recent_activity || 0}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function updateYoloActivity(yoloData) {
            document.getElementById('yolo-posts').textContent = 
                yoloData.recent_posts || '--';
            document.getElementById('yolo-ratio').textContent = 
                yoloData.speculative_ratio || '--';
        }
        
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    updateMonitoringStatus(data.monitoring);
                    if (data.data_available) {
                        fetch('/api/data')
                            .then(response => response.json())
                            .then(updateUI);
                    }
                });
        }
        
        function openPost(url) {
            if (url) {
                window.open(url, '_blank');
            }
        }
        
        function downloadJSON(data, filename) {
            const jsonStr = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonStr], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        // Initialize
        checkStatus();
    </script>
</body>
</html>"""
    
    # Write dashboard template
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    
    print("✅ HTML templates created successfully")


def main():
    """Main entry point for web GUI"""
    # Create templates
    create_templates()
    
    # Start server
    server = WebGUIServer(host='localhost', port=5000)
    server.run(debug=False)


if __name__ == "__main__":
    main()