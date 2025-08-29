"""
Demo flight scraper that generates sample flight data for testing purposes.
This can be used when web scraping libraries are not available or for testing.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging


class DemoFlightScraper:
    """Demo flight scraper that generates realistic sample flight data."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Sample airlines and their typical price ranges
        self.airlines = {
            'American Airlines': (200, 800),
            'Delta Air Lines': (220, 850),
            'United Airlines': (210, 820),
            'Southwest Airlines': (150, 600),
            'JetBlue Airways': (180, 700),
            'Alaska Airlines': (190, 750),
            'Spirit Airlines': (100, 400),
            'Frontier Airlines': (120, 450)
        }
        
        # Common flight durations between major cities (in minutes)
        self.flight_durations = {
            ('NYC', 'LAX'): (330, 390),  # 5.5-6.5 hours
            ('NYC', 'CHI'): (150, 180),  # 2.5-3 hours
            ('LAX', 'CHI'): (240, 280),  # 4-4.5 hours
            ('NYC', 'MIA'): (180, 220),  # 3-3.5 hours
            ('LAX', 'SEA'): (150, 180),  # 2.5-3 hours
        }
    
    def search_flights(self, source: str, destination: str, travel_date: str,
                      return_date: Optional[str] = None, passengers: int = 1,
                      flight_class: str = "economy") -> List[Dict]:
        """Generate sample flight data."""
        
        self.logger.info(f"Generating demo flights from {source} to {destination}")
        
        flights = []
        num_flights = min(self.config['search_settings']['max_results'], 8)
        
        for i in range(num_flights):
            flight = self._generate_flight(source, destination, travel_date)
            flights.append(flight)
        
        # Sort by price
        flights.sort(key=lambda x: x['price_numeric'])
        
        return flights
    
    def _generate_flight(self, source: str, destination: str, travel_date: str) -> Dict:
        """Generate a single flight with realistic data."""
        
        # Select random airline
        airline = random.choice(list(self.airlines.keys()))
        price_range = self.airlines[airline]
        
        # Generate price (add some randomness)
        base_price = random.randint(price_range[0], price_range[1])
        price_numeric = base_price + random.randint(-50, 100)
        price = f"${price_numeric}"
        
        # Generate flight duration
        route_key = (source.upper(), destination.upper())
        reverse_route_key = (destination.upper(), source.upper())
        
        if route_key in self.flight_durations:
            duration_range = self.flight_durations[route_key]
        elif reverse_route_key in self.flight_durations:
            duration_range = self.flight_durations[reverse_route_key]
        else:
            # Default duration for unknown routes
            duration_range = (120, 480)  # 2-8 hours
        
        duration_minutes = random.randint(duration_range[0], duration_range[1])
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        duration = f"{hours}h {minutes}m"
        
        # Generate departure time (between 6 AM and 10 PM)
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        
        # Calculate arrival time
        departure_dt = datetime.strptime(f"{travel_date} {departure_time}", "%Y-%m-%d %H:%M")
        arrival_dt = departure_dt + timedelta(minutes=duration_minutes)
        arrival_time = arrival_dt.strftime("%H:%M")
        
        # Add +1 day indicator if flight arrives next day
        if arrival_dt.date() > departure_dt.date():
            arrival_time += " +1"
        
        # Generate stops
        stops_options = ["Nonstop", "1 stop", "2 stops"]
        stops_weights = [0.4, 0.5, 0.1]  # Prefer nonstop and 1 stop
        stops = random.choices(stops_options, weights=stops_weights)[0]
        
        # Adjust price based on stops (nonstop is usually more expensive)
        if stops == "Nonstop":
            price_numeric += random.randint(50, 150)
        elif stops == "2 stops":
            price_numeric -= random.randint(30, 100)
        
        price = f"${price_numeric}"
        
        return {
            'airline': airline,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'duration': duration,
            'duration_minutes': duration_minutes,
            'price': price,
            'price_numeric': price_numeric,
            'stops': stops,
            'departure_airport': source.upper(),
            'arrival_airport': destination.upper(),
            'website': 'Demo Data'
        }
