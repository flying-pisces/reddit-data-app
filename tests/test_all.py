"""
Main test runner for Reddit Data Engine
Run with: python -m pytest test_all.py -v
"""
import pytest
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)

def test_imports():
    """Test that all modules can be imported"""
    try:
        import reddit_client
        import data_processor  
        import api_interface
        import monitor
        import config
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

def test_dependencies():
    """Test that required dependencies are available"""
    required_packages = [
        'praw',
        'asyncpraw', 
        'pandas',
        'numpy',
        'aiofiles',
        'asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        pytest.fail(f"Missing required packages: {missing_packages}")

def test_configuration():
    """Test configuration is valid"""
    from config import MonitoringConfig, DataConfig, RedditConfig
    
    # Test monitoring config
    assert len(MonitoringConfig.ALL_SUBREDDITS) > 0
    assert MonitoringConfig.HOT_POSTS_INTERVAL > 0
    assert MonitoringConfig.NEW_POSTS_INTERVAL > 0
    assert MonitoringConfig.MIN_SCORE >= 0
    assert MonitoringConfig.MIN_COMMENTS >= 0
    
    # Test data config  
    assert DataConfig.EXPORT_INTERVAL > 0
    assert DataConfig.DATA_RETENTION_HOURS > 0
    
    # Test Reddit config structure
    assert hasattr(RedditConfig, 'USER_AGENT')
    assert RedditConfig.USER_AGENT is not None

if __name__ == "__main__":
    print("🧪 Running Reddit Data Engine Test Suite")
    print(f"📅 Started at: {datetime.now()}")
    print("=" * 50)
    
    # Run the basic tests first
    test_imports()
    test_dependencies()
    test_configuration()
    
    print("✅ Basic tests passed")
    
    # Run pytest with coverage if available
    try:
        pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "--durations=10"
        ])
    except SystemExit as e:
        print(f"\n🏁 Test suite completed with exit code: {e.code}")
        sys.exit(e.code)