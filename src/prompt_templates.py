"""
Prompt templates for different tasks
"""

class PromptTemplates:
    """Manages prompt templates"""
    
    @staticmethod
    def build_rag_prompt(query, context, history=None):
        """Build RAG prompt with context"""
        context_str = "\n\n".join(context) if context else "No specific context available."
        
        history_str = ""
        if history:
            history_str = "Previous conversation:\n" + "\n".join(history[-5:]) + "\n\n"
        
        prompt = f"""You are a helpful travel planning assistant. Use the provided context to answer the user's question accurately.

Context:
{context_str}

{history_str}User Question: {query}

Provide a helpful, accurate response based on the context. If the context doesn't contain relevant information, use your general knowledge but mention that explicitly."""
