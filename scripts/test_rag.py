"""
Test RAG retrieval and response generation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from vector_store import VectorStoreManager
from llm_handler import LLMHandler
from prompt_templates import PromptTemplates


def test_retrieval():
    """Test vector store retrieval only"""
    print("=" * 70)
    print("🔍 TESTING VECTOR STORE RETRIEVAL")
    print("=" * 70)
    
    vector_store = VectorStoreManager()
    
    # Test queries
    test_queries = [
        "What are the best places to visit in Paris?",
        "How much does a trip to Tokyo cost?",
        "What should I pack for a beach vacation?",
        "Do I need a visa for Japan?",
        "Suggest a 5-day itinerary for Paris"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        results = vector_store.query(query, n_results=3)
        
        if results and results['documents']:
            print("\n   ✅ Retrieved chunks:")
            for i, doc in enumerate(results['documents'][0], 1):
                preview = doc[:150].replace('\n', ' ')
                print(f"   {i}. {preview}...")
                if results['metadatas']:
                    metadata = results['metadatas'][0][i-1]
                    print(f"      📁 Source: {metadata.get('filename')} | Category: {metadata.get('category')}")
        else:
            print("   ❌ No results found")
        
        print("-" * 70)


def test_rag_response():
    """Test full RAG response generation"""
    print("\n" + "=" * 70)
    print("🤖 TESTING FULL RAG RESPONSE GENERATION")
    print("=" * 70)
    
    vector_store = VectorStoreManager()
    llm = LLMHandler()
    prompts = PromptTemplates()
    
    # Test query
    query = "What are the top 3 must-see attractions in Paris with their costs?"
    
    print(f"\n📝 User Query: {query}")
    
    # Retrieve context
    print("\n🔍 Retrieving relevant context...")
    results = vector_store.query(query, n_results=5)
    
    if not results or not results['documents']:
        print("❌ No context retrieved")
        return
    
    context_docs = results['documents'][0]
    print(f"✅ Retrieved {len(context_docs)} relevant chunks")
    
    # Preview retrieved context
    print("\n📄 Context Preview:")
    for i, doc in enumerate(context_docs[:2], 1):
        preview = doc[:100].replace('\n', ' ')
        print(f"   {i}. {preview}...")
    
    # Build prompt
    print("\n📝 Building RAG prompt...")
    prompt = prompts.build_rag_prompt(
        query=query,
        context=context_docs,
        history=None
    )
    print("✅ Prompt built with context")
    
    # Generate response
    print("\n🤖 Generating response with LLM...")
    print("   (Please wait 10-30 seconds...)")
    
    try:
        response = llm.generate_response(prompt, max_tokens=500)
        
        print("\n" + "=" * 70)
        print("💬 AI RESPONSE:")
        print("=" * 70)
        print(response)
        print("=" * 70)
        
        # Quality check
        print("\n📊 Quality Check:")
        keywords = ['Eiffel', 'Louvre', 'Arc', '€', 'euro', 'cost']
        found = [kw for kw in keywords if kw.lower() in response.lower()]
        
        if found:
            print(f"✅ Response includes: {', '.join(found)}")
            print("✅ RAG system working correctly!")
        else:
            print("⚠️  Expected keywords not found in response")
        
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        print("   Check your .env file has HUGGINGFACE_API_KEY set correctly")


def main():
    """Run all tests"""
    
    print("\n" + "=" * 70)
    print("🧪 RAG SYSTEM TESTING SUITE")
    print("=" * 70)
    
    # Test 1: Retrieval only
    test_retrieval()
    
    # Test 2: Full RAG pipeline
    print("\n\n")
    try:
        test_rag_response()
    except Exception as e:
        print(f"\n❌ Error in RAG response test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ TESTING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
