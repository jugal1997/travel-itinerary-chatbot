"""
Script to populate ChromaDB vector store with travel knowledge base documents.
Handles document loading, chunking, embedding, and storage.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from vector_store import VectorStoreManager
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict
import re

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
                
                # Extract category from path (destinations, travel_tips, etc.)
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
        
        Uses sentence-aware chunking to avoid breaking mid-sentence.
        Based on best practices for RAG applications.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous chunk
                # Take last few sentences for context
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


class VectorStorePopulator:
    """Populate vector store with embedded documents"""
    
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2'):
        """
        Initialize populator with embedding model
        
        Args:
            embedding_model_name: Name of sentence-transformers model
        """
        print(f"Loading embedding model: {embedding_model_name}...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.vector_store = VectorStoreManager()
        print("✅ Embedding model loaded")
    
    def populate(self, chunks: List[Dict]):
        """
        Embed chunks and add to vector store
        
        Args:
            chunks: List of processed text chunks with metadata
        """
        if not chunks:
            print("No chunks to process")
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
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Add to vector store in batches (ChromaDB has batch size limits)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size].tolist()
            
            self.vector_store.collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids,
                embeddings=batch_embeddings
            )
            
            print(f"✅ Added batch {i//batch_size + 1} ({len(batch_texts)} chunks)")
        
        print(f"\n✅ Successfully added {len(chunks)} chunks to vector store")
        print(f"📊 Total documents in collection: {self.vector_store.get_collection_count()}")


def main():
    """Main function to populate vector database"""
    
    print("=" * 60)
    print("🚀 POPULATING VECTOR DATABASE")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    
    # Load documents from knowledge base
    knowledge_base_path = Path(__file__).parent.parent / 'knowledge_base'
    print(f"\n📂 Loading documents from: {knowledge_base_path}")
    
    documents = processor.load_documents_from_directory(str(knowledge_base_path))
    
    if not documents:
        print("\n❌ No documents found! Please add documents to knowledge_base/ directory")
        return
    
    print(f"\n✅ Loaded {len(documents)} documents")
    
    # Process into chunks
    print("\n🔪 Chunking documents...")
    chunks = processor.process_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")
    
    # Show statistics
    categories = {}
    for chunk in chunks:
        cat = chunk['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Chunks by category:")
    for category, count in categories.items():
        print(f"  - {category}: {count} chunks")
    
    # Populate vector store
    print("\n" + "=" * 60)
    populator = VectorStorePopulator()
    populator.populate(chunks)
    
    print("\n" + "=" * 60)
    print("✅ VECTOR DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    
    # Test query
    print("\n🧪 Testing semantic search...")
    test_query = "What are the best attractions to visit in Paris?"
    results = populator.vector_store.query(test_query, n_results=3)
    
    if results and results['documents']:
        print(f"\nQuery: '{test_query}'")
        print("\nTop 3 results:")
        for i, doc in enumerate(results['documents'][0], 1):
            print(f"\n{i}. {doc[:200]}...")
            if results['metadatas']:
                print(f"   Source: {results['metadatas'][0][i-1].get('filename', 'Unknown')}")
    
    print("\n✅ All done! Your RAG system is ready.")


if __name__ == "__main__":
    main()
