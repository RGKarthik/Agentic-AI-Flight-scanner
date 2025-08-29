import logging
import os
from datetime import datetime
from typing import Dict


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(f"logs/flight_scanner_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def validate_config(config: Dict) -> None:
    """Validate configuration parameters."""
    required_keys = [
        'flight_search',
        'websites',
        'search_settings',
        'browser_settings'
    ]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Validate flight search parameters
    flight_search = config['flight_search']
    required_flight_keys = ['source', 'destination', 'travel_date']
    
    for key in required_flight_keys:
        if key not in flight_search or not flight_search[key]:
            raise ValueError(f"Missing required flight search parameter: {key}")
    
    # Validate date format
    try:
        datetime.strptime(flight_search['travel_date'], '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid travel_date format. Use YYYY-MM-DD")
    
    # Validate return date if provided
    if flight_search.get('return_date'):
        try:
            datetime.strptime(flight_search['return_date'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid return_date format. Use YYYY-MM-DD")
    
    # Validate websites
    if 'primary' not in config['websites']:
        raise ValueError("Missing primary website in configuration")
    
    supported_websites = ['kayak', 'expedia', 'booking']
    if config['websites']['primary'] not in supported_websites:
        raise ValueError(f"Unsupported primary website. Supported: {supported_websites}")


def format_airport_code(code: str) -> str:
    """Format airport code to uppercase 3-letter format."""
    if not code:
        raise ValueError("Airport code cannot be empty")
    
    code = code.strip().upper()
    
    # If it's a city name, return as is (the scraper will handle it)
    if len(code) > 3:
        return code
    
    # If it's already a 3-letter code
    if len(code) == 3 and code.isalpha():
        return code
    
    return code


def get_airport_mapping() -> Dict[str, str]:
    """Return a mapping of common city names to airport codes."""
    return {
        'NEW YORK': 'NYC',
        'LOS ANGELES': 'LAX',
        'CHICAGO': 'CHI',
        'MIAMI': 'MIA',
        'SAN FRANCISCO': 'SFO',
        'SEATTLE': 'SEA',
        'BOSTON': 'BOS',
        'WASHINGTON': 'WAS',
        'ATLANTA': 'ATL',
        'DENVER': 'DEN',
        'DALLAS': 'DFW',
        'HOUSTON': 'HOU',
        'PHOENIX': 'PHX',
        'LAS VEGAS': 'LAS',
        'ORLANDO': 'MCO'
    }
