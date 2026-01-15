"""
Vector database setup and management using ChromaDB
"""
import chromadb
from chromadb.config import Settings
import os

class VectorStoreManager:
    """Manages ChromaDB vector store"""
    
    def __init__(self, persist_directory='data/vector_db'):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="travel_knowledge",
            metadata={"description": "Travel information and itineraries"}
        )
    
    def add_documents(self, documents, metadatas, ids):
        """Add documents to vector store"""
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
