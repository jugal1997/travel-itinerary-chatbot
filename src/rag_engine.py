"""
Retrieval-Augmented Generation engine
"""
from vector_store import VectorStoreManager
from llm_handler import LLMHandler
from prompt_templates import PromptTemplates
from apis.travel_data import TravelDataAPI
import re
import os
import chromadb
from huggingface_hub import InferenceClient
from typing import List, Dict
import re
from apis.travel_data import TravelDataAPI

class RAGEngine:
    """Main RAG pipeline"""
    # Airport code mappings for common cities
    CITY_TO_AIRPORT = {
        'PAR': 'CDG',  # Paris - Charles de Gaulle
        'LON': 'LHR',  # London - Heathrow
        'NYC': 'JFK',  # New York - JFK
        'TYO': 'NRT',  # Tokyo - Narita
        'TOK': 'NRT',  # Tokyo - Narita (alternative)
        'DXB': 'DXB',  # Dubai
        'BKK': 'BKK',  # Bangkok
        'SIN': 'SIN',  # Singapore
        'HKG': 'HKG',  # Hong Kong
        'SYD': 'SYD',  # Sydney
        'MEL': 'MEL',  # Melbourne
        'LAX': 'LAX',  # Los Angeles
        'SFO': 'SFO',  # San Francisco
        'ROM': 'FCO',  # Rome - Fiumicino
        'BCN': 'BCN',  # Barcelona
        'MAD': 'MAD',  # Madrid
        'BER': 'BER',  # Berlin
        'AMS': 'AMS',  # Amsterdam
        'IST': 'IST',  # Istanbul
    }
    def __init__(self):
        """Initialize RAG engine with LLM and vector store"""
        # Initialize Hugging Face client for Llama 3.1
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
        
        self.llm_client = InferenceClient(api_key=self.api_key)
        self.model_name = "meta-llama/Llama-3.1-8B-Instruct"
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        
        # Get or create collection - SAFER METHOD
        collection_name = "travel_docs"
        existing_collections = [col.name for col in self.chroma_client.list_collections()]
        
        if collection_name in existing_collections:
            self.collection = self.chroma_client.get_collection(name=collection_name)
            print(f"✅ Loaded collection: {self.collection.count()} documents")
        else:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Travel itinerary documents"}
            )
            print("✅ Created new collection")
        
        # System prompt
        self.system_prompt = """You are an expert travel advisor AI assistant specialized in creating personalized travel itineraries.

CRITICAL INSTRUCTION - Using Real-Time Flight/Hotel Data:
When you see "✈️ REAL-TIME FLIGHT DATA:" in the context, you MUST:
1. Start your response by mentioning "I found real-time flight options for you:"
2. List ALL the flights shown with their exact prices, carriers, and durations
3. Use the EXACT data provided - do not modify prices or details
4. Present the information clearly and completely

When you see "🏨 HOTEL DATA:" in the context:
1. List ALL hotels with their exact prices and ratings
2. Use the EXACT data provided

If NO real-time data is provided:
- Say "I couldn't fetch live pricing at the moment"
- Provide general guidance only
- NEVER make up specific prices or flight details

Your role:
- Help users plan trips based on their preferences, budget, and timeframe
- Provide destination recommendations with cultural insights
- Offer practical travel advice (visas, weather, safety, packing)
- Use real-time weather and currency data when available

Always be honest about data availability and provide responsible travel advice."""


    def _extract_location_code(self, location_text: str) -> str:
        """Convert city name or code to proper airport code"""
        location = location_text.upper().strip()
        
        # If it's already a 3-letter code, check mapping
        if len(location) == 3:
            return self.CITY_TO_AIRPORT.get(location, location)
        
        # Map full city names to airport codes
        city_name_mapping = {
            'PARIS': 'CDG',
            'LONDON': 'LHR',
            'NEW YORK': 'JFK',
            'NEWYORK': 'JFK',
            'TOKYO': 'NRT',
            'DUBAI': 'DXB',
            'BANGKOK': 'BKK',
            'SINGAPORE': 'SIN',
            'HONG KONG': 'HKG',
            'HONGKONG': 'HKG',
            'SYDNEY': 'SYD',
            'MELBOURNE': 'MEL',
            'LOS ANGELES': 'LAX',
            'LOSANGELES': 'LAX',
            'SAN FRANCISCO': 'SFO',
            'SANFRANCISCO': 'SFO',
            'ROME': 'FCO',
            'BARCELONA': 'BCN',
            'MADRID': 'MAD',
            'BERLIN': 'BER',
            'AMSTERDAM': 'AMS',
            'ISTANBUL': 'IST',
            'MUMBAI': 'BOM',
            'DELHI': 'DEL',
            'NEW DELHI': 'DEL',
            'NEWDELHI': 'DEL',
        }
        
        return city_name_mapping.get(location, location[:3])  # Fallback to first 3 letters

    def retrieve_context(self, query, top_k=5):
        """Retrieve relevant documents"""
        results = self.vector_store.query(query, n_results=top_k)
        
        if results and results['documents']:
            return results['documents'][0]  # Return list of documents
        return []
    
    def generate_response(self, user_query: str, conversation_history: str = "") -> str:
        """Generate response using RAG"""
        try:
            # Get real-time data
            realtime_context = self.enhance_query_with_realtime_data(user_query)
            print(f"🐛 Real-time context length: {len(realtime_context)} chars")  # DEBUG
            if realtime_context:
                print(f"🐛 Context preview: {realtime_context[:200]}...")  # DEBUG
            # Query vector database
            results = self.collection.query(
                query_texts=[user_query],
                n_results=3
            )
            
            # Build context from retrieved documents
            context = "\n\n".join(results['documents'][0]) if results['documents'] else ""
            
            # Add real-time data to context
            if realtime_context:
                context = f"{realtime_context}\n\n{context}"
            
            # Build prompt
            prompt = self._build_prompt(user_query, context, conversation_history)
            
            # Generate response
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def enhance_query_with_realtime_data(self, user_query: str) -> str:
        """Enhance query with real-time travel data"""
        travel_api = TravelDataAPI()
        additional_context = []
        
        # Extract city names - IMPROVED PATTERN
        query_lower = user_query.lower()
        
        # Common city-related keywords
        city_keywords = ['weather', 'temperature', 'climate', 'visit', 'trip', 'travel', 'going', 'plan', 'flight', 'hotel']
        
        # Check if query mentions weather/city-related terms
        has_city_context = any(keyword in query_lower for keyword in city_keywords)
        
        # Extract cities
        cities = []
        if has_city_context:
            import re
            words = user_query.split()
            potential_cities = [word.strip('?,!.') for word in words if word and word[0].isupper() and len(word) > 2]
            skip_words = ['What', 'Where', 'When', 'How', 'Why', 'The', 'Is', 'Are', 'Can', 'Should', 'Will', 'Show', 'Tell', 'Find', 'Get', 'Book']
            cities = [city for city in potential_cities if city not in skip_words]
        
        # FLIGHT SEARCH
        if any(word in query_lower for word in ['flight', 'fly', 'flying', 'airline']):
            import re
            
            # Pattern 1: "from X to Y" with 3-letter codes
            from_to_pattern = r'(?:from\s+)?([A-Z]{3})\s+to\s+([A-Z]{3})'
            match = re.search(from_to_pattern, user_query, re.IGNORECASE)
            
            # Pattern 2: "from City to City" with full names
            if not match:
                from_to_pattern2 = r'from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+on|\s+\d)'
                match = re.search(from_to_pattern2, user_query, re.IGNORECASE)
            
            if match:
                origin = match.group(1).strip()
                destination = match.group(2).strip()
                
                # Convert to proper airport codes
                origin = self._extract_location_code(origin)
                destination = self._extract_location_code(destination)
                
                print(f"📍 Converted to airport codes: {origin} → {destination}")
                
                # Try to extract date
                date_pattern = r'(\d{4}-\d{2}-\d{2})'
                date_match = re.search(date_pattern, user_query)
                departure_date = date_match.group(1) if date_match else None
                
                if departure_date:
                    print(f"✈️ Searching flights: {origin} → {destination} on {departure_date}")
                    flight_data = travel_api.search_flights(origin, destination, departure_date)
                    
                    print(f"🐛 Flight data received: {flight_data}")
                    
                    if 'error' not in flight_data and flight_data.get('count', 0) > 0:
                        flight_context = travel_api.format_for_rag(flight_data, 'flights')
                        additional_context.append(flight_context)
                        print(f"✅ Added flight context to RAG")
                    else:
                        error_msg = flight_data.get('error') or flight_data.get('message', 'No flights found')
                        print(f"⚠️ Flight search failed: {error_msg}")
                        additional_context.append(f"Flight search attempted but no data available: {error_msg}")

        # HOTEL SEARCH
        if any(word in query_lower for word in ['hotel', 'accommodation', 'stay', 'lodging', 'resort']):
            if cities and len(cities) > 0:
                city = cities[0]
                # Try to get city code (first 3 letters uppercase)
                city_code = city[:3].upper()
                
                # Try to extract dates
                date_pattern = r'(\d{4}-\d{2}-\d{2})'
                dates = re.findall(date_pattern, user_query)
                
                if len(dates) >= 2:
                    check_in = dates[0]
                    check_out = dates[1]
                    print(f"🏨 Searching hotels in {city_code}: {check_in} to {check_out}")
                    
                    hotel_data = travel_api.get_hotel_offers(city_code, check_in, check_out)
                    
                    if 'error' not in hotel_data:
                        hotel_context = travel_api.format_for_rag(hotel_data, 'hotels')
                        additional_context.append(hotel_context)
                        print(f"✅ Found {hotel_data.get('count', 0)} hotel options")
        
        # WEATHER DATA
        if cities and any(word in query_lower for word in ['weather', 'temperature', 'climate']):
            city = cities[0]
            print(f"🌍 Detected city: {city}")
            
            weather_data = travel_api.get_weather_data(city)
            if 'error' not in weather_data:
                weather_context = travel_api.format_for_rag(weather_data, 'weather')
                additional_context.append(weather_context)
                print(f"✅ Added weather data for {city}")
        
        # CURRENCY DATA
        if any(word in query_lower for word in ['budget', 'cost', 'price', 'expensive', 'currency', 'exchange', 'money', 'dollar', 'euro']):
            currency_data = travel_api.get_currency_rates('USD')
            if 'error' not in currency_data:
                currency_context = travel_api.format_for_rag(currency_data, 'currency')
                additional_context.append(currency_context)
                print("✅ Added currency exchange data")
        
        result = '\n\n'.join(additional_context)
        if result:
            print(f"📊 Added {len(additional_context)} real-time data sources")
        return result


    def _build_prompt(self, user_query: str, context: str, conversation_history: str = "") -> str:
        """Build the final prompt for the LLM"""
        prompt = f"""Context from travel knowledge base:
{context}

"""
        
        if conversation_history:
            prompt += f"""Previous conversation:
{conversation_history}

"""
        
        prompt += f"""User question: {user_query}

Please provide a helpful, detailed response based on the context and conversation history above. If you use real-time data (weather, currency), mention it clearly."""
        
        return prompt
