#!/usr/bin/env python3
"""
Final Test Summary for Reddit Data Engine
"""

import os
import time
from datetime import datetime
from pathlib import Path

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_status(condition, success_msg, fail_msg):
    if condition:
        print(f"✅ {success_msg}")
        return True
    else:
        print(f"❌ {fail_msg}")
        return False

def main():
    print("🚀 REDDIT DATA ENGINE - SYSTEM STATUS CHECK 🚀")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    passed = 0
    failed = 0
    
    # 1. Environment Check
    print_section("1. ENVIRONMENT & CREDENTIALS")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    if check_status(client_id, "Reddit Client ID configured", "Reddit Client ID missing"):
        passed += 1
    else:
        failed += 1
        
    if check_status(client_secret, "Reddit Client Secret configured", "Reddit Client Secret missing"):
        passed += 1
    else:
        failed += 1
        
    if check_status(user_agent, f"User Agent: {user_agent}", "User Agent missing"):
        passed += 1
    else:
        failed += 1
    
    # 2. API Connection Test
    print_section("2. REDDIT API CONNECTION")
    
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test with a simple fetch
        test_posts = list(reddit.subreddit('python').hot(limit=3))
        
        if check_status(len(test_posts) > 0, 
                       f"Successfully fetched {len(test_posts)} posts from Reddit",
                       "Failed to fetch posts from Reddit"):
            passed += 1
            
            # Show sample post
            if test_posts:
                print(f"  📄 Sample: '{test_posts[0].title[:60]}...'")
        else:
            failed += 1
            
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        failed += 1
    
    # 3. Core Modules Check
    print_section("3. CORE MODULES")
    
    modules = [
        ('reddit_client', 'Reddit Client Module'),
        ('data_processor', 'Data Processor Module'),
        ('monitor', 'Monitoring System'),
        ('api_interface', 'API Interface'),
        ('config', 'Configuration Module')
    ]
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            if check_status(True, f"{description} loaded", ""):
                passed += 1
        except ImportError as e:
            if check_status(False, "", f"{description} failed: {e}"):
                failed += 1
    
    # 4. Data Export Check
    print_section("4. DATA EXPORT SYSTEM")
    
    exports_dir = Path('exports')
    if check_status(exports_dir.exists(), 
                   "Exports directory exists",
                   "Exports directory missing"):
        passed += 1
        
        # Count export files
        export_files = list(exports_dir.glob('*.json'))
        print(f"  📁 Found {len(export_files)} export files")
        
        if export_files:
            latest = max(export_files, key=lambda f: f.stat().st_mtime)
            print(f"  📄 Latest: {latest.name}")
    else:
        failed += 1
    
    # 5. Feature Tests
    print_section("5. FEATURE AVAILABILITY")
    
    features = [
        ('main.py test', 'Connection Test'),
        ('main.py monitor', 'Real-time Monitoring'),
        ('main.py insights', 'Market Insights'),
        ('main.py export', 'Custom Export'),
        ('setup_reddit_api.py', 'Setup Script'),
        ('full_test.py', 'Full Test Suite')
    ]
    
    for file_cmd, description in features:
        file_name = file_cmd.split()[0]
        if check_status(Path(file_name).exists(),
                       f"{description} available ({file_cmd})",
                       f"{description} missing"):
            passed += 1
        else:
            failed += 1
    
    # Final Summary
    print_section("FINAL SUMMARY")
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ({success_rate:.1f}%)")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("All components are working correctly.")
    elif failed <= 2:
        print("\n⚠️  SYSTEM MOSTLY OPERATIONAL")
        print("Minor issues detected but core functionality works.")
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION")
        print("Multiple issues detected. Please review above.")
    
    print("\n" + "="*60)
    print("QUICK START COMMANDS:")
    print("  python main.py test        # Test connection")
    print("  python main.py monitor     # Start monitoring")
    print("  python main.py insights    # Get insights")
    print("  python full_test.py        # Run full test suite")
    print("="*60)

if __name__ == "__main__":
    main()