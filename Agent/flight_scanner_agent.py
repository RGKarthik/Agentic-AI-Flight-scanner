import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from flight_scrapers import FlightScraperFactory
from utils import setup_logging, validate_config


class FlightScannerAgent:
    """
    Main agent class that orchestrates flight searches across multiple travel websites.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the flight scanner agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = setup_logging()
        validate_config(self.config)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{config_path}' not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def search_flights(self) -> List[Dict]:
        """
        Search for flights using the configured parameters.
        
        Returns:
            List of flight dictionaries with details
        """
        self.logger.info("Starting flight search...")
        self.logger.info(f"Source: {self.config['flight_search']['source']}")
        self.logger.info(f"Destination: {self.config['flight_search']['destination']}")
        self.logger.info(f"Date: {self.config['flight_search']['travel_date']}")
        
        all_flights = []
        websites_to_try = [self.config['websites']['primary']] + self.config['websites']['fallback']
        
        for website in websites_to_try:
            try:
                self.logger.info(f"Searching on {website}...")
                scraper = FlightScraperFactory.create_scraper(website, self.config)
                
                flights = scraper.search_flights(
                    source=self.config['flight_search']['source'],
                    destination=self.config['flight_search']['destination'],
                    travel_date=self.config['flight_search']['travel_date'],
                    return_date=self.config['flight_search'].get('return_date'),
                    passengers=self.config['flight_search']['passengers'],
                    flight_class=self.config['flight_search']['class']
                )
                
                if flights:
                    self.logger.info(f"Found {len(flights)} flights on {website}")
                    all_flights.extend(flights)
                    break  # Success, no need to try fallback sites
                    
            except Exception as e:
                self.logger.error(f"Error searching on {website}: {str(e)}")
                continue
        
        if not all_flights:
            self.logger.warning("No flights found on any website")
            return []
        
        # Sort flights based on configuration
        sort_key = self.config['search_settings'].get('sort_by', 'price')
        if sort_key == 'price':
            all_flights.sort(key=lambda x: x.get('price_numeric', float('inf')))
        elif sort_key == 'duration':
            all_flights.sort(key=lambda x: x.get('duration_minutes', float('inf')))
        elif sort_key == 'departure_time':
            all_flights.sort(key=lambda x: x.get('departure_time', ''))
        
        # Limit results
        max_results = self.config['search_settings'].get('max_results', 10)
        return all_flights[:max_results]
    
    def display_results(self, flights: List[Dict]):
        """Display flight results in a formatted way."""
        if not flights:
            print("No flights found.")
            return
        
        print(f"\n{'='*80}")
        print(f"FLIGHT SEARCH RESULTS")
        print(f"{'='*80}")
        print(f"Route: {self.config['flight_search']['source']} → {self.config['flight_search']['destination']}")
        print(f"Date: {self.config['flight_search']['travel_date']}")
        print(f"Found {len(flights)} flights")
        print(f"{'='*80}")
        
        for i, flight in enumerate(flights, 1):
            print(f"\n{i}. {flight.get('airline', 'Unknown Airline')}")
            print(f"   Departure: {flight.get('departure_time', 'N/A')} from {flight.get('departure_airport', 'N/A')}")
            print(f"   Arrival: {flight.get('arrival_time', 'N/A')} at {flight.get('arrival_airport', 'N/A')}")
            print(f"   Duration: {flight.get('duration', 'N/A')}")
            print(f"   Price: {flight.get('price', 'N/A')}")
            print(f"   Stops: {flight.get('stops', 'N/A')}")
            if flight.get('website'):
                print(f"   Source: {flight['website']}")
    
    def save_results(self, flights: List[Dict], filename: Optional[str] = None):
        """Save flight results to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flight_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'search_parameters': self.config['flight_search'],
                    'search_timestamp': datetime.now().isoformat(),
                    'flights': flights
                }, f, indent=2)
            
            self.logger.info(f"Results saved to {filename}")
            print(f"\nResults saved to: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")


def main():
    """Main function to run the flight scanner agent."""
    try:
        agent = FlightScannerAgent()
        flights = agent.search_flights()
        agent.display_results(flights)
        agent.save_results(flights)
        
    except KeyboardInterrupt:
        print("\nSearch cancelled by user.")
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
