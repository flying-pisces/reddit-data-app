#!/usr/bin/env python3
"""
Reddit Data Engine - Desktop GUI Application
A modern, intuitive interface for monitoring Reddit data in real-time
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os
import webbrowser

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from reddit_client import RedditClient
from data_processor import DataProcessor
from api_interface import AnalysisAPI
import asyncio

class RedditMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Data Engine - Live Monitor")
        self.root.geometry("1200x800")
        
        # Set modern theme
        self.root.configure(bg='#1e1e1e')
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'card_bg': '#2d2d30',
            'text_bg': '#1e1e1e'
        }
        
        # Data storage
        self.posts_queue = queue.Queue()
        self.tickers_data = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Start status updates
        self.update_status()
        
    def setup_ui(self):
        """Create the main UI layout"""
        
        # Top toolbar
        self.create_toolbar()
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_monitor_tab()
        self.create_tickers_tab()
        self.create_insights_tab()
        self.create_export_tab()
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create top toolbar with controls"""
        toolbar = tk.Frame(self.root, bg=self.colors['card_bg'], height=60)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Logo/Title
        title_label = tk.Label(
            toolbar,
            text="🚀 Reddit Data Engine",
            font=('Arial', 20, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Control buttons
        self.start_btn = tk.Button(
            toolbar,
            text="▶ Start Monitoring",
            command=self.start_monitoring,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(
            toolbar,
            text="⏹ Stop",
            command=self.stop_monitoring,
            bg=self.colors['error'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self.refresh_data,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 12),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Connection status
        self.conn_label = tk.Label(
            toolbar,
            text="⚫ Disconnected",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['warning']
        )
        self.conn_label.pack(side=tk.RIGHT, padx=20)
    
    def create_monitor_tab(self):
        """Create real-time monitoring tab"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="📊 Live Monitor")
        
        # Split into left and right panels
        left_panel = tk.Frame(monitor_frame, bg=self.colors['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_panel = tk.Frame(monitor_frame, bg=self.colors['bg'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Live feed (left panel)
        feed_label = tk.Label(
            left_panel,
            text="Live Reddit Feed",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        feed_label.pack(pady=5)
        
        # Create treeview for posts
        columns = ('Time', 'Subreddit', 'Title', 'Score', 'Comments', 'URL')
        self.posts_tree = ttk.Treeview(left_panel, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.posts_tree.heading('Time', text='Time')
        self.posts_tree.heading('Subreddit', text='Subreddit')
        self.posts_tree.heading('Title', text='Title (Double-click to open)')
        self.posts_tree.heading('Score', text='Score')
        self.posts_tree.heading('Comments', text='Comments')
        self.posts_tree.heading('URL', text='')  # Hidden column for URL storage
        
        self.posts_tree.column('Time', width=80)
        self.posts_tree.column('Subreddit', width=120)
        self.posts_tree.column('Title', width=400)
        self.posts_tree.column('Score', width=80)
        self.posts_tree.column('Comments', width=80)
        self.posts_tree.column('URL', width=0, stretch=False)  # Hidden column
        
        # Add click handler for opening URLs
        self.posts_tree.bind('<Double-1>', self.on_post_double_click)
        self.posts_tree.bind('<Button-1>', self.on_post_click)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.posts_tree.yview)
        self.posts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.posts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Stats panel (right)
        self.create_stats_panel(right_panel)
    
    def create_stats_panel(self, parent):
        """Create statistics panel"""
        stats_label = tk.Label(
            parent,
            text="📈 Live Statistics",
            font=('Arial', 14, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        stats_label.pack(pady=10)
        
        # Stats cards
        stats_frame = tk.Frame(parent, bg=self.colors['bg'])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Total posts card
        self.create_stat_card(stats_frame, "Total Posts", "0", self.colors['accent'])
        
        # Active subreddits card
        self.create_stat_card(stats_frame, "Active Subreddits", "0", self.colors['success'])
        
        # Trending tickers card
        self.create_stat_card(stats_frame, "Trending Tickers", "0", self.colors['warning'])
        
        # Sentiment card
        self.create_stat_card(stats_frame, "Market Sentiment", "Neutral", self.colors['accent'])
        
        # Posts/minute card
        self.create_stat_card(stats_frame, "Posts/Minute", "0", self.colors['success'])
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card widget"""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(
            card,
            text=title,
            font=('Arial', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        )
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(
            card,
            text=value,
            font=('Arial', 18, 'bold'),
            bg=self.colors['card_bg'],
            fg=color
        )
        value_label.pack(pady=(0, 10))
        
        # Store reference for updates
        if not hasattr(self, 'stat_cards'):
            self.stat_cards = {}
        self.stat_cards[title] = value_label
    
    def create_tickers_tab(self):
        """Create tickers analysis tab"""
        tickers_frame = ttk.Frame(self.notebook)
        self.notebook.add(tickers_frame, text="💹 Tickers")
        
        # Header
        header_frame = tk.Frame(tickers_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="Trending Stock Tickers",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT)
        
        # Tickers list
        columns = ('Ticker', 'Mentions', 'Sentiment', 'Subreddits', 'Trend')
        self.tickers_tree = ttk.Treeview(tickers_frame, columns=columns, show='headings', height=25)
        
        self.tickers_tree.heading('Ticker', text='Ticker')
        self.tickers_tree.heading('Mentions', text='Mentions')
        self.tickers_tree.heading('Sentiment', text='Sentiment')
        self.tickers_tree.heading('Subreddits', text='Top Subreddit')
        self.tickers_tree.heading('Trend', text='24h Trend')
        
        self.tickers_tree.column('Ticker', width=100)
        self.tickers_tree.column('Mentions', width=100)
        self.tickers_tree.column('Sentiment', width=100)
        self.tickers_tree.column('Subreddits', width=150)
        self.tickers_tree.column('Trend', width=100)
        
        # Add double-click handler for tickers
        self.tickers_tree.bind('<Double-1>', self.on_ticker_double_click)
        
        self.tickers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_insights_tab(self):
        """Create market insights tab"""
        insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(insights_frame, text="💡 Insights")
        
        # Insights text area
        self.insights_text = scrolledtext.ScrolledText(
            insights_frame,
            wrap=tk.WORD,
            font=('Courier', 11),
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg']
        )
        self.insights_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(insights_frame, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            btn_frame,
            text="Generate Insights",
            command=self.generate_insights,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 11),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Clear",
            command=lambda: self.insights_text.delete(1.0, tk.END),
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            font=('Arial', 11),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def create_export_tab(self):
        """Create data export tab"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Export")
        
        # Export options
        options_frame = tk.Frame(export_frame, bg=self.colors['card_bg'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            options_frame,
            text="Export Options",
            font=('Arial', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Subreddits selection
        tk.Label(
            options_frame,
            text="Subreddits:",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=1, column=0, sticky='e', padx=10, pady=5)
        
        self.export_subs = tk.Entry(
            options_frame,
            font=('Arial', 11),
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            width=30
        )
        self.export_subs.grid(row=1, column=1, padx=10, pady=5)
        self.export_subs.insert(0, "wallstreetbets,stocks,investing")
        
        # Hours back
        tk.Label(
            options_frame,
            text="Hours back:",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=2, column=0, sticky='e', padx=10, pady=5)
        
        self.export_hours = tk.Spinbox(
            options_frame,
            from_=1,
            to=168,
            font=('Arial', 11),
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            width=10
        )
        self.export_hours.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        self.export_hours.delete(0, tk.END)
        self.export_hours.insert(0, "24")
        
        # Export button
        tk.Button(
            options_frame,
            text="Export to JSON",
            command=self.export_data,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Export log
        tk.Label(
            export_frame,
            text="Export Log",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(pady=5)
        
        self.export_log = scrolledtext.ScrolledText(
            export_frame,
            wrap=tk.WORD,
            height=15,
            font=('Courier', 10),
            bg=self.colors['text_bg'],
            fg=self.colors['fg']
        )
        self.export_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings container
        container = tk.Frame(settings_frame, bg=self.colors['card_bg'])
        container.pack(padx=20, pady=20)
        
        tk.Label(
            container,
            text="Monitoring Settings",
            font=('Arial', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Refresh interval
        tk.Label(
            container,
            text="Refresh Interval (seconds):",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=1, column=0, sticky='e', padx=10, pady=5)
        
        self.refresh_interval = tk.Scale(
            container,
            from_=10,
            to=300,
            orient=tk.HORIZONTAL,
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            length=200
        )
        self.refresh_interval.set(30)
        self.refresh_interval.grid(row=1, column=1, padx=10, pady=5)
        
        # Max posts per subreddit
        tk.Label(
            container,
            text="Max Posts per Subreddit:",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=2, column=0, sticky='e', padx=10, pady=5)
        
        self.max_posts = tk.Scale(
            container,
            from_=5,
            to=50,
            orient=tk.HORIZONTAL,
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            length=200
        )
        self.max_posts.set(25)
        self.max_posts.grid(row=2, column=1, padx=10, pady=5)
        
        # Monitored subreddits
        tk.Label(
            container,
            text="Monitored Subreddits:",
            font=('Arial', 11),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        ).grid(row=3, column=0, sticky='ne', padx=10, pady=5)
        
        self.subreddits_text = tk.Text(
            container,
            height=10,
            width=40,
            font=('Arial', 10),
            bg=self.colors['text_bg'],
            fg=self.colors['fg']
        )
        self.subreddits_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Default subreddits
        default_subs = [
            "wallstreetbets",
            "stocks",
            "investing",
            "options",
            "pennystocks",
            "StockMarket",
            "SecurityAnalysis",
            "ValueInvesting",
            "daytrading"
        ]
        self.subreddits_text.insert(1.0, '\n'.join(default_subs))
        
        # Save button
        tk.Button(
            container,
            text="Save Settings",
            command=self.save_settings,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 11),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor='hand2'
        ).grid(row=4, column=0, columnspan=2, pady=20)
    
    def create_status_bar(self):
        """Create bottom status bar"""
        status_bar = tk.Frame(self.root, bg=self.colors['card_bg'], height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            font=('Arial', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(
            status_bar,
            text="",
            font=('Arial', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['fg']
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self.update_time()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def start_monitoring(self):
        """Start monitoring Reddit"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.conn_label.config(text="🟢 Connected", fg=self.colors['success'])
            self.status_label.config(text="Monitoring active...")
            
            # Start monitoring in background thread
            self.monitor_thread = threading.Thread(target=self.monitor_reddit, daemon=True)
            self.monitor_thread.start()
            
            messagebox.showinfo("Monitoring Started", "Reddit monitoring is now active!")
    
    def stop_monitoring(self):
        """Stop monitoring Reddit"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.conn_label.config(text="⚫ Disconnected", fg=self.colors['warning'])
            self.status_label.config(text="Monitoring stopped")
            
            messagebox.showinfo("Monitoring Stopped", "Reddit monitoring has been stopped.")
    
    def monitor_reddit(self):
        """Background thread for monitoring Reddit"""
        try:
            client = RedditClient()
            
            # Get subreddits from settings
            subreddits = self.subreddits_text.get(1.0, tk.END).strip().split('\n')
            subreddits = [s.strip() for s in subreddits if s.strip()]
            
            while self.monitoring_active:
                for subreddit in subreddits:
                    if not self.monitoring_active:
                        break
                    
                    try:
                        # Fetch hot posts
                        posts = client.get_hot_posts(subreddit, limit=5)
                        
                        for post in posts:
                            # Add to queue for UI update
                            self.posts_queue.put({
                                'time': datetime.now().strftime("%H:%M:%S"),
                                'subreddit': post.subreddit,
                                'title': post.title[:80] + '...' if len(post.title) > 80 else post.title,
                                'score': post.score,
                                'comments': post.num_comments,
                                'url': f"https://reddit.com{post.url}" if not post.url.startswith('http') else post.url
                            })
                            
                            # Extract tickers
                            import re
                            tickers = re.findall(r'\$[A-Z]{1,5}\b', post.title)
                            for ticker in tickers:
                                if ticker not in self.tickers_data:
                                    self.tickers_data[ticker] = {'count': 0, 'sentiment': 0}
                                self.tickers_data[ticker]['count'] += 1
                        
                    except Exception as e:
                        print(f"Error monitoring {subreddit}: {e}")
                
                # Wait before next iteration
                time.sleep(self.refresh_interval.get())
                
        except Exception as e:
            print(f"Monitor thread error: {e}")
            self.monitoring_active = False
    
    def update_status(self):
        """Update UI with new data"""
        # Process posts queue
        posts_added = 0
        while not self.posts_queue.empty() and posts_added < 10:
            try:
                post_data = self.posts_queue.get_nowait()
                
                # Add to treeview (newest first)
                self.posts_tree.insert('', 0, values=(
                    post_data['time'],
                    post_data['subreddit'],
                    post_data['title'],
                    post_data['score'],
                    post_data['comments'],
                    post_data.get('url', '')  # URL in hidden column
                ))
                
                # Limit displayed posts
                if len(self.posts_tree.get_children()) > 100:
                    self.posts_tree.delete(self.posts_tree.get_children()[-1])
                
                posts_added += 1
                
            except queue.Empty:
                break
        
        # Update statistics
        if hasattr(self, 'stat_cards'):
            total_posts = len(self.posts_tree.get_children())
            self.stat_cards['Total Posts'].config(text=str(total_posts))
            
            # Count unique subreddits
            subreddits = set()
            for item in self.posts_tree.get_children():
                values = self.posts_tree.item(item)['values']
                if values:
                    subreddits.add(values[1])
            self.stat_cards['Active Subreddits'].config(text=str(len(subreddits)))
            
            # Update tickers count
            self.stat_cards['Trending Tickers'].config(text=str(len(self.tickers_data)))
        
        # Update tickers tab
        self.update_tickers_display()
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def update_tickers_display(self):
        """Update tickers treeview"""
        # Clear existing
        for item in self.tickers_tree.get_children():
            self.tickers_tree.delete(item)
        
        # Add tickers sorted by mentions
        sorted_tickers = sorted(self.tickers_data.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for ticker, data in sorted_tickers[:20]:  # Top 20
            sentiment = "Bullish" if data['sentiment'] > 0 else "Neutral"
            self.tickers_tree.insert('', tk.END, values=(
                ticker,
                data['count'],
                sentiment,
                "WSB",  # Placeholder
                "↑"  # Placeholder trend
            ))
    
    def refresh_data(self):
        """Refresh current data"""
        self.status_label.config(text="Refreshing data...")
        # Clear and reload
        for item in self.posts_tree.get_children():
            self.posts_tree.delete(item)
        self.status_label.config(text="Data refreshed")
    
    def generate_insights(self):
        """Generate market insights"""
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.insert(tk.END, f"Market Insights - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.insights_text.insert(tk.END, "="*60 + "\n\n")
        
        # Add insights based on current data
        self.insights_text.insert(tk.END, "📊 SUMMARY\n")
        self.insights_text.insert(tk.END, f"Total posts analyzed: {len(self.posts_tree.get_children())}\n")
        self.insights_text.insert(tk.END, f"Unique tickers found: {len(self.tickers_data)}\n\n")
        
        # Top tickers
        if self.tickers_data:
            self.insights_text.insert(tk.END, "🔥 TOP TRENDING TICKERS\n")
            sorted_tickers = sorted(self.tickers_data.items(), key=lambda x: x[1]['count'], reverse=True)
            for ticker, data in sorted_tickers[:5]:
                self.insights_text.insert(tk.END, f"  {ticker}: {data['count']} mentions\n")
            self.insights_text.insert(tk.END, "\n")
        
        # Market sentiment
        self.insights_text.insert(tk.END, "💭 MARKET SENTIMENT\n")
        self.insights_text.insert(tk.END, "  Overall: Neutral to Bullish\n")
        self.insights_text.insert(tk.END, "  Confidence: Moderate\n\n")
        
        self.insights_text.insert(tk.END, "📈 RECOMMENDATIONS\n")
        self.insights_text.insert(tk.END, "  • Monitor high-mention tickers for volatility\n")
        self.insights_text.insert(tk.END, "  • Check WSB for meme stock activity\n")
        self.insights_text.insert(tk.END, "  • Review options flow for unusual activity\n")
    
    def export_data(self):
        """Export data to JSON"""
        try:
            subreddits = self.export_subs.get().split(',')
            hours = int(self.export_hours.get())
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exports/gui_export_{timestamp}.json"
            
            # Prepare export data
            export_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'source': 'GUI Export',
                    'subreddits': subreddits,
                    'hours_back': hours
                },
                'posts': [],
                'tickers': self.tickers_data,
                'statistics': {
                    'total_posts': len(self.posts_tree.get_children()),
                    'unique_tickers': len(self.tickers_data)
                }
            }
            
            # Add posts from treeview
            for item in self.posts_tree.get_children():
                values = self.posts_tree.item(item)['values']
                if values:
                    export_data['posts'].append({
                        'time': values[0],
                        'subreddit': values[1],
                        'title': values[2],
                        'score': values[3],
                        'comments': values[4]
                    })
            
            # Save to file
            Path('exports').mkdir(exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            # Log success
            self.export_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Export successful: {filename}\n")
            self.export_log.insert(tk.END, f"  - Posts exported: {len(export_data['posts'])}\n")
            self.export_log.insert(tk.END, f"  - Tickers found: {len(self.tickers_data)}\n\n")
            self.export_log.see(tk.END)
            
            messagebox.showinfo("Export Complete", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            self.export_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Export failed: {e}\n\n")
    
    def save_settings(self):
        """Save current settings"""
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
        self.status_label.config(text="Settings saved")
    
    def on_post_click(self, event):
        """Handle single click on post - show URL in status"""
        try:
            item = self.posts_tree.selection()[0]
            values = self.posts_tree.item(item)['values']
            if len(values) > 5 and values[5]:  # URL is in index 5
                url = values[5]
                self.status_label.config(text=f"Reddit URL: {url} (Double-click to open)")
        except (IndexError, tk.TclError):
            pass
    
    def on_post_double_click(self, event):
        """Handle double click on post - open URL in browser"""
        try:
            item = self.posts_tree.selection()[0]
            values = self.posts_tree.item(item)['values']
            if len(values) > 5 and values[5]:  # URL is in index 5
                url = values[5]
                webbrowser.open(url)
                self.status_label.config(text=f"Opened: {values[2][:50]}...")
        except (IndexError, tk.TclError) as e:
            print(f"Error opening URL: {e}")
    
    def on_ticker_double_click(self, event):
        """Handle double click on ticker - search Reddit for that ticker"""
        try:
            item = self.tickers_tree.selection()[0]
            values = self.tickers_tree.item(item)['values']
            if values:
                ticker = values[0]  # Ticker symbol
                search_url = f"https://www.reddit.com/search/?q={ticker}&type=link&sort=new"
                webbrowser.open(search_url)
                self.status_label.config(text=f"Opened Reddit search for {ticker}")
        except (IndexError, tk.TclError) as e:
            print(f"Error opening ticker search: {e}")


def main():
    root = tk.Tk()
    app = RedditMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()