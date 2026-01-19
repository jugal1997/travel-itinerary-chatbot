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
        
Your role:
- Help users plan trips based on their preferences, budget, and timeframe
- Provide destination recommendations with cultural insights
- Suggest activities, accommodations, and dining options
- Offer practical travel advice (visas, weather, safety, packing)
- Create day-by-day itineraries when requested

Guidelines:
- Be friendly, enthusiastic, and informative
- Ask clarifying questions when needed
- Provide specific, actionable recommendations
- Include real-time data when available (weather, currency)
- Cite sources when using retrieved information
- Be honest if you don't have current information

Always prioritize user safety and provide responsible travel advice."""

    
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
        
        # Extract city names (simple pattern matching)
        # Common patterns: "to Paris", "in Tokyo", "visit London"
        city_pattern = r'\b(?:to|in|visit|visiting|plan.*trip.*to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        matches = re.findall(city_pattern, user_query)
        
        if matches:
            city = matches[0]
            
            # Get weather data
            weather_data = travel_api.get_weather_data(city)
            weather_context = travel_api.format_for_rag(weather_data, 'weather')
            additional_context.append(weather_context)
        
        # If query mentions budget or cost
        if any(word in user_query.lower() for word in ['budget', 'cost', 'price', 'expensive']):
            currency_data = travel_api.get_currency_rates('USD')
            currency_context = travel_api.format_for_rag(currency_data, 'currency')
            additional_context.append(currency_context)
        
        return '\n\n'.join(additional_context)
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
