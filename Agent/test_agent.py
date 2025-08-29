#!/usr/bin/env python3
"""
Test script to verify the flight scanner agent functionality.
"""

import json
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from demo_scraper import DemoFlightScraper
    from utils import setup_logging, validate_config
    print("✓ All core modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def test_config_loading():
    """Test configuration file loading and validation."""
    print("\n--- Testing Configuration ---")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ Configuration file loaded successfully")
        
        validate_config(config)
        print("✓ Configuration validation passed")
        
        return config
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return None


def test_demo_scraper(config):
    """Test the demo flight scraper."""
    print("\n--- Testing Demo Scraper ---")
    
    try:
        scraper = DemoFlightScraper(config)
        print("✓ Demo scraper initialized successfully")
        
        flights = scraper.search_flights(
            source=config['flight_search']['source'],
            destination=config['flight_search']['destination'],
            travel_date=config['flight_search']['travel_date']
        )
        
        print(f"✓ Generated {len(flights)} demo flights")
        
        if flights:
            print("\nSample flight data:")
            flight = flights[0]
            print(f"  Airline: {flight['airline']}")
            print(f"  Route: {flight['departure_airport']} → {flight['arrival_airport']}")
            print(f"  Time: {flight['departure_time']} - {flight['arrival_time']}")
            print(f"  Duration: {flight['duration']}")
            print(f"  Price: {flight['price']}")
            print(f"  Stops: {flight['stops']}")
        
        return True
    except Exception as e:
        print(f"✗ Demo scraper error: {e}")
        return False


def test_logging():
    """Test logging functionality."""
    print("\n--- Testing Logging ---")
    
    try:
        logger = setup_logging()
        logger.info("Test log message")
        print("✓ Logging system initialized successfully")
        
        # Check if logs directory was created
        if os.path.exists('logs'):
            print("✓ Logs directory created")
        else:
            print("? Logs directory not found (may be created on first use)")
        
        return True
    except Exception as e:
        print(f"✗ Logging error: {e}")
        return False


def test_main_agent():
    """Test main flight scanner agent."""
    print("\n--- Testing Main Agent ---")
    
    try:
        from flight_scanner_agent import FlightScannerAgent
        
        agent = FlightScannerAgent()
        print("✓ Flight scanner agent initialized successfully")
        
        # Test with demo data (don't actually scrape websites)
        print("✓ Agent ready for flight searches")
        
        return True
    except Exception as e:
        print(f"✗ Main agent error: {e}")
        return False


def main():
    """Run all tests."""
    print("===============================================")
    print("    Agentic AI Flight Scanner - Test Suite")
    print("===============================================")
    
    tests_passed = 0
    total_tests = 4
    
    # Test configuration
    config = test_config_loading()
    if config:
        tests_passed += 1
    
    # Test logging
    if test_logging():
        tests_passed += 1
    
    # Test demo scraper
    if config and test_demo_scraper(config):
        tests_passed += 1
    
    # Test main agent
    if test_main_agent():
        tests_passed += 1
    
    # Summary
    print(f"\n--- Test Summary ---")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! The flight scanner is ready to use.")
        print("\nTo run the agent:")
        print("  python flight_scanner_agent.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
        if tests_passed >= 2:
            print("\n💡 You can still use demo mode:")
            print("  python demo_scraper.py")
    
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
