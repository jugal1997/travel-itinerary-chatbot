"""
Vector database setup and management using ChromaDB
"""
import chromadb
from chromadb.config import Settings
import os
from pathlib import Path


class VectorStoreManager:
    """Manages ChromaDB vector store"""
    
    def __init__(self, persist_directory='data/vector_db'):
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="travel_knowledge",
            metadata={"description": "Travel information and itineraries"}
        )
        
        print(f"Vector store initialized at: {persist_directory}")
        print(f"Collection: {self.collection.name}")
        print(f"Current documents: {self.collection.count()}")
    
    def add_documents(self, documents, metadatas, ids, embeddings=None):
        """Add documents to vector store"""
        if embeddings:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        else:
            # Let ChromaDB generate embeddings
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def query(self, query_text, n_results=5):
        """Query vector store"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
    
    def get_collection_count(self):
        """Get number of documents in collection"""
        return self.collection.count()
    
    def clear_collection(self):
        """Clear all documents from collection"""
        # Delete and recreate collection
        self.client.delete_collection(name="travel_knowledge")
        self.collection = self.client.create_collection(
            name="travel_knowledge",
            metadata={"description": "Travel information and itineraries"}
        )
        print("✅ Collection cleared")
