import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium not installed. Web scraping functionality will be limited.")

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests or BeautifulSoup not installed. Some functionality may be limited.")


class BaseFlightScraper(ABC):
    """Base class for flight scrapers."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.timeout = config['search_settings']['timeout']
        self.retry_attempts = config['search_settings']['retry_attempts']
    
    @abstractmethod
    def search_flights(self, source: str, destination: str, travel_date: str, 
                      return_date: Optional[str] = None, passengers: int = 1,
                      flight_class: str = "economy") -> List[Dict]:
        """Search for flights and return results."""
        pass
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not installed. Please install it using: pip install selenium")
        
        options = Options()
        
        if self.config['browser_settings']['headless']:
            options.add_argument('--headless')
        
        options.add_argument(f"--window-size={','.join(map(str, self.config['browser_settings']['window_size']))}")
        options.add_argument(f"--user-agent={self.config['browser_settings']['user_agent']}")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _parse_price(self, price_text: str) -> tuple:
        """Parse price text and return (display_price, numeric_price)."""
        if not price_text:
            return "N/A", float('inf')
        
        # Remove currency symbols and extract numbers
        numeric_price = re.findall(r'[\d,]+', price_text.replace(',', ''))
        if numeric_price:
            try:
                return price_text.strip(), float(numeric_price[0])
            except (ValueError, IndexError):
                pass
        
        return price_text.strip(), float('inf')
    
    def _parse_duration(self, duration_text: str) -> tuple:
        """Parse duration text and return (display_duration, minutes)."""
        if not duration_text:
            return "N/A", float('inf')
        
        # Extract hours and minutes
        hours = re.findall(r'(\d+)h', duration_text)
        minutes = re.findall(r'(\d+)m', duration_text)
        
        total_minutes = 0
        if hours:
            total_minutes += int(hours[0]) * 60
        if minutes:
            total_minutes += int(minutes[0])
        
        return duration_text.strip(), total_minutes if total_minutes > 0 else float('inf')


class KayakScraper(BaseFlightScraper):
    """Kayak.com flight scraper."""
    
    def search_flights(self, source: str, destination: str, travel_date: str,
                      return_date: Optional[str] = None, passengers: int = 1,
                      flight_class: str = "economy") -> List[Dict]:
        """Search flights on Kayak."""
        flights = []
        driver = None
        
        try:
            driver = self._setup_driver()
            
            # Build Kayak URL
            trip_type = "roundtrip" if return_date else "oneway"
            url = f"https://www.kayak.com/flights/{source}-{destination}/{travel_date}"
            if return_date:
                url += f"/{return_date}"
            url += f"?sort=price_a&fs=stops=0;1;2"
            
            self.logger.info(f"Navigating to: {url}")
            driver.get(url)
            
            # Wait for results to load
            time.sleep(5)
            
            # Try to find flight results
            try:
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-resultid]"))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for flight results on Kayak")
                return flights
            
            # Parse flight results
            flight_elements = driver.find_elements(By.CSS_SELECTOR, "[data-resultid]")
            
            for element in flight_elements[:self.config['search_settings']['max_results']]:
                try:
                    flight_data = self._parse_kayak_flight(element, source, destination)
                    if flight_data:
                        flight_data['website'] = 'Kayak'
                        flights.append(flight_data)
                except Exception as e:
                    self.logger.error(f"Error parsing Kayak flight: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Kayak: {str(e)}")
        
        finally:
            if driver:
                driver.quit()
        
        return flights
    
    def _parse_kayak_flight(self, element, source: str = "N/A", destination: str = "N/A") -> Optional[Dict]:
        """Parse individual flight element from Kayak."""
        try:
            # Extract flight details
            airline_elem = element.find_element(By.CSS_SELECTOR, "[data-code]")
            airline = airline_elem.get_attribute("title") if airline_elem else "Unknown"
            
            # Times
            time_elements = element.find_elements(By.CSS_SELECTOR, ".vmXl .vmXl-mod-variant-large")
            departure_time = time_elements[0].text if len(time_elements) > 0 else "N/A"
            arrival_time = time_elements[1].text if len(time_elements) > 1 else "N/A"
            
            # Duration
            duration_elem = element.find_element(By.CSS_SELECTOR, ".vmXl .vmXl-mod-variant-default")
            duration, duration_minutes = self._parse_duration(duration_elem.text if duration_elem else "")
            
            # Price
            price_elem = element.find_element(By.CSS_SELECTOR, ".f8F1-price-text")
            price, price_numeric = self._parse_price(price_elem.text if price_elem else "")
            
            # Stops
            stops_elem = element.find_element(By.CSS_SELECTOR, ".JWEO")
            stops = stops_elem.text if stops_elem else "N/A"
            
            return {
                'airline': airline,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'duration': duration,
                'duration_minutes': duration_minutes,
                'price': price,
                'price_numeric': price_numeric,
                'stops': stops,
                'departure_airport': source,
                'arrival_airport': destination
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Kayak flight element: {str(e)}")
            return None


class ExpediaScraper(BaseFlightScraper):
    """Expedia.com flight scraper."""
    
    def search_flights(self, source: str, destination: str, travel_date: str,
                      return_date: Optional[str] = None, passengers: int = 1,
                      flight_class: str = "economy") -> List[Dict]:
        """Search flights on Expedia."""
        flights = []
        driver = None
        
        try:
            driver = self._setup_driver()
            
            # Navigate to Expedia
            driver.get("https://www.expedia.com/Flights")
            time.sleep(3)
            
            # Fill in search form
            self._fill_expedia_form(driver, source, destination, travel_date, return_date, passengers)
            
            # Wait for results
            try:
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='offer-listing']"))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for flight results on Expedia")
                return flights
            
            # Parse results
            flight_elements = driver.find_elements(By.CSS_SELECTOR, "[data-test-id='offer-listing']")
            
            for element in flight_elements[:self.config['search_settings']['max_results']]:
                try:
                    flight_data = self._parse_expedia_flight(element)
                    if flight_data:
                        flight_data['website'] = 'Expedia'
                        flights.append(flight_data)
                except Exception as e:
                    self.logger.error(f"Error parsing Expedia flight: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Expedia: {str(e)}")
        
        finally:
            if driver:
                driver.quit()
        
        return flights
    
    def _fill_expedia_form(self, driver, source: str, destination: str, travel_date: str,
                          return_date: Optional[str], passengers: int):
        """Fill Expedia search form."""
        try:
            # Origin
            origin_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "location-field-leg1-origin"))
            )
            origin_input.clear()
            origin_input.send_keys(source)
            time.sleep(1)
            
            # Destination
            dest_input = driver.find_element(By.ID, "location-field-leg1-destination")
            dest_input.clear()
            dest_input.send_keys(destination)
            time.sleep(1)
            
            # Departure date
            dep_date_input = driver.find_element(By.ID, "d1-btn")
            dep_date_input.click()
            # Implementation would need date picker logic
            
            # Search button
            search_btn = driver.find_element(By.ID, "search-button")
            search_btn.click()
            
        except Exception as e:
            self.logger.error(f"Error filling Expedia form: {str(e)}")
            raise
    
    def _parse_expedia_flight(self, element) -> Optional[Dict]:
        """Parse individual flight element from Expedia."""
        # Implementation similar to Kayak parser
        # This would need to be customized based on Expedia's HTML structure
        return {
            'airline': "Sample Airline",
            'departure_time': "10:00 AM",
            'arrival_time': "2:00 PM",
            'duration': "4h 0m",
            'duration_minutes': 240,
            'price': "$300",
            'price_numeric': 300,
            'stops': "Nonstop"
        }


class BookingScraper(BaseFlightScraper):
    """Booking.com flight scraper."""
    
    def search_flights(self, source: str, destination: str, travel_date: str,
                      return_date: Optional[str] = None, passengers: int = 1,
                      flight_class: str = "economy") -> List[Dict]:
        """Search flights on Booking.com."""
        # Implementation would be similar to other scrapers
        # For now, returning sample data
        return [{
            'airline': "Sample Airline",
            'departure_time': "12:00 PM",
            'arrival_time': "4:00 PM",
            'duration': "4h 0m",
            'duration_minutes': 240,
            'price': "$350",
            'price_numeric': 350,
            'stops': "1 stop",
            'website': 'Booking.com'
        }]


class FlightScraperFactory:
    """Factory class to create appropriate scraper instances."""
    
    SCRAPERS = {
        'kayak': KayakScraper,
        'expedia': ExpediaScraper,
        'booking': BookingScraper
    }
    
    @classmethod
    def create_scraper(cls, website: str, config: Dict) -> BaseFlightScraper:
        """Create a scraper instance for the specified website."""
        scraper_class = cls.SCRAPERS.get(website.lower())
        if not scraper_class:
            # If the requested scraper is not available, try using demo scraper
            if not SELENIUM_AVAILABLE:
                print(f"Selenium not available. Using demo data for {website}.")
                from demo_scraper import DemoFlightScraper
                return DemoFlightScraper(config)
            raise ValueError(f"Unsupported website: {website}")
        
        return scraper_class(config)
