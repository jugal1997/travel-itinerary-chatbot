"""
Prompt templates for different tasks
"""


class PromptTemplates:
    """Manages prompt templates"""
    
    @staticmethod
    def build_rag_prompt(query, context, history=None):
        """
        Build RAG prompt with context
        
        Args:
            query: User's question
            context: List of retrieved context chunks
            history: Optional conversation history
            
        Returns:
            Formatted prompt string
        """
        # Combine context chunks
        if context and len(context) > 0:
            context_str = "\n\n".join([f"[Context {i+1}]\n{chunk}" for i, chunk in enumerate(context)])
        else:
            context_str = "No specific context available."
        
        # Build conversation history if provided
        history_str = ""
        if history and len(history) > 0:
            history_str = "Previous conversation:\n" + "\n".join(history[-5:]) + "\n\n"
        
        # Construct the complete prompt
        prompt = f"""You are a helpful and knowledgeable travel planning assistant. Your role is to provide accurate, detailed travel advice based on the information provided in the context below.

CONTEXT INFORMATION:
{context_str}

{history_str}USER QUESTION:
{query}

INSTRUCTIONS:
- Answer the user's question using ONLY the information provided in the context above
- Be specific and include relevant details like prices, locations, and recommendations from the context
- If the context doesn't contain enough information to fully answer the question, say so
- Format your response in a clear, organized way
- Be helpful and friendly

YOUR RESPONSE:"""
        
        return prompt
    
    @staticmethod
    def build_simple_prompt(query):
        """Build a simple prompt without RAG context"""
        return f"""You are a helpful travel planning assistant. Answer this question:

{query}

Provide a helpful, accurate response."""
    
    @staticmethod
    def build_itinerary_prompt(destination, days, budget, preferences=None):
        """Build prompt for itinerary generation"""
        pref_str = f"\n- Preferences: {preferences}" if preferences else ""
        
        return f"""Create a detailed {days}-day travel itinerary for {destination}.

Requirements:
- Budget: ${budget}{pref_str}
- Include daily activities, estimated costs, and practical tips
- Format as a day-by-day breakdown

Generate the itinerary:"""
