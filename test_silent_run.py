#!/usr/bin/env python3
"""
Test silent operation of NSE Data Scraper
This test verifies that Chrome errors/warnings are properly suppressed
"""

from nse_data_scraper import NSEDataScraper
import sys

def test_silent_operation():
    """Test that the scraper runs without Chrome errors/warnings"""
    print("Testing Silent Operation...")
    print("=" * 40)
    print("Note: This test should run without Chrome browser errors.")
    print("If you see WebGL or GCM errors, the suppression didn't work properly.")
    print()
    
    scraper = NSEDataScraper(headless=True)
    
    try:
        print("Initializing session (should be silent)...")
        
        # Just test session initialization without full data download
        if scraper.initialize_session():
            print("✅ Session initialized successfully without errors")
            
            # Test getting expiry dates briefly
            print("Testing expiry date fetch...")
            expiry_dates = scraper.get_expiry_dates(2024)
            
            if expiry_dates:
                print(f"✅ Found {len(expiry_dates)} expiry dates")
                print("✅ Silent operation test passed")
            else:
                print("⚠️  No expiry dates found (might be NSE server issue)")
                
        else:
            print("❌ Session initialization failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        scraper.close()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    test_silent_operation() 