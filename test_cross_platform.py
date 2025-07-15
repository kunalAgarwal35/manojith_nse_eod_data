#!/usr/bin/env python3
"""
Cross-platform compatibility test for NSE Data Scraper
Tests Chrome driver setup and basic functionality across Windows, macOS, and Linux
"""

import platform
import os
import sys
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_platform_detection():
    """Test platform detection"""
    print("Platform Detection Test")
    print("=" * 30)
    
    system = platform.system()
    machine = platform.machine()
    python_version = platform.python_version()
    
    print(f"Operating System: {system}")
    print(f"Architecture: {machine}")
    print(f"Python Version: {python_version}")
    
    # Test platform-specific paths
    if system == "Windows":
        expected_executable = "chromedriver.exe"
    else:
        expected_executable = "chromedriver"
    
    print(f"Expected Chrome driver executable: {expected_executable}")
    print()
    return True

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Dependencies Test")
    print("=" * 30)
    
    required_packages = [
        'selenium',
        'webdriver_manager',
        'requests',
        'pandas',
        'dateutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dateutil':
                import dateutil
            elif package == 'webdriver_manager':
                import webdriver_manager
            else:
                __import__(package)
            print(f"✅ {package} - Available")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies available")
        return True

def test_chrome_detection():
    """Test Chrome browser detection"""
    print("Chrome Browser Detection Test")
    print("=" * 30)
    
    system = platform.system()
    
    # Common Chrome installation paths by platform
    chrome_paths = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ],
        "Darwin": [  # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    }
    
    found_chrome = False
    
    if system in chrome_paths:
        for path in chrome_paths[system]:
            if os.path.exists(path):
                print(f"✅ Chrome found at: {path}")
                found_chrome = True
                break
    
    if not found_chrome:
        print("⚠️  Chrome browser not found in common locations")
        print("Please ensure Google Chrome is installed")
        return False
    
    return True

def test_webdriver_manager():
    """Test webdriver-manager functionality"""
    print("WebDriver Manager Test")
    print("=" * 30)
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Attempting to download Chrome driver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ Chrome driver available at: {driver_path}")
        
        # Verify the file exists and is executable
        if os.path.exists(driver_path):
            print("✅ Driver file exists")
            
            # Check if it's the correct executable for platform
            system = platform.system()
            if system == "Windows" and driver_path.endswith('.exe'):
                print("✅ Correct Windows executable (.exe)")
            elif system != "Windows" and not driver_path.endswith('.exe'):
                print("✅ Correct Unix executable (no .exe)")
            else:
                print("⚠️  Unexpected executable format")
            
            return True
        else:
            print("❌ Driver file not found")
            return False
            
    except Exception as e:
        print(f"❌ WebDriver manager test failed: {e}")
        return False

def test_basic_scraper_import():
    """Test if the NSE scraper can be imported and initialized"""
    print("NSE Scraper Import Test")
    print("=" * 30)
    
    try:
        from nse_data_scraper import NSEDataScraper
        print("✅ NSE scraper imported successfully")
        
        # Test initialization (without actually starting browser)
        print("Testing basic initialization...")
        scraper = NSEDataScraper(headless=True)
        print("✅ NSE scraper initialized")
        
        # Test cleanup
        scraper.close()
        print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ NSE scraper test failed: {e}")
        return False

def test_date_handling():
    """Test date parsing and formatting across platforms"""
    print("Date Handling Test")
    print("=" * 30)
    
    try:
        from datetime import datetime, timedelta
        
        # Test date parsing formats used by NSE
        test_date_str = "25-JAN-2024"
        parsed_date = datetime.strptime(test_date_str, "%d-%b-%Y")
        print(f"✅ Date parsing: {test_date_str} → {parsed_date}")
        
        # Test date arithmetic
        start_date = parsed_date - timedelta(days=60)
        end_date = parsed_date + timedelta(days=1)
        
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")
        
        print(f"✅ Date calculation: {start_str} to {end_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ Date handling test failed: {e}")
        return False

def main():
    """Run all cross-platform compatibility tests"""
    print("NSE Data Scraper - Cross-Platform Compatibility Test")
    print("=" * 60)
    print(f"Testing on: {platform.platform()}")
    print("=" * 60)
    
    tests = [
        test_platform_detection,
        test_dependencies,
        test_chrome_detection,
        test_webdriver_manager,
        test_date_handling,
        test_basic_scraper_import
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("Test Summary")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The scraper should work on this platform.")
        return 0
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 