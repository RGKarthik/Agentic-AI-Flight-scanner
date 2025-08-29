#!/usr/bin/env python3
"""
Simple runner script that gracefully handles missing dependencies 
by falling back to demo mode.
"""

import sys
import json
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def run_with_demo_fallback():
    """Run flight scanner with automatic fallback to demo mode."""
    
    print("🛫 Agentic AI Flight Scanner")
    print("=" * 50)
    
    try:
        # Try to import and run the main agent
        from flight_scanner_agent import FlightScannerAgent
        
        print("🔍 Starting flight search...")
        agent = FlightScannerAgent()
        flights = agent.search_flights()
        agent.display_results(flights)
        agent.save_results(flights)
        
    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("📊 Falling back to demo mode with sample data...")
        print()
        
        # Fallback to demo mode
        try:
            from demo_scraper import DemoFlightScraper
            from utils import setup_logging
            
            # Load config
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Setup logging
            setup_logging()
            
            # Run demo scraper
            scraper = DemoFlightScraper(config)
            flights = scraper.search_flights(
                source=config['flight_search']['source'],
                destination=config['flight_search']['destination'],
                travel_date=config['flight_search']['travel_date']
            )
            
            # Display results
            print(f"\n{'='*80}")
            print(f"DEMO FLIGHT SEARCH RESULTS")
            print(f"{'='*80}")
            print(f"Route: {config['flight_search']['source']} → {config['flight_search']['destination']}")
            print(f"Date: {config['flight_search']['travel_date']}")
            print(f"Found {len(flights)} sample flights")
            print(f"{'='*80}")
            
            for i, flight in enumerate(flights, 1):
                print(f"\n{i}. {flight.get('airline', 'Unknown Airline')}")
                print(f"   Departure: {flight.get('departure_time', 'N/A')} from {flight.get('departure_airport', 'N/A')}")
                print(f"   Arrival: {flight.get('arrival_time', 'N/A')} at {flight.get('arrival_airport', 'N/A')}")
                print(f"   Duration: {flight.get('duration', 'N/A')}")
                print(f"   Price: {flight.get('price', 'N/A')}")
                print(f"   Stops: {flight.get('stops', 'N/A')}")
                print(f"   Source: {flight['website']}")
            
            print(f"\n📋 Note: This is demo data for testing purposes.")
            print(f"💡 To use real data, install dependencies: pip install -r requirements.txt")
            
        except Exception as demo_error:
            print(f"❌ Error in demo mode: {demo_error}")
            print("🔧 Please check your configuration and try again.")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("🔧 Please check the logs and configuration.")


if __name__ == "__main__":
    try:
        run_with_demo_fallback()
    except KeyboardInterrupt:
        print("\n\n👋 Search cancelled by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
