"""
Travel Itinerary Chatbot - Main Streamlit Application
Interactive chat interface with RAG-powered responses
"""

import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime
import json

# Import our custom modules
from rag_engine import RAGEngine
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Travel Itinerary Chatbot",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 20%;
    }
    .message-content {
        margin-top: 0.5rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'rag_engine' not in st.session_state:
        with st.spinner("🔄 Initializing AI engine..."):
            st.session_state.rag_engine = RAGEngine()
    
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")


def display_chat_message(role, content, timestamp=None):
    """Display a chat message with styling"""
    if role == "user":
        # User message - right aligned, blue background
        st.markdown(f"""
        <div style="background-color: #E3F2FD; padding: 10px; border-radius: 10px; margin: 10px 0; margin-left: 20%; color: black;">
            <strong>👤 You</strong> {f'<small>({timestamp})</small>' if timestamp else ''}
            <div style="margin-top: 5px; color: black;">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message - left aligned, gray background
        st.markdown(f"""
        <div style="background-color: #F5F5F5; padding: 10px; border-radius: 10px; margin: 10px 0; margin-right: 20%; color: black;">
            <strong>🤖 Assistant</strong> {f'<small>({timestamp})</small>' if timestamp else ''}
            <div style="margin-top: 5px; color: black;">{content}</div>
        </div>
        """, unsafe_allow_html=True)



def get_conversation_history_text():
    """Get conversation history as formatted text for context"""
    history = []
    for msg in st.session_state.messages[-5:]:  # Last 5 messages for context
        role = msg['role'].title()
        content = msg['content']
        history.append(f"{role}: {content}")
    return history


def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<p class="main-header">🌍 Travel Itinerary Chatbot</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("💬 Chat Controls")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.experimental_rerun()
        
        # Save conversation button
        if st.button("💾 Save Conversation"):
            if st.session_state.messages:
                # TODO: Implement save to database
                st.success("✅ Conversation saved!")
            else:
                st.warning("⚠️ No conversation to save")
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Session ID", st.session_state.conversation_id)
        
        st.markdown("---")
        
        # About
        st.subheader("ℹ️ About")
        st.info("""
        This AI-powered chatbot helps you plan your travel itinerary.
        
        **Features:**
        - Destination recommendations
        - Budget planning
        - Packing advice
        - Visa information
        - Custom itineraries
        
        **Powered by:**
        - Llama 3.1 8B LLM
        - RAG for accurate info
        - ChromaDB vector store
        """)
        
                # Sample queries
        st.subheader("💡 Try Asking:")
        sample_queries = [
            "Plan a 5-day trip to Paris",
            "What's the budget for Tokyo?",
            "What should I pack for Bali?",
            "Do I need a visa for Japan?",
            "Best time to visit Paris"
        ]
        
        for query in sample_queries:
            if st.button(f"📝 {query}", key=f"sample_{query}"):
                # Add the query directly as a user message
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.messages.append({
                    'role': 'user',
                    'content': query,
                    'timestamp': timestamp
                })
                
                # Generate response immediately
                history = get_conversation_history_text()
                
                with st.spinner("🤔 Thinking..."):
                    try:
                        response = st.session_state.rag_engine.generate_response(
                            user_query=query,
                            conversation_history=history
                        )
                        
                        st.session_state.messages.append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                    except Exception as e:
                        st.session_state.messages.append({
                            'role': 'assistant',
                            'content': f"Error: {str(e)}",
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                
                st.experimental_rerun()

    
    # Main chat area
    st.subheader("💬 Conversation")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Hello! I'm your travel planning assistant. Ask me anything about travel destinations, budgets, packing, visas, or itineraries!")
        else:
            for message in st.session_state.messages:
                display_chat_message(
                    message['role'],
                    message['content'],
                    message.get('timestamp')
                )
    
    # Chat input
        # Chat input using form (more reliable)
    st.markdown("---")
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "",
            key="user_input_field",
            placeholder="Ask me about travel planning, destinations, budgets, visas..."
        )
        submit_button = st.form_submit_button("Send 🚀")
    
    # Process form submission
    if submit_button and user_input:
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # Get conversation history for context
        history = get_conversation_history_text()
        
        # Generate response with RAG
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.rag_engine.generate_response(
                    user_query=user_input,
                    conversation_history=history
                )
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
        
        # Rerun to update the chat display
        st.experimental_rerun()  # Changed from st.rerun()

    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>🌍 Travel Itinerary Chatbot | Powered by RAG & Llama 3.1 | Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
