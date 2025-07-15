#!/usr/bin/env python3
"""
NSE Historical Options Chain Data Scraper
Author: AI Assistant
Description: Downloads historical options chain data from NSE using Selenium for proper session management
"""

import os
import time
import json
import glob
import platform
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from urllib.parse import urlencode
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NSEDataScraper:
    def __init__(self, headless=True):
        """Initialize the NSE data scraper with Selenium WebDriver"""
        self.base_url = "https://www.nseindia.com"
        self.driver = None
        self.session = requests.Session()
        self.headless = headless
        self.setup_driver()
        
    def setup_driver(self):
        """Set up Chrome WebDriver with proper options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Set platform-specific user agent
        system_platform = platform.system().lower()
        if system_platform == "windows":
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        elif system_platform == "darwin":  # macOS
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        else:  # Linux
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Additional options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Windows-specific options
        if system_platform == "windows":
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
        
        try:
            # Try to get chrome driver path and verify it
            driver_path = ChromeDriverManager().install()
            logger.info(f"Chrome driver path: {driver_path}")
            
            # Check if the path points to actual chromedriver executable
            # Handle platform-specific executable names
            executable_name = "chromedriver.exe" if system_platform == "windows" else "chromedriver"
            
            if not (driver_path.endswith('chromedriver') or driver_path.endswith('chromedriver.exe')):
                # Look for chromedriver in the directory
                driver_dir = os.path.dirname(driver_path)
                
                # Search patterns for different platforms
                search_patterns = [
                    os.path.join(driver_dir, '**', executable_name),
                    os.path.join(driver_dir, executable_name)
                ]
                
                possible_paths = []
                for pattern in search_patterns:
                    possible_paths.extend(glob.glob(pattern, recursive=True))
                
                if possible_paths:
                    driver_path = possible_paths[0]
                    logger.info(f"Found chromedriver at: {driver_path}")
                else:
                    logger.error(f"Could not find {executable_name} executable in {driver_dir}")
                    raise Exception(f"Chrome driver not found: {executable_name}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            logger.info("Trying alternative Chrome driver setup...")
            
            # Fallback: try without webdriver-manager
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Successfully initialized Chrome driver using system PATH")
            except Exception as e2:
                logger.error(f"All Chrome driver setup methods failed: {e2}")
                raise Exception("Could not initialize Chrome driver. Please ensure Chrome browser is installed and available in PATH.")
        
    def initialize_session(self):
        """Initialize session by visiting NSE website and getting cookies"""
        logger.info("Initializing NSE session...")
        
        try:
            # Visit the main NSE page first
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Visit the FO reports page to get proper session
            fo_reports_url = f"{self.base_url}/report-detail/fo_eq_security"
            self.driver.get(fo_reports_url)
            time.sleep(5)
            
            # Wait for page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get cookies from selenium and add to requests session
            selenium_cookies = self.driver.get_cookies()
            for cookie in selenium_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # Set up headers to match browser request
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': fo_reports_url
            })
            
            logger.info("Session initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def get_expiry_dates(self, year, instrument="FUTIDX", symbol="NIFTY"):
        """Get all expiry dates for the given year"""
        logger.info(f"Getting expiry dates for {symbol} {instrument} {year}")
        
        url = f"{self.base_url}/api/historicalOR/meta/foCPV/expireDts"
        params = {
            'instrument': instrument,
            'symbol': symbol,
            'year': year
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            # Check for different possible keys in response
            expiry_dates = None
            if 'expiryDt' in data:
                expiry_dates = data['expiryDt']
            elif 'expiresDts' in data:
                expiry_dates = data['expiresDts']
            elif 'expiryDates' in data:
                expiry_dates = data['expiryDates']
            
            if expiry_dates:
                logger.info(f"Found {len(expiry_dates)} expiry dates: {expiry_dates}")
                return expiry_dates
            else:
                logger.warning(f"No expiry dates found in response: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get expiry dates: {e}")
            return []
    
    def calculate_date_range(self, expiry_date_str):
        """Calculate start and end dates based on expiry date"""
        try:
            # Parse expiry date (format: DD-MMM-YYYY)
            expiry_date = datetime.strptime(expiry_date_str, "%d-%b-%Y")
            
            # Start date: 60 days before expiry
            start_date = expiry_date - timedelta(days=60)
            
            # End date: 1 day after expiry
            end_date = expiry_date + timedelta(days=1)
            
            # Format dates as DD-MM-YYYY for API
            start_date_str = start_date.strftime("%d-%m-%Y")
            end_date_str = end_date.strftime("%d-%m-%Y")
            
            logger.info(f"Expiry: {expiry_date_str}, Range: {start_date_str} to {end_date_str}")
            return start_date_str, end_date_str, expiry_date.year
            
        except Exception as e:
            logger.error(f"Failed to calculate date range for {expiry_date_str}: {e}")
            return None, None, None
    
    def create_folder_structure(self, base_dir="nse_data"):
        """Create organized folder structure for data storage"""
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return base_dir
    
    def download_csv_data(self, expiry_date, start_date, end_date, year, 
                         instrument="FUTIDX", symbol="NIFTY", base_dir="nse_data"):
        """Download CSV data for specific expiry"""
        logger.info(f"Downloading CSV for expiry {expiry_date}")
        
        # Create folder structure: base_dir/YEAR/SYMBOL/INSTRUMENT/
        folder_path = os.path.join(base_dir, str(year), symbol, instrument)
        os.makedirs(folder_path, exist_ok=True)
        
        # Prepare API call
        url = f"{self.base_url}/api/historicalOR/foCPV"
        params = {
            'from': start_date,
            'to': end_date,
            'instrumentType': instrument,
            'symbol': symbol,
            'year': year,
            'expiryDate': expiry_date,
            'csv': 'true'
        }
        
        try:
            # Make request with session cookies
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Check if response is CSV data
            if response.headers.get('content-type', '').startswith('text/csv') or \
               response.headers.get('content-disposition', '').startswith('attachment'):
                
                # Create filename
                clean_expiry = expiry_date.replace('-', '_')
                filename = f"{symbol}_{instrument}_{clean_expiry}_{start_date.replace('-', '_')}_to_{end_date.replace('-', '_')}.csv"
                filepath = os.path.join(folder_path, filename)
                
                # Save CSV file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                logger.info(f"Successfully downloaded: {filepath}")
                return filepath
            else:
                # Try to parse JSON response and convert to CSV
                try:
                    data = response.json()
                    
                    # Check if we have data in the expected format
                    if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                        logger.info(f"Received JSON data with {len(data['data'])} records, converting to CSV")
                        
                        # Convert JSON to CSV using pandas
                        import pandas as pd
                        df = pd.DataFrame(data['data'])
                        
                        # Create filename
                        clean_expiry = expiry_date.replace('-', '_')
                        filename = f"{symbol}_{instrument}_{clean_expiry}_{start_date.replace('-', '_')}_to_{end_date.replace('-', '_')}.csv"
                        filepath = os.path.join(folder_path, filename)
                        
                        # Save as CSV
                        df.to_csv(filepath, index=False)
                        
                        logger.info(f"Successfully converted JSON to CSV and saved: {filepath}")
                        logger.info(f"Data contains columns: {list(df.columns)}")
                        logger.info(f"Date range in data: {df['FH_TIMESTAMP'].min()} to {df['FH_TIMESTAMP'].max()}")
                        return filepath
                    else:
                        logger.error(f"JSON response does not contain expected data format: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        return None
                        
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON response: {json_error}")
                    logger.error(f"Response content (first 500 chars): {response.text[:500]}")
                    return None
                
        except Exception as e:
            logger.error(f"Failed to download CSV for expiry {expiry_date}: {e}")
            return None
    
    def process_year(self, year, symbol="NIFTY", instrument="FUTIDX", test_single=False):
        """Process all expiries for a given year"""
        logger.info(f"Processing year {year} for {symbol} {instrument}")
        
        # Initialize session first
        if not self.initialize_session():
            logger.error("Failed to initialize session. Aborting.")
            return False
        
        # Create base directory
        base_dir = self.create_folder_structure()
        
        # Get expiry dates
        expiry_dates = self.get_expiry_dates(year, instrument, symbol)
        if not expiry_dates:
            logger.error("No expiry dates found")
            return False
        
        # If testing, only process first expiry
        if test_single:
            expiry_dates = expiry_dates[:1]
            logger.info(f"Testing mode: Processing only first expiry: {expiry_dates[0]}")
        
        success_count = 0
        total_expiries = len(expiry_dates)
        
        for i, expiry_date in enumerate(expiry_dates, 1):
            logger.info(f"Processing expiry {i}/{total_expiries}: {expiry_date}")
            
            # Calculate date range
            start_date, end_date, exp_year = self.calculate_date_range(expiry_date)
            if not start_date or not end_date:
                logger.error(f"Failed to calculate dates for expiry {expiry_date}")
                continue
            
            # Download CSV
            filepath = self.download_csv_data(
                expiry_date, start_date, end_date, exp_year,
                instrument, symbol, base_dir
            )
            
            if filepath:
                success_count += 1
                logger.info(f"Successfully processed {expiry_date}")
            else:
                logger.error(f"Failed to process {expiry_date}")
            
            # Add small delay between requests
            time.sleep(2)
        
        logger.info(f"Completed processing. Success: {success_count}/{total_expiries}")
        return success_count > 0
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()

def main():
    """Main function to run the scraper"""
    print("NSE Historical Options Chain Data Scraper")
    print("=" * 50)
    
    # Get year input from user
    while True:
        try:
            year = input("Enter the year (e.g., 2015): ").strip()
            year = int(year)
            if 2000 <= year <= datetime.now().year:
                break
            else:
                print("Please enter a valid year between 2000 and current year")
        except ValueError:
            print("Please enter a valid year")
    
    # Ask if user wants to test with single expiry first
    test_mode = input("Test with single expiry first? (y/n): ").strip().lower() == 'y'
    
    # Create scraper instance
    scraper = NSEDataScraper(headless=False)  # Set to False to see browser for debugging
    
    try:
        # Process the year
        success = scraper.process_year(year, test_single=test_mode)
        
        if success:
            print(f"\n✅ Successfully completed processing for year {year}")
            print(f"📁 Data saved in: nse_data/{year}/NIFTY/FUTIDX/")
        else:
            print(f"\n❌ Failed to process year {year}")
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        logger.error(f"Main process error: {e}")
    finally:
        # Clean up
        scraper.close()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    main() 