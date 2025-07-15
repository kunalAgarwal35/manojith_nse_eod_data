#!/usr/bin/env python3
"""
Example usage of NSE Data Scraper
"""

from nse_data_scraper import NSEDataScraper

def example_1_basic_usage():
    """Example 1: Basic usage with single year"""
    print("Example 1: Basic usage")
    print("-" * 30)
    
    scraper = NSEDataScraper(headless=True)  # Run in background
    
    try:
        # Download all expiries for 2024
        success = scraper.process_year(2024)
        if success:
            print("✅ Successfully downloaded 2024 data")
        else:
            print("❌ Failed to download 2024 data")
    finally:
        scraper.close()

def example_2_test_mode():
    """Example 2: Test with single expiry first"""
    print("Example 2: Test mode (single expiry)")
    print("-" * 30)
    
    scraper = NSEDataScraper(headless=False)  # Show browser for debugging
    
    try:
        # Test with single expiry first
        success = scraper.process_year(2024, test_single=True)
        if success:
            print("✅ Test successful - ready to process all expiries")
        else:
            print("❌ Test failed")
    finally:
        scraper.close()

def example_3_multiple_years():
    """Example 3: Download data for multiple years"""
    print("Example 3: Multiple years")
    print("-" * 30)
    
    scraper = NSEDataScraper(headless=True)
    
    try:
        years = [2022, 2023, 2024]
        for year in years:
            print(f"Processing year {year}...")
            success = scraper.process_year(year)
            if success:
                print(f"✅ Successfully downloaded {year} data")
            else:
                print(f"❌ Failed to download {year} data")
    finally:
        scraper.close()

def example_4_different_symbol():
    """Example 4: Download data for different symbol (BANKNIFTY)"""
    print("Example 4: Different symbol (BANKNIFTY)")
    print("-" * 30)
    
    scraper = NSEDataScraper(headless=True)
    
    try:
        # Download BANKNIFTY data
        success = scraper.process_year(2024, symbol="BANKNIFTY", instrument="FUTIDX")
        if success:
            print("✅ Successfully downloaded BANKNIFTY data")
        else:
            print("❌ Failed to download BANKNIFTY data")
    finally:
        scraper.close()

if __name__ == "__main__":
    print("NSE Data Scraper - Example Usage")
    print("=" * 50)
    
    # Choose which example to run
    print("Choose an example to run:")
    print("1. Basic usage (download all 2024 expiries)")
    print("2. Test mode (single expiry)")
    print("3. Multiple years (2022-2024)")
    print("4. Different symbol (BANKNIFTY)")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        example_1_basic_usage()
    elif choice == "2":
        example_2_test_mode()
    elif choice == "3":
        example_3_multiple_years()
    elif choice == "4":
        example_4_different_symbol()
    else:
        print("Invalid choice. Please run again and select 1-4.") 