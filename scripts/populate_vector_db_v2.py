"""
Script to populate ChromaDB using default embeddings (no sentence-transformers)
This version is more stable and has fewer dependencies.
"""

import os
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from vector_store import VectorStoreManager
import re
from typing import List, Dict


class DocumentProcessor:
    """Process and chunk documents for RAG"""
    
    def __init__(self, chunk_size=500, chunk_overlap=50):
        """
        Initialize document processor
        
        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def load_documents_from_directory(self, directory_path: str) -> List[Dict]:
        """
        Load all text files from a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of document dictionaries with content and metadata
        """
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Warning: Directory {directory_path} does not exist")
            return documents
        
        # Recursively find all .txt files
        for file_path in directory.rglob('*.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract category from path
                relative_path = file_path.relative_to(directory)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"
                
                documents.append({
                    'content': content,
                    'source': str(file_path),
                    'filename': file_path.name,
                    'category': category
                })
                
                print(f"✅ Loaded: {file_path.name}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        
        return documents
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Process documents into chunks with metadata
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of processed chunks with metadata
        """
        processed_chunks = []
        
        for doc in documents:
            content = doc['content']
            chunks = self.chunk_text(content)
            
            # Create chunk metadata
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'text': chunk,
                    'source': doc['source'],
                    'filename': doc['filename'],
                    'category': doc['category'],
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                })
        
        return processed_chunks


class SimpleVectorStorePopulator:
    """Populate vector store using ChromaDB's default embeddings"""
    
    def __init__(self):
        """Initialize with ChromaDB's built-in embedding function"""
        print("Initializing vector store with default embeddings...")
        self.vector_store = VectorStoreManager()
        print("✅ Vector store ready (using ChromaDB default embeddings)")
    
    def populate(self, chunks: List[Dict]):
        """
        Add chunks to vector store
        ChromaDB will automatically generate embeddings
        
        Args:
            chunks: List of processed text chunks with metadata
        """
        if not chunks:
            print("❌ No chunks to process")
            return
        
        print(f"\n📦 Processing {len(chunks)} chunks...")
        
        # Extract texts and prepare metadata
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'filename': chunk['filename'],
                'category': chunk['category'],
                'chunk_id': str(chunk['chunk_id']),
                'total_chunks': str(chunk['total_chunks'])
            }
            for chunk in chunks
        ]
        
        # Generate unique IDs
        ids = [f"{chunk['filename']}_{chunk['chunk_id']}" for chunk in chunks]
        
        # Add to vector store in batches
        # ChromaDB will automatically generate embeddings
        batch_size = 50
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        print(f"📤 Adding to vector store in {total_batches} batches...")
        print("   (ChromaDB is generating embeddings automatically)")
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            try:
                self.vector_store.collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                    # No embeddings parameter - ChromaDB generates them
                )
                
                batch_num = i // batch_size + 1
                print(f"  ✅ Batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)")
                time.sleep(0.2)  # Small delay to avoid overwhelming the system
                
            except Exception as e:
                print(f"  ❌ Error adding batch {batch_num}: {e}")
                raise
        
        print(f"\n✅ Successfully added {len(chunks)} chunks to vector store")
        print(f"📊 Total documents in collection: {self.vector_store.get_collection_count()}")


def main():
    """Main function to populate vector database"""
    
    print("=" * 70)
    print("🚀 TRAVEL CHATBOT - VECTOR DATABASE POPULATION")
    print("   (Using ChromaDB Default Embeddings)")
    print("=" * 70)
    
    # Initialize processor
    print("\n📋 Initializing document processor...")
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    print("✅ Processor ready")
    
    # Load documents from knowledge base
    knowledge_base_path = Path(__file__).parent.parent / 'knowledge_base'
    print(f"\n📂 Loading documents from: {knowledge_base_path}")
    print("-" * 70)
    
    documents = processor.load_documents_from_directory(str(knowledge_base_path))
    
    if not documents:
        print("\n❌ No documents found! Please add .txt files to knowledge_base/")
        return
    
    print("-" * 70)
    print(f"✅ Successfully loaded {len(documents)} documents")
    
    # Process into chunks
    print("\n🔪 Chunking documents...")
    print("-" * 70)
    chunks = processor.process_documents(documents)
    print("-" * 70)
    print(f"✅ Created {len(chunks)} chunks")
    
    # Show statistics
    categories = {}
    for chunk in chunks:
        cat = chunk['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Distribution by category:")
    for category, count in sorted(categories.items()):
        percentage = (count / len(chunks)) * 100
        print(f"   {category:.<30} {count:>4} chunks ({percentage:>5.1f}%)")
    
    # Populate vector store
    print("\n" + "=" * 70)
    print("🧠 POPULATING VECTOR STORE")
    print("=" * 70)
    
    try:
        populator = SimpleVectorStorePopulator()
        populator.populate(chunks)
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✅ VECTOR DATABASE POPULATION COMPLETE!")
    print("=" * 70)
    
    # Test queries
    print("\n🧪 Testing semantic search...")
    print("-" * 70)
    
    test_queries = [
        "What are the best attractions to visit in Paris?",
        "How much does a trip to Tokyo cost?",
        "What should I pack for travel?"
    ]
    
    for test_query in test_queries:
        print(f"\n📝 Query: '{test_query}'")
        try:
            results = populator.vector_store.query(test_query, n_results=2)
            
            if results and results['documents']:
                print("   Results:")
                for i, doc in enumerate(results['documents'][0], 1):
                    preview = doc[:120].replace('\n', ' ')
                    print(f"   {i}. {preview}...")
                    if results['metadatas']:
                        meta = results['metadatas'][0][i-1]
                        print(f"      📁 {meta.get('filename')} ({meta.get('category')})")
            else:
                print("   ❌ No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ ALL DONE! Your RAG system is ready to use.")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run: python scripts/test_rag.py")
    print("  2. Run: streamlit run src/app.py")
    print()


if __name__ == "__main__":
    main()
