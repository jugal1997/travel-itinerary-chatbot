import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class TravelDataAPI:
    """Fetch real-time travel data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
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
