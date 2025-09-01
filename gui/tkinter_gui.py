"""
Tkinter GUI for Reddit Data Engine
Real-time monitoring dashboard with live updates
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import time
from datetime import datetime
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_interface import AnalysisAPI, SimpleAPI
from reddit_client import RedditClient
from config import MonitoringConfig


class RedditDataGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reddit Data Engine - Live Dashboard")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # API interfaces
        self.api = AnalysisAPI()
        self.simple_api = SimpleAPI()
        self.reddit_client = None
        
        # Data storage
        self.current_data = {}
        self.is_monitoring = False
        self.update_thread = None
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_overview_tab()
        self.create_tickers_tab()
        self.create_sentiment_tab()
        self.create_posts_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click 'Start Monitoring' to begin")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.start_btn = ttk.Button(self.control_frame, text="Start Monitoring", 
                                  command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(self.control_frame, text="Stop Monitoring", 
                                 command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(self.control_frame, text="Refresh Now", 
                                    command=self.manual_refresh)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(self.control_frame, text="Export Data", 
                                   command=self.export_data)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Last updated label
        self.last_updated_var = tk.StringVar()
        self.last_updated_var.set("Last updated: Never")
        ttk.Label(self.control_frame, textvariable=self.last_updated_var).pack(side=tk.RIGHT, padx=5)
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.manual_refresh)
        view_menu.add_command(label="Clear Data", command=self.clear_data)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_overview_tab(self):
        """Create overview/dashboard tab"""
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        
        # Market mood section
        mood_frame = ttk.LabelFrame(self.overview_frame, text="Market Mood", padding=10)
        mood_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mood_var = tk.StringVar()
        self.mood_var.set("Unknown")
        mood_label = ttk.Label(mood_frame, textvariable=self.mood_var, font=('Arial', 16, 'bold'))
        mood_label.pack()
        
        # Key metrics section
        metrics_frame = ttk.LabelFrame(self.overview_frame, text="Key Metrics", padding=10)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        metrics_inner = ttk.Frame(metrics_frame)
        metrics_inner.pack(fill=tk.X)
        
        # Create metric displays
        self.metrics = {}
        metric_names = ["Total Posts", "Speculative Posts", "Active Subreddits", "Trending Tickers"]
        
        for i, metric in enumerate(metric_names):
            frame = ttk.Frame(metrics_inner)
            frame.grid(row=0, column=i, padx=10, sticky="ew")
            metrics_inner.columnconfigure(i, weight=1)
            
            ttk.Label(frame, text=metric, font=('Arial', 10, 'bold')).pack()
            self.metrics[metric] = tk.StringVar()
            self.metrics[metric].set("--")
            ttk.Label(frame, textvariable=self.metrics[metric], 
                     font=('Arial', 14)).pack()
        
        # Alerts section
        alerts_frame = ttk.LabelFrame(self.overview_frame, text="Alerts", padding=10)
        alerts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.alerts_text = scrolledtext.ScrolledText(alerts_frame, height=8, state=tk.DISABLED)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
    
    def create_tickers_tab(self):
        """Create trending tickers tab"""
        self.tickers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tickers_frame, text="Trending Tickers")
        
        # Tickers treeview
        columns = ("Rank", "Ticker", "Mentions", "Trend")
        self.tickers_tree = ttk.Treeview(self.tickers_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tickers_tree.heading(col, text=col)
            self.tickers_tree.column(col, width=100, anchor="center")
        
        # Scrollbar for tickers tree
        tickers_scrollbar = ttk.Scrollbar(self.tickers_frame, orient=tk.VERTICAL, 
                                        command=self.tickers_tree.yview)
        self.tickers_tree.configure(yscrollcommand=tickers_scrollbar.set)
        
        self.tickers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        tickers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
    
    def create_sentiment_tab(self):
        """Create sentiment analysis tab"""
        self.sentiment_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sentiment_frame, text="Sentiment")
        
        # Overall sentiment
        overall_frame = ttk.LabelFrame(self.sentiment_frame, text="Overall Sentiment", padding=10)
        overall_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sentiment_inner = ttk.Frame(overall_frame)
        sentiment_inner.pack(fill=tk.X)
        
        # Sentiment metrics
        self.sentiment_metrics = {}
        sentiment_labels = ["Mood", "Average Score", "Positive", "Negative", "Neutral"]
        
        for i, label in enumerate(sentiment_labels):
            frame = ttk.Frame(sentiment_inner)
            frame.grid(row=0, column=i, padx=10, sticky="ew")
            sentiment_inner.columnconfigure(i, weight=1)
            
            ttk.Label(frame, text=label, font=('Arial', 10, 'bold')).pack()
            self.sentiment_metrics[label] = tk.StringVar()
            self.sentiment_metrics[label].set("--")
            ttk.Label(frame, textvariable=self.sentiment_metrics[label], 
                     font=('Arial', 12)).pack()
        
        # Subreddit sentiment breakdown
        breakdown_frame = ttk.LabelFrame(self.sentiment_frame, text="Subreddit Breakdown", padding=10)
        breakdown_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Subreddit", "Posts", "Avg Score", "Speculative %", "Activity")
        self.sentiment_tree = ttk.Treeview(breakdown_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.sentiment_tree.heading(col, text=col)
            self.sentiment_tree.column(col, width=120, anchor="center")
        
        sentiment_scrollbar = ttk.Scrollbar(breakdown_frame, orient=tk.VERTICAL,
                                          command=self.sentiment_tree.yview)
        self.sentiment_tree.configure(yscrollcommand=sentiment_scrollbar.set)
        
        self.sentiment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sentiment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_posts_tab(self):
        """Create priority posts tab"""
        self.posts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.posts_frame, text="Priority Posts")
        
        # Filter frame
        filter_frame = ttk.Frame(self.posts_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filter by category:").pack(side=tk.LEFT, padx=5)
        
        self.category_filter = ttk.Combobox(filter_frame, 
                                          values=["All"] + list(MonitoringConfig.SUBREDDITS.keys()))
        self.category_filter.set("All")
        self.category_filter.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filter", 
                  command=self.apply_post_filter).pack(side=tk.LEFT, padx=5)
        
        # Posts treeview
        columns = ("Score", "Comments", "Subreddit", "Title", "Speculative")
        self.posts_tree = ttk.Treeview(self.posts_frame, columns=columns, show="headings", height=15)
        
        column_widths = {"Score": 80, "Comments": 80, "Subreddit": 120, 
                        "Title": 400, "Speculative": 80}
        
        for col in columns:
            self.posts_tree.heading(col, text=col)
            self.posts_tree.column(col, width=column_widths.get(col, 100), anchor="w" if col == "Title" else "center")
        
        # Scrollbars
        posts_v_scrollbar = ttk.Scrollbar(self.posts_frame, orient=tk.VERTICAL,
                                        command=self.posts_tree.yview)
        posts_h_scrollbar = ttk.Scrollbar(self.posts_frame, orient=tk.HORIZONTAL,
                                        command=self.posts_tree.xview)
        
        self.posts_tree.configure(yscrollcommand=posts_v_scrollbar.set,
                                 xscrollcommand=posts_h_scrollbar.set)
        
        self.posts_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        posts_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        posts_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Double-click to open post
        self.posts_tree.bind("<Double-1>", self.open_post_url)
    
    def create_settings_tab(self):
        """Create settings/configuration tab"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Monitoring settings
        monitor_frame = ttk.LabelFrame(self.settings_frame, text="Monitoring Settings", padding=10)
        monitor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Update interval
        ttk.Label(monitor_frame, text="Update Interval (seconds):").grid(row=0, column=0, sticky="w", padx=5)
        self.update_interval = tk.IntVar(value=30)
        ttk.Entry(monitor_frame, textvariable=self.update_interval, width=10).grid(row=0, column=1, padx=5)
        
        # Subreddit selection
        subreddits_frame = ttk.LabelFrame(self.settings_frame, text="Monitored Subreddits", padding=10)
        subreddits_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.subreddit_vars = {}
        row = 0
        col = 0
        
        for category, subreddits in MonitoringConfig.SUBREDDITS.items():
            # Category label
            ttk.Label(subreddits_frame, text=f"{category.replace('_', ' ').title()}:", 
                     font=('Arial', 10, 'bold')).grid(row=row, column=col, columnspan=2, sticky="w", pady=(10, 5))
            row += 1
            
            for subreddit in subreddits:
                var = tk.BooleanVar(value=True)
                self.subreddit_vars[subreddit] = var
                ttk.Checkbutton(subreddits_frame, text=f"r/{subreddit}", 
                              variable=var).grid(row=row, column=col, sticky="w", padx=10)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
            
            if col != 0:
                col = 0
                row += 1
        
        # Apply settings button
        ttk.Button(subreddits_frame, text="Apply Settings", 
                  command=self.apply_settings).grid(row=row+1, column=0, pady=10)
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Start update thread
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
            
            self.status_var.set("Monitoring active - Fetching data...")
            self.add_alert("🚀 Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        if self.is_monitoring:
            self.is_monitoring = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
            self.status_var.set("Monitoring stopped")
            self.add_alert("⏹️ Monitoring stopped")
    
    def update_loop(self):
        """Main update loop running in background thread"""
        while self.is_monitoring:
            try:
                # Run async update in thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.fetch_data())
                loop.close()
                
                # Schedule UI update on main thread
                self.root.after(0, self.update_ui)
                
            except Exception as e:
                self.root.after(0, lambda: self.add_alert(f"❌ Error: {str(e)[:100]}"))
            
            # Wait for next update
            for _ in range(self.update_interval.get()):
                if not self.is_monitoring:
                    break
                time.sleep(1)
    
    async def fetch_data(self):
        """Fetch data from Reddit API"""
        try:
            # Get current insights
            self.current_data = {
                'trending_tickers': await self.api.get_trending_tickers(limit=20),
                'sentiment': await self.api.get_sentiment_overview(),
                'priority_posts': await self.api.get_priority_posts(limit=50),
                'subreddit_activity': await self.api.get_subreddit_activity(),
                'speculative_signals': await self.api.get_speculative_signals(),
                'market_mood': await self.simple_api.get_market_mood()
            }
            
        except Exception as e:
            raise Exception(f"Data fetch failed: {e}")
    
    def update_ui(self):
        """Update UI elements with current data"""
        if not self.current_data:
            return
        
        try:
            # Update overview tab
            self.update_overview_tab()
            
            # Update tickers tab
            self.update_tickers_tab()
            
            # Update sentiment tab
            self.update_sentiment_tab()
            
            # Update posts tab
            self.update_posts_tab()
            
            # Update last updated time
            self.last_updated_var.set(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            self.status_var.set("Data updated successfully")
            
        except Exception as e:
            self.add_alert(f"❌ UI update error: {str(e)[:100]}")
    
    def update_overview_tab(self):
        """Update overview tab with current data"""
        # Market mood
        mood = self.current_data.get('market_mood', 'Unknown')
        self.mood_var.set(mood.upper())
        
        # Key metrics
        sentiment_data = self.current_data.get('sentiment', {})
        speculative_data = self.current_data.get('speculative_signals', {})
        
        self.metrics["Total Posts"].set(str(sentiment_data.get('total', 0)))
        self.metrics["Speculative Posts"].set(str(speculative_data.get('total_speculative_posts', 0)))
        self.metrics["Active Subreddits"].set(str(len(self.current_data.get('subreddit_activity', {}))))
        self.metrics["Trending Tickers"].set(str(len(self.current_data.get('trending_tickers', []))))
    
    def update_tickers_tab(self):
        """Update trending tickers tab"""
        # Clear existing items
        for item in self.tickers_tree.get_children():
            self.tickers_tree.delete(item)
        
        # Add ticker data
        tickers = self.current_data.get('trending_tickers', [])
        for ticker_data in tickers:
            rank = ticker_data.get('rank', 0)
            ticker = ticker_data.get('ticker', '')
            mentions = ticker_data.get('mentions', 0)
            trend = "📈" if mentions > 10 else "📊"
            
            self.tickers_tree.insert('', 'end', values=(rank, f"${ticker}", mentions, trend))
    
    def update_sentiment_tab(self):
        """Update sentiment analysis tab"""
        sentiment = self.current_data.get('sentiment', {})
        
        # Update sentiment metrics
        self.sentiment_metrics["Mood"].set(sentiment.get('mood', 'Unknown').title())
        self.sentiment_metrics["Average Score"].set(f"{sentiment.get('average', 0):.3f}")
        self.sentiment_metrics["Positive"].set(str(sentiment.get('positive', 0)))
        self.sentiment_metrics["Negative"].set(str(sentiment.get('negative', 0)))
        self.sentiment_metrics["Neutral"].set(str(sentiment.get('neutral', 0)))
        
        # Update subreddit breakdown
        for item in self.sentiment_tree.get_children():
            self.sentiment_tree.delete(item)
        
        subreddit_data = self.current_data.get('subreddit_activity', {})
        for subreddit, data in subreddit_data.items():
            posts = data.get('total_posts', 0)
            avg_score = data.get('avg_score', 0)
            speculative_ratio = data.get('speculative_ratio', 0)
            activity = data.get('recent_activity', 0)
            
            self.sentiment_tree.insert('', 'end', values=(
                f"r/{subreddit}",
                posts,
                f"{avg_score:.1f}",
                f"{speculative_ratio:.1%}",
                activity
            ))
    
    def update_posts_tab(self):
        """Update priority posts tab"""
        # Clear existing items
        for item in self.posts_tree.get_children():
            self.posts_tree.delete(item)
        
        # Add post data
        posts = self.current_data.get('priority_posts', [])
        for post in posts:
            score = post.get('score', 0)
            comments = post.get('comments', 0)
            subreddit = f"r/{post.get('subreddit', '')}"
            title = post.get('title', '')[:80] + "..." if len(post.get('title', '')) > 80 else post.get('title', '')
            speculative = "🔥" if post.get('is_speculative', False) else ""
            
            self.posts_tree.insert('', 'end', values=(score, comments, subreddit, title, speculative))
    
    def manual_refresh(self):
        """Manually refresh data"""
        if not self.is_monitoring:
            # Single refresh
            thread = threading.Thread(target=self.single_refresh, daemon=True)
            thread.start()
        
    def single_refresh(self):
        """Single data refresh"""
        try:
            self.root.after(0, lambda: self.status_var.set("Refreshing data..."))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.fetch_data())
            loop.close()
            
            self.root.after(0, self.update_ui)
            self.root.after(0, lambda: self.add_alert("🔄 Data refreshed manually"))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_alert(f"❌ Refresh failed: {str(e)[:100]}"))
    
    def export_data(self):
        """Export current data to file"""
        if not self.current_data:
            messagebox.showwarning("No Data", "No data available to export")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Reddit Data"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.current_data, f, indent=2, default=str)
                
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
                self.add_alert(f"📤 Data exported to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export data: {e}")
    
    def load_data(self):
        """Load data from file"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Reddit Data"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.current_data = json.load(f)
                
                self.update_ui()
                messagebox.showinfo("Load Successful", f"Data loaded from {filename}")
                self.add_alert(f"📥 Data loaded from {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Load Failed", f"Failed to load data: {e}")
    
    def clear_data(self):
        """Clear all current data"""
        self.current_data = {}
        
        # Clear all UI elements
        self.mood_var.set("Unknown")
        for metric in self.metrics.values():
            metric.set("--")
        for metric in self.sentiment_metrics.values():
            metric.set("--")
        
        # Clear trees
        for item in self.tickers_tree.get_children():
            self.tickers_tree.delete(item)
        for item in self.sentiment_tree.get_children():
            self.sentiment_tree.delete(item)
        for item in self.posts_tree.get_children():
            self.posts_tree.delete(item)
        
        self.add_alert("🗑️ Data cleared")
    
    def apply_post_filter(self):
        """Apply category filter to posts"""
        selected_category = self.category_filter.get()
        if selected_category == "All":
            self.update_posts_tab()
        else:
            # Filter posts by category
            # This would require category information in the posts data
            self.update_posts_tab()  # For now, just refresh
    
    def apply_settings(self):
        """Apply changed settings"""
        # Update monitoring settings
        self.add_alert("⚙️ Settings applied")
    
    def open_post_url(self, event):
        """Open selected post URL in browser"""
        selection = self.posts_tree.selection()
        if selection:
            # This would require storing URLs with the post data
            self.add_alert("🔗 Post URL functionality not yet implemented")
    
    def add_alert(self, message):
        """Add alert message to alerts display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {message}\n"
        
        self.alerts_text.config(state=tk.NORMAL)
        self.alerts_text.insert(tk.END, alert_text)
        self.alerts_text.see(tk.END)
        self.alerts_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Reddit Data Engine GUI v1.0

Real-time monitoring dashboard for Reddit investment data.

Features:
• Live trending ticker tracking
• Market sentiment analysis  
• Priority post detection
• Speculative activity monitoring

Built with Python and Tkinter
        """
        messagebox.showinfo("About Reddit Data Engine", about_text)
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_monitoring:
            self.stop_monitoring()
        
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point for Tkinter GUI"""
    try:
        app = RedditDataGUI()
        app.run()
    except Exception as e:
        print(f"GUI Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()