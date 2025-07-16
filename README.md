# NSE Historical Options Chain Data Scraper

A Selenium-based Python application to download historical options chain data from NSE (National Stock Exchange of India) with proper session management and anti-bot protection handling.

## Features

- **Selenium-based session management**: Handles NSE's anti-bot protections by using real browser sessions
- **Automatic expiry date fetching**: Gets all available expiry dates for a given year
- **Smart date range calculation**: Automatically calculates 60 days before expiry as start date and 1 day after expiry as end date
- **Organized folder structure**: Saves files in `nse_data/YEAR/SYMBOL/INSTRUMENT/` format
- **Comprehensive logging**: Detailed logging for debugging and monitoring
- **Test mode**: Option to test with single expiry before processing all data
- **Error handling**: Robust error handling with retries and proper cleanup

## Installation

### Cross-Platform Support
✅ **Windows 10/11** (PowerShell and Command Prompt)  
✅ **macOS** (Intel and Apple Silicon)  
✅ **Linux** (Ubuntu, CentOS, etc.)

### Prerequisites
- **Python 3.7+** (recommended: Python 3.8 or higher)
- **Google Chrome browser** installed
- **Internet connection** for downloading Chrome driver

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kunalAgarwal35/manojith_nse_eod_data.git
   cd manojith_nse_eod_data
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test cross-platform compatibility** (optional but recommended):
   ```bash
   python test_cross_platform.py
   ```

4. **Chrome Browser**: Ensure Google Chrome is installed and accessible

## Usage

### Basic Usage

Run the script:
```bash
python nse_data_scraper.py
```

The script will:
1. Ask for the year you want to process
2. Ask if you want to test with a single expiry first (recommended)
3. Initialize browser session with NSE
4. Fetch all expiry dates for that year
5. Download CSV data for each expiry
6. Save files in organized folder structure

### Example

```
NSE Historical Options Chain Data Scraper
==================================================
Enter the year (e.g., 2015): 2015
Test with single expiry first? (y/n): y
```

### Folder Structure

Downloaded files are organized as:
```
nse_data/
├── 2015/
│   └── NIFTY/
│       └── FUTIDX/
│           ├── NIFTY_FUTIDX_28_MAY_2015_28_03_2015_to_29_05_2015.csv
│           ├── NIFTY_FUTIDX_25_JUN_2015_25_04_2015_to_26_06_2015.csv
│           └── ...
└── 2024/
    └── NIFTY/
        └── FUTIDX/
            └── ...
```

## Configuration Options

### Headless Mode
By default, the browser runs in visible mode for debugging. To run headlessly:
```python
scraper = NSEDataScraper(headless=True)
```

### Custom Parameters
You can modify the script to use different symbols and instruments:
```python
# For different symbols (e.g., BANKNIFTY)
scraper.process_year(2024, symbol="BANKNIFTY", instrument="FUTIDX")

# For options instead of futures
scraper.process_year(2024, symbol="NIFTY", instrument="OPTIDX")
```

## API Endpoints Used

1. **Expiry Dates**: 
   ```
   GET /api/historicalOR/meta/foCPV/expireDts?instrument=FUTIDX&symbol=NIFTY&year=2015
   ```

2. **CSV Data**: 
   ```
   GET /api/historicalOR/foCPV?from=01-02-2024&to=29-02-2024&instrumentType=FUTIDX&symbol=NIFTY&year=2024&expiryDate=29-FEB-2024&csv=true
   ```

## Important Notes

### Date Range Logic
- **Start Date**: 60 days before expiry date
- **End Date**: 1 day after expiry date
- This ensures you get complete options chain data leading up to and including expiry

### Session Management
The script properly handles NSE's session requirements by:
- Visiting the FO reports page first to establish session
- Copying all cookies from Selenium browser to requests session
- Using proper headers that match browser requests
- Adding delays between requests to avoid rate limiting

### Error Handling
- Validates API responses before saving
- Logs all errors with detailed information
- Gracefully handles network timeouts and connection issues
- Properly cleans up browser resources

### Rate Limiting
The script includes a 2-second delay between requests to be respectful to NSE servers.

## Platform-Specific Notes

### Windows
- Supports both **PowerShell** and **Command Prompt**
- Chrome driver automatically downloads as `chromedriver.exe`
- Uses Windows-specific user agent string
- Additional Windows-specific Chrome options for stability

### macOS
- Works on both **Intel** and **Apple Silicon** Macs
- Chrome driver downloads as `chromedriver` (no .exe extension)
- Uses macOS-specific user agent string
- Handles macOS security permissions automatically

### Linux
- Tested on Ubuntu, CentOS, and other major distributions
- May require additional permissions for Chrome driver execution
- Uses Linux-specific user agent string
- Supports both GUI and headless server environments

## Troubleshooting

### Cross-Platform Issues

1. **Chrome Driver Download Problems**:
   ```bash
   # Test your platform compatibility first
   python test_cross_platform.py
   ```

2. **Platform Detection Issues**:
   - The script automatically detects Windows/Mac/Linux
   - Uses appropriate Chrome driver executable (.exe on Windows)
   - Applies platform-specific user agent strings

### Common Issues

1. **Chrome Driver Issues**:
   - The script automatically downloads the correct driver for your platform
   - Ensure Chrome browser is installed and up to date
   - On Linux, you may need to install additional dependencies:
     ```bash
     # Ubuntu/Debian
     sudo apt-get update
     sudo apt-get install -y google-chrome-stable
     
     # CentOS/RHEL
     sudo yum install -y google-chrome-stable
     ```

2. **Session Initialization Failures**:
   - NSE occasionally blocks automated requests
   - Try running in non-headless mode to see what's happening
   - Check your internet connection
   - Verify Chrome is properly installed

3. **No Expiry Dates Found**:
   - Verify the year is correct
   - Some years might not have data available
   - Check NSE website manually to confirm data availability

4. **CSV Download Failures**:
   - NSE might return JSON error instead of CSV
   - This usually indicates invalid date ranges or missing data
   - Check the logs for specific error messages

5. **Permission Errors (Linux/Mac)**:
   ```bash
   # Make sure Chrome driver is executable
   chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver
   ```

6. **Chrome Browser Warnings/Errors**:
   - You might see WebGL or GCM registration errors in the console
   - These are harmless Chrome internal warnings in automated mode
   - The scraper includes options to suppress most of these warnings
   - Test silent operation:
     ```bash
     python test_silent_run.py
     ```

### Debug Mode

Run with visible browser to debug issues:
```python
scraper = NSEDataScraper(headless=False)
```

This allows you to see what the browser is doing and identify any issues with page loading or session establishment.

## Legal and Ethical Considerations

- This tool is for educational and research purposes
- Respect NSE's terms of service and rate limits
- Use the data responsibly and in compliance with applicable regulations
- The script includes reasonable delays to avoid overloading NSE servers

## Support

If you encounter issues:
1. Check the console logs for detailed error messages
2. Verify your internet connection
3. Ensure Chrome browser is up to date
4. Try running in non-headless mode for debugging

## License

This project is provided as-is for educational purposes. Users are responsible for compliance with NSE's terms of service and applicable regulations. 