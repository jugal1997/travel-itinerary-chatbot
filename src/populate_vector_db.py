import os
from rag_engine import RAGEngine

def populate_travel_database():
    """Add travel documents to ChromaDB"""
    
    # Initialize RAG engine
    rag = RAGEngine()
    
    # Sample travel documents
    travel_docs = [
        # Destinations
        "Paris, France: Known for the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, and French cuisine. Best time to visit is April-June or September-October. Average budget: $150-300/day. Popular activities include visiting museums, Seine river cruise, Montmartre exploration, and café culture.",
        
        "Tokyo, Japan: A blend of traditional temples and modern technology. Famous for cherry blossoms in spring (March-April), Mount Fuji views, sushi and ramen, anime culture, and shopping districts like Shibuya and Harajuku. Budget: $100-250/day. Visit temples early morning to avoid crowds.",
        
        "Bali, Indonesia: Tropical paradise with beaches, rice terraces, and Hindu temples. Popular areas: Ubud (culture), Seminyak (beaches), Canggu (surfing). Best time: April-October (dry season). Budget: $50-150/day. Activities: temple visits, yoga retreats, snorkeling, rice terrace tours.",
        
        "New York City, USA: The Big Apple offers Times Square, Central Park, Statue of Liberty, Broadway shows, and diverse cuisine. Best visited in spring (April-June) or fall (September-November). Budget: $200-400/day. Must-do: Broadway show, Central Park walk, Brooklyn Bridge.",
        
        "Dubai, UAE: Luxury destination with Burj Khalifa (world's tallest building), desert safaris, gold souks, and beach resorts. Best time: November-March (cooler weather). Budget: $150-500/day. Activities: desert safari, mall shopping, beach clubs, skydiving.",
        
        "London, UK: Historic city with Big Ben, British Museum, Tower of London, and royal palaces. Year-round destination, though July-August is warmest. Budget: $150-350/day. Free museums, afternoon tea culture, theatre in West End.",
        
        "Bangkok, Thailand: Street food paradise with temples, floating markets, and nightlife. Visit November-February for cooler weather. Budget: $40-100/day. Must-see: Grand Palace, Wat Pho, weekend markets, Chao Phraya River, street food tours.",
        
        # Travel Tips
        "Packing essentials for international travel: Valid passport (6+ months validity), appropriate visas, travel insurance, copies of documents, universal adapter, basic first-aid kit, comfortable walking shoes, weather-appropriate clothing, portable charger.",
        
        "Budget travel tips: Book flights 2-3 months in advance, use public transportation, stay in hostels or Airbnb, eat local street food, visit free attractions, travel during shoulder season, use travel rewards credit cards.",
        
        "Safety tips: Research destination safety, register with embassy, keep valuables secure, avoid showing expensive items, stay in well-lit areas at night, keep emergency contacts handy, purchase travel insurance, make copies of important documents.",
        
        # Visa Information
        "Visa requirements for popular destinations: Schengen visa covers 27 European countries (90 days). Japan offers visa-free entry for many countries (90 days). USA requires ESTA for visa waiver countries. Always check official embassy websites for current requirements.",
        
        "Indian passport holders: Need visa for USA, UK, Schengen, Australia, Canada. Visa-free/on-arrival: Thailand, Indonesia, Maldives, Mauritius, Nepal, Bhutan, Sri Lanka. E-visa available for: Turkey, Vietnam, Kenya, Myanmar.",
        
        # Best Times to Visit
        "Europe: Best visited April-June (spring) or September-October (fall) - pleasant weather, fewer crowds, moderate prices. Summer (July-August) is peak season with higher prices and crowds. Winter offers Christmas markets but cold weather.",
        
        "Southeast Asia: Best time is November-February (dry season, cooler). March-May is hot. June-October is monsoon season with heavy rains, but also lower prices and fewer tourists.",
        
        # Specific Activities
        "Adventure activities: Scuba diving in Maldives (year-round), skiing in Swiss Alps (December-March), safari in Kenya (July-October), hiking Machu Picchu Peru (May-September), Northern Lights in Iceland (September-March).",
        
        "Food experiences: Street food tours in Bangkok, wine tasting in Tuscany Italy, sushi courses in Tokyo, tapas crawl in Barcelona Spain, cooking classes in Chiang Mai Thailand, food markets in Morocco.",
        
        # Transportation
        "Getting around cities: Metro systems in Paris, London, Tokyo, NYC are efficient. Tuk-tuks in Thailand, rickshaws in India. Uber/Grab available in most major cities. Rent bicycles in Amsterdam, Copenhagen. Consider city tourist passes for unlimited transport.",
        
        # Accommodation
        "Accommodation options: Luxury hotels ($200-500+/night), mid-range hotels ($80-200), budget hotels/hostels ($20-80), Airbnb apartments (varies), homestays ($15-50). Book directly for better rates, check cancellation policies, read recent reviews.",
        
        # Health
        "Travel health: Get vaccinations 4-6 weeks before travel. Pack prescription medications in original containers. Drink bottled water in developing countries. Purchase travel health insurance. Know location of hospitals. Bring hand sanitizer and basic medicines.",
        
        # Cultural Tips
        "Cultural etiquette: Research local customs. Dress modestly in temples/mosques. Learn basic phrases in local language. Respect local traditions. Tip appropriately (15-20% in USA, not expected in Japan). Remove shoes when entering homes in Asia."
    ]
    
    # Generate IDs for documents
    doc_ids = [f"travel_doc_{i}" for i in range(len(travel_docs))]
    
    # Add to ChromaDB
    print(f"Adding {len(travel_docs)} documents to vector database...")
    
    rag.collection.add(
        documents=travel_docs,
        ids=doc_ids
    )
    
    print(f"✅ Successfully added {rag.collection.count()} documents to the database!")
    
    # Test retrieval
    print("\n--- Testing Retrieval ---")
    test_query = "What should I pack for a trip to Paris?"
    results = rag.collection.query(
        query_texts=[test_query],
        n_results=2
    )
    
    print(f"\nQuery: {test_query}")
    print(f"Retrieved {len(results['documents'][0])} relevant documents:")
    for i, doc in enumerate(results['documents'][0], 1):
        print(f"\n{i}. {doc[:200]}...")

if __name__ == "__main__":
    populate_travel_database()
