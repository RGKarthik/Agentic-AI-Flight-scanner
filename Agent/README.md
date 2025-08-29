# Agentic AI Flight Scanner

An intelligent flight scanning agent that searches multiple travel websites to find the best flight deals based on your preferences. The agent uses configurable parameters and can scrape various travel websites to provide comprehensive flight information.

## Features

- 🔍 **Multi-Website Search**: Searches across multiple travel websites (Kayak, Expedia, Booking.com)
- ⚙️ **Configurable Parameters**: All search parameters stored in a configuration file
- 🤖 **Intelligent Fallback**: Automatically tries alternative websites if primary fails
- 📊 **Smart Sorting**: Sort results by price, duration, or departure time
- 💾 **Data Export**: Save results to JSON format for further analysis
- 🖥️ **Headless Browser**: Runs in background without opening browser windows
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- 🎯 **Demo Mode**: Test functionality with realistic sample data

## Project Structure

```
Agent/
├── config.json                 # Configuration file with search parameters
├── flight_scanner_agent.py     # Main agent orchestrator
├── flight_scrapers.py          # Web scraping implementations
├── demo_scraper.py             # Demo data generator for testing
├── utils.py                    # Utility functions and validation
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── logs/                       # Log files (created automatically)
```

## Installation

1. **Clone or download the project**
   ```bash
   cd "c:\Users\karrg\Agentic-AI-Flight-scanner\Agent"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome browser** (required for web scraping)
   - Download and install Google Chrome from https://www.google.com/chrome/

## Configuration

Edit the `config.json` file to customize your search parameters:

```json
{
  "flight_search": {
    "source": "NYC",           // Origin airport/city
    "destination": "LAX",      // Destination airport/city
    "travel_date": "2025-09-15", // Departure date (YYYY-MM-DD)
    "return_date": null,       // Return date (null for one-way)
    "passengers": 1,           // Number of passengers
    "class": "economy"         // Flight class
  },
  "websites": {
    "primary": "kayak",        // Primary website to search
    "fallback": ["expedia", "booking"] // Backup websites
  },
  "search_settings": {
    "max_results": 10,         // Maximum number of results
    "timeout": 30,             // Timeout in seconds
    "retry_attempts": 3,       // Number of retry attempts
    "sort_by": "price"         // Sort by: price, duration, departure_time
  },
  "browser_settings": {
    "headless": true,          // Run browser in background
    "window_size": [1920, 1080], // Browser window size
    "user_agent": "Mozilla/5.0..." // Browser user agent
  }
}
```

### Supported Airport Codes

You can use either 3-letter airport codes or city names:

- **Airport Codes**: NYC, LAX, CHI, MIA, SFO, SEA, BOS, etc.
- **City Names**: New York, Los Angeles, Chicago, Miami, etc.

### Supported Websites

- **kayak**: Kayak.com
- **expedia**: Expedia.com  
- **booking**: Booking.com

## Usage

### Basic Usage

```bash
python flight_scanner_agent.py
```

This will:
1. Load configuration from `config.json`
2. Search for flights using the configured parameters
3. Display results in the terminal
4. Save results to a timestamped JSON file

### Example Output

```
================================================================================
FLIGHT SEARCH RESULTS
================================================================================
Route: NYC → LAX
Date: 2025-09-15
Found 8 flights
================================================================================

1. Southwest Airlines
   Departure: 08:30 from NYC
   Arrival: 11:45 at LAX
   Duration: 5h 15m
   Price: $245
   Stops: Nonstop
   Source: Demo Data

2. American Airlines
   Departure: 14:15 from NYC
   Arrival: 17:30 at LAX
   Duration: 5h 15m
   Price: $298
   Stops: Nonstop
   Source: Demo Data
```

## Demo Mode

If you don't have the required dependencies installed or want to test the functionality, the agent will automatically use demo mode with realistic sample data.

To test demo mode:
```bash
python demo_scraper.py
```

## Logging

The agent creates detailed logs in the `logs/` directory:
- Filename format: `flight_scanner_YYYYMMDD.log`
- Includes timestamps, error messages, and search progress
- Useful for debugging and monitoring agent performance

## Troubleshooting

### Common Issues

1. **"Selenium not installed" error**
   ```bash
   pip install selenium webdriver-manager
   ```

2. **Chrome driver issues**
   - Ensure Google Chrome is installed
   - The webdriver-manager will automatically download the correct ChromeDriver

3. **No flights found**
   - Check your internet connection
   - Verify airport codes are correct
   - Try different date ranges
   - Check if websites are accessible

4. **Import errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version (3.7+ recommended)

### Debug Mode

To run with detailed debugging:
1. Edit `config.json` and set `"headless": false` to see browser actions
2. Check log files in the `logs/` directory
3. Use demo mode to test without external dependencies

## Customization

### Adding New Websites

1. Create a new scraper class in `flight_scrapers.py`:
   ```python
   class NewWebsiteScraper(BaseFlightScraper):
       def search_flights(self, ...):
           # Implementation here
           pass
   ```

2. Add to the factory:
   ```python
   SCRAPERS = {
       'newwebsite': NewWebsiteScraper,
       # ... existing scrapers
   }
   ```

### Modifying Search Parameters

Edit the `config.json` file to change:
- Search destinations and dates
- Number of passengers
- Sort preferences
- Browser behavior
- Timeout settings

## API Reference

### FlightScannerAgent

Main agent class that orchestrates flight searches.

**Methods:**
- `search_flights()`: Perform flight search
- `display_results(flights)`: Display formatted results
- `save_results(flights, filename)`: Save results to file

### BaseFlightScraper

Abstract base class for website scrapers.

**Methods:**
- `search_flights()`: Abstract method for flight search
- `_setup_driver()`: Setup Selenium WebDriver
- `_parse_price()`: Parse price text
- `_parse_duration()`: Parse duration text

## Data Format

Flight results are returned as dictionaries with the following structure:

```python
{
    'airline': str,           # Airline name
    'departure_time': str,    # Departure time (HH:MM)
    'arrival_time': str,      # Arrival time (HH:MM)
    'duration': str,          # Flight duration (Xh Ym)
    'duration_minutes': int,  # Duration in minutes
    'price': str,             # Formatted price ($XXX)
    'price_numeric': float,   # Numeric price for sorting
    'stops': str,             # Number of stops
    'departure_airport': str, # Origin airport
    'arrival_airport': str,   # Destination airport
    'website': str            # Source website
}
```

## License

This project is provided as-is for educational and personal use. Please respect the terms of service of the websites being scraped and use responsibly.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the flight scanner agent.

## Disclaimer

This tool is for educational purposes. Always verify flight information and prices on the official airline or travel website before making any bookings. The developers are not responsible for any inaccuracies in the scraped data.
