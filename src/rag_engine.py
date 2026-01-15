"""
Retrieval-Augmented Generation engine
"""
from vector_store import VectorStoreManager
from llm_handler import LLMHandler
from prompt_templates import PromptTemplates

class RAGEngine:
    """Main RAG pipeline"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm = LLMHandler()
        self.prompts = PromptTemplates()
    
    def retrieve_context(self, query, top_k=5):
        """Retrieve relevant documents"""
        results = self.vector_store.query(query, n_results=top_k)
        
        if results and results['documents']:
            return results['documents'][0]  # Return list of documents
        return []
    
    def generate_response(self, user_query, conversation_history=None):
        """Generate response using RAG"""
        # Retrieve relevant context
        context_docs = self.retrieve_context(user_query)
        
        # Build prompt with context
        prompt = self.prompts.build_rag_prompt(
            query=user_query,
            context=context_docs,
            history=conversation_history
        )
        
        # Generate response
        response = self.llm.generate_response(prompt)
        
        return response
