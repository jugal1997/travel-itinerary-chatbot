import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from amadeus import Client, ResponseError
import os

class TravelDataAPI:
    """Fetch real-time travel data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize Amadeus client (optional - only if API keys are set)
        amadeus_key = os.getenv('AMADEUS_API_KEY')
        amadeus_secret = os.getenv('AMADEUS_API_SECRET')
        
        if amadeus_key and amadeus_secret:
            self.amadeus = Client(
                client_id=amadeus_key,
                client_secret=amadeus_secret
            )
        else:
            self.amadeus = None
            print("⚠️ Amadeus API not configured - flight search disabled")
    
    def search_flights(self, origin: str, destination: str, departure_date: str, 
                       return_date: str = None, adults: int = 1) -> Dict:
        """Search for flight offers using Amadeus API"""
        if not self.amadeus:
            return {'error': 'Amadeus API not configured'}
        
        try:
            # Search for flight offers
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                returnDate=return_date,
                adults=adults,
                max=5  # Limit to 5 results
            )
            
            # Parse results
            flights = []
            for offer in response.data[:3]:  # Top 3 offers
                price = offer['price']
                itinerary = offer['itineraries'][0]
                
                flights.append({
                    'price': f"{price['total']} {price['currency']}",
                    'carrier': itinerary['segments'][0]['carrierCode'],
                    'duration': itinerary['duration'],
                    'stops': len(itinerary['segments']) - 1
                })
            
            return {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'flights': flights,
                'count': len(flights)
            }
            
        except ResponseError as error:
            return {'error': f"Amadeus API error: {error}"}
        except Exception as e:
            return {'error': str(e)}
    
    def get_hotel_offers(self, city_code: str, check_in: str, check_out: str) -> Dict:
        """Get hotel offers using Amadeus API"""
        if not self.amadeus:
            return {'error': 'Amadeus API not configured'}
        
        try:
            # Search hotels by city
            hotels_response = self.amadeus.reference_data.locations.hotels.by_city.get(
                cityCode=city_code
            )
            
            if not hotels_response.data:
                return {'error': 'No hotels found'}
            
            # Get first few hotel IDs
            hotel_ids = [hotel['hotelId'] for hotel in hotels_response.data[:5]]
            
            # Get offers for these hotels
            offers_response = self.amadeus.shopping.hotel_offers_search.get(
                hotelIds=','.join(hotel_ids),
                checkInDate=check_in,
                checkOutDate=check_out
            )
            
            hotels = []
            for offer in offers_response.data[:3]:
                hotel_data = offer['hotel']
                price_data = offer['offers'][0]['price']
                
                hotels.append({
                    'name': hotel_data.get('name', 'Unknown'),
                    'price_per_night': f"{price_data['total']} {price_data['currency']}",
                    'rating': hotel_data.get('rating', 'N/A')
                })
            
            return {
                'city': city_code,
                'check_in': check_in,
                'check_out': check_out,
                'hotels': hotels,
                'count': len(hotels)
            }
            
        except ResponseError as error:
            return {'error': f"Amadeus API error: {error}"}
        except Exception as e:
            return {'error': str(e)}
    
    def get_weather_data(self, city: str, country_code: str = None) -> Dict:
        """Get weather data for a destination using Open-Meteo (free, no API key)"""
        try:
            # First, geocode the city
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            if country_code:
                geocode_url += f"&country_code={country_code}"
            
            geo_response = self.session.get(geocode_url, timeout=10)
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                return {'error': f'City {city} not found'}
            
            location = geo_data['results'][0]
            lat, lon = location['latitude'], location['longitude']
            
            # Get weather forecast
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
            
            weather_response = self.session.get(weather_url, timeout=10)
            weather_data = weather_response.json()
            
            return {
                'city': location['name'],
                'country': location.get('country', ''),
                'current_temp': weather_data['current']['temperature_2m'],
                'humidity': weather_data['current']['relative_humidity_2m'],
                'daily_forecast': {
                    'max_temps': weather_data['daily']['temperature_2m_max'][:7],
                    'min_temps': weather_data['daily']['temperature_2m_min'][:7],
                    'precipitation': weather_data['daily']['precipitation_sum'][:7]
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_currency_rates(self, base_currency: str = 'USD') -> Dict:
        """Get currency exchange rates (free API, no key needed)"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            return {
                'base': base_currency,
                'rates': data['rates'],
                'timestamp': data['date']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_visa_requirements(self, from_country: str, to_country: str) -> Dict:
        """Get visa requirements (simplified - you can enhance with real API)"""
        # This is a placeholder - you can integrate with real visa APIs
        visa_free_countries = {
            'India': ['Nepal', 'Bhutan', 'Maldives', 'Mauritius'],
            'USA': ['Canada', 'Mexico', 'UK', 'France', 'Germany', 'Japan'],
            'UK': ['EU countries', 'USA', 'Canada', 'Australia']
        }
        
        return {
            'from': from_country,
            'to': to_country,
            'visa_required': to_country not in visa_free_countries.get(from_country, []),
            'note': 'Please verify with official sources'
        }
    
    def get_destination_info(self, destination: str) -> Dict:
        """Get comprehensive destination information"""
        weather = self.get_weather_data(destination)
        
        return {
            'destination': destination,
            'weather': weather,
            'timestamp': datetime.now().isoformat()
        }
    
    def format_for_rag(self, data: Dict, data_type: str) -> str:
        """Format API data for RAG context"""
        if data_type == 'weather':
            if 'error' in data:
                return f"Weather data unavailable: {data['error']}"
            
            return f"""
Current Weather for {data['city']}, {data['country']}:
- Temperature: {data['current_temp']}°C
- Humidity: {data['humidity']}%
- 7-Day Forecast: Max temps {data['daily_forecast']['max_temps'][0]}-{max(data['daily_forecast']['max_temps'])}°C
"""
        
        elif data_type == 'currency':
            if 'error' in data:
                return f"Currency data unavailable: {data['error']}"
            
            common_currencies = ['EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'INR']
            rates_text = '\n'.join([
                f"- 1 {data['base']} = {data['rates'].get(curr, 'N/A')} {curr}"
                for curr in common_currencies if curr in data['rates']
            ])
            
            return f"""
Exchange Rates (Base: {data['base']}):
{rates_text}
Last updated: {data['timestamp']}
"""
        
        elif data_type == 'flights':
            if 'error' in data:
                return f"Flight data unavailable: {data['error']}"
            
            if data['count'] == 0:
                return "No flights found for this route."
            
            flights_text = '\n'.join([
                f"- {f['carrier']}: {f['price']} ({f['duration']}, {f['stops']} stops)"
                for f in data['flights']
            ])
            
            return f"""
Flight Options from {data['origin']} to {data['destination']}:
Departure: {data['departure_date']}
{flights_text}
"""
        
        elif data_type == 'hotels':
            if 'error' in data:
                return f"Hotel data unavailable: {data['error']}"
            
            if data['count'] == 0:
                return "No hotels found."
            
            hotels_text = '\n'.join([
                f"- {h['name']}: {h['price_per_night']}/night (Rating: {h['rating']})"
                for h in data['hotels']
            ])
            
            return f"""
Hotel Options in {data['city']}:
Check-in: {data['check_in']}, Check-out: {data['check_out']}
{hotels_text}
"""
        
        elif data_type == 'visa':
            visa_status = "NOT required" if not data['visa_required'] else "REQUIRED"
            return f"""
Visa Requirements:
- From: {data['from']}
- To: {data['to']}
- Visa Status: {visa_status}
- Note: {data['note']}
"""
        
        return str(data)
