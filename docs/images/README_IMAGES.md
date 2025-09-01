# Screenshot Placeholders

This folder contains placeholder references for GUI screenshots.

To add actual screenshots:

1. **Desktop GUI Screenshot**: 
   - Run: `python gui/tkinter_app/reddit_monitor_gui.py`
   - Take screenshot when monitoring is active
   - Save as: `desktop_gui_preview.png`

2. **Web Dashboard Screenshot**:
   - Run: `python gui/web_app/app.py`
   - Open: http://localhost:5000
   - Start monitoring and take screenshot
   - Save as: `web_dashboard_preview.png`

3. **Command Line Screenshot**:
   - Run: `python main.py monitor`
   - Take terminal screenshot showing live output
   - Save as: `cli_preview.png`

## Recommended Screenshot Content

### Desktop GUI
- Show the Live Monitor tab with posts flowing
- Display statistics cards with real numbers
- Include trending tickers in the sidebar

### Web Dashboard  
- Show the main dashboard with charts
- Display real-time post feed
- Include the header with connection status

### Command Line
- Show live monitoring output with colored text
- Include some priority post alerts
- Display performance statistics

## Image Specifications
- **Format**: PNG with transparency support
- **Size**: 1200x800px (desktop), 800x600px (mobile views)
- **Quality**: High resolution for README display
- **Annotations**: Add callouts highlighting key features