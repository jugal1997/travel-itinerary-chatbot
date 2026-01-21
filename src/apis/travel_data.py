import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from amadeus import Client, ResponseError
import os

class TravelDataAPI:
    """Fetch real-time travel data from various sources"""
    # Common airline code to name mapping
    AIRLINE_NAMES = {
        '6E': 'IndiGo', 'AI': 'Air India', 'UK': 'Vistara', 'SG': 'SpiceJet',
        'EK': 'Emirates', 'QR': 'Qatar Airways', 'EY': 'Etihad Airways',
        'BA': 'British Airways', 'LH': 'Lufthansa', 'AF': 'Air France',
        'KL': 'KLM', 'LX': 'Swiss', 'OS': 'Austrian Airlines',
        'TK': 'Turkish Airlines', 'SQ': 'Singapore Airlines', 'CX': 'Cathay Pacific',
        'QF': 'Qantas', 'NH': 'ANA', 'JL': 'Japan Airlines',
        'AA': 'American Airlines', 'UA': 'United Airlines', 'DL': 'Delta',
        'AC': 'Air Canada', 'VS': 'Virgin Atlantic',
        'UL': 'SriLankan Airlines', 'VJ': 'VietJet Air', 'W2': 'FlexFlight',
        'KU': 'Kuwait Airways', '9W': 'Jet Airways', 'G8': 'Go Air',
        'FZ': 'flydubai', 'WY': 'Oman Air', 'MS': 'EgyptAir',
        'TG': 'Thai Airways', 'MH': 'Malaysia Airlines', 'GA': 'Garuda Indonesia',
    }
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
    def _get_airline_name(self, code: str) -> str:
        """Get full airline name from IATA code"""
        airline_name = self.AIRLINE_NAMES.get(code, None)
        if airline_name:
            return f"{airline_name} ({code})"
        return code  # Return code if name not found


    def search_flights(self, origin: str, destination: str, departure_date: str, 
                       return_date: str = None, adults: int = 1) -> Dict:
        """Search for flight offers using Amadeus API"""
        if not self.amadeus:
            return {'error': 'Amadeus API not configured'}
        
        try:
            print(f"🔍 Amadeus API call parameters:")
            print(f"   Origin: {origin}")
            print(f"   Destination: {destination}")
            print(f"   Departure: {departure_date}")
            print(f"   Adults: {adults}")
            
            # Search for flight offers
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                max=5
            )
            
            if not response.data:
                return {
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'flights': [],
                    'count': 0,
                    'message': 'No flights found for this route/date'
                }
            
            # Parse results
            flights = []
            for offer in response.data[:3]:
                price = offer['price']
                itinerary = offer['itineraries'][0]
                first_segment = itinerary['segments'][0]
                carrier_code = first_segment['carrierCode']
                
                flights.append({
                    'price': f"{price['total']} {price['currency']}",
                    'carrier': carrier_code,
                    'carrier_name': self._get_airline_name(carrier_code),  # Add full name
                    'duration': self._format_duration(itinerary['duration']),
                    'stops': len(itinerary['segments']) - 1,
                    'departure': first_segment['departure']['at'],
                    'arrival': itinerary['segments'][-1]['arrival']['at']
                })

            
            print(f"✅ Amadeus returned {len(flights)} flight options")
            
            return {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'flights': flights,
                'count': len(flights)
            }
            
        except ResponseError as error:
            print(f"❌ Amadeus ResponseError:")
            print(f"   Status Code: {error.response.status_code}")
            print(f"   Response: {error.response.result}")
            
            # Try to extract error details
            try:
                error_body = error.response.result
                if 'errors' in error_body:
                    for err in error_body['errors']:
                        print(f"   Error: {err.get('title', 'Unknown')} - {err.get('detail', '')}")
            except:
                pass
            
            return {'error': f"Amadeus API error: Status {error.response.status_code}"}
        except Exception as e:
            print(f"❌ Flight search exception: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

    def _format_duration(self, duration: str) -> str:
        """Convert ISO 8601 duration (PT14H15M) to readable format (14h 15m)"""
        import re
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        
        result = []
        if hours:
            result.append(f"{hours.group(1)}h")
        if minutes:
            result.append(f"{minutes.group(1)}m")
        
        return ' '.join(result) if result else duration

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
            
            if data.get('count', 0) == 0:
                message = data.get('message', 'No flights found')
                return f"Flight search from {data['origin']} to {data['destination']}: {message}"
            
            flights_text = '\n'.join([
                f"{i+1}. **{f['carrier_name']}** - €{f['price'].split()[0]}\n"
                f"   Duration: {f['duration']} ({f['stops']} stop{'s' if f['stops'] != 1 else ''})\n"
                f"   Departure: {f['departure'][:16].replace('T', ' at ')}\n"
                f"   Arrival: {f['arrival'][:16].replace('T', ' at ')}"
                for i, f in enumerate(data['flights'])
            ])
            
            return f"""
✈️ REAL-TIME FLIGHT DATA:
Route: {data['origin']} → {data['destination']}
Date: {data['departure_date']}
Found {data['count']} available flights:

{flights_text}

Prices shown are in Euros. Book directly with airlines or travel booking sites for confirmation.
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
