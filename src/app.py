"""
Main Streamlit application for Travel Itinerary Chatbot
"""
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Travel Itinerary Chatbot",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    st.title("🌍 Travel Itinerary Chatbot")
    st.write("Welcome! This chatbot helps you plan your travel itinerary.")
    
    # Placeholder for future functionality
    st.info("🚧 Application under development...")
    
    # Test environment variables
    if os.getenv("HUGGINGFACE_API_KEY"):
        st.success("✅ Environment variables loaded successfully")
    else:
        st.warning("⚠️ Please configure your .env file")

if __name__ == "__main__":
    main()
