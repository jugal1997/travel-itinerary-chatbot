# 🌍 Travel Itinerary Chatbot

An AI-powered travel planning assistant that provides personalized itineraries, real-time flight prices, weather data, and expert travel advice using RAG (Retrieval-Augmented Generation) architecture.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Data Flow](#data-flow)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Project Overview

The Travel Itinerary Chatbot is an intelligent assistant designed to help users plan their trips with real-time data and AI-powered recommendations. Built using a Retrieval-Augmented Generation (RAG) architecture, it combines the reasoning capabilities of Large Language Models with up-to-date travel information from multiple APIs [web:32][web:35].

### Purpose

- Simplify travel planning with conversational AI
- Provide accurate, real-time flight and hotel pricing
- Offer personalized recommendations based on user preferences
- Deliver contextual travel advice (weather, currency, visas, packing)

### Target Users

- Individual travelers planning vacations
- Travel enthusiasts seeking destination insights
- Budget-conscious travelers comparing options
- First-time international travelers needing guidance

---

## ✨ Key Features

### Core Functionality

- **🤖 AI-Powered Chat Interface**: Natural conversation flow using Llama 3.1 8B model via Hugging Face
- **📚 RAG Architecture**: Combines vector database (ChromaDB) with 20+ curated travel documents for context-aware responses
- **💬 Multi-Turn Conversations**: Maintains chat history for contextual follow-up questions

### Real-Time Data Integration

- **✈️ Flight Search**: Live flight prices, carriers, durations, and stops via Amadeus API
- **🏨 Hotel Search**: Real-time hotel availability and pricing
- **🌤️ Weather Data**: Current conditions and 7-day forecasts for destinations (Open-Meteo API)
- **💱 Currency Exchange**: Live exchange rates for 160+ currencies (ExchangeRate-API)
- **🛂 Visa Requirements**: Basic visa information framework with official source recommendations

### Smart Features

- **🗺️ Airport Code Mapping**: Automatically converts city names (e.g., "Tokyo") to airport codes (NRT)
- **✈️ Airline Recognition**: Displays full airline names instead of cryptic codes (e.g., "Emirates (EK)")
- **📊 Budget Calculations**: Uses real-time currency data for accurate cost estimates
- **🎯 Sample Queries**: Quick-start buttons for common travel questions

### User Experience

- **💾 Export Chat**: Download conversation history as text file
- **📈 Session Stats**: Track message count and conversation ID
- **🎨 Clean UI**: Streamlit-based responsive interface
- **⚠️ Transparent Disclaimers**: Clear notices about data approximation and limitations

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                        │
│  (User Interface, Chat Display, Session Management)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG Engine (Core Logic)                    │
│  ├─ Query Processing & Context Enhancement                   │
│  ├─ LLM Integration (Llama 3.1 via Hugging Face)            │
│  └─ Response Generation & Formatting                         │
└────┬────────────────────┬──────────────────┬────────────────┘
     │                    │                  │
     ▼                    ▼                  ▼
┌──────────┐    ┌─────────────────┐   ┌─────────────────────┐
│ ChromaDB │    │  Travel Data    │   │   Database Layer    │
│ Vector   │    │   API Module    │   │  (SQLite)           │
│  Store   │    │                 │   │                     │
│          │    │  ├─ Amadeus    │   │  ├─ Conversations   │
│ 20+ Docs │    │  ├─ Open-Meteo │   │  ├─ User Prefs      │
│          │    │  └─ Exchange   │   │  └─ Session Data    │
└──────────┘    └────────┬────────┘   └─────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   External APIs      │
              │  ├─ Amadeus (Flights)│
              │  ├─ Open-Meteo       │
              │  └─ ExchangeRate-API │
              └──────────────────────┘
```

### Architecture Components [web:37]

#### 1. **Presentation Layer** (Streamlit)
- Handles user interactions and chat display
- Manages session state and conversation history
- Provides export and save functionality
- Renders real-time data visualizations

#### 2. **Application Layer** (RAG Engine)
- **Query Enhancement**: Detects destinations, dates, and intent
- **Context Retrieval**: Queries ChromaDB for relevant travel documents
- **Real-Time Integration**: Fetches live data from APIs
- **LLM Processing**: Sends enriched context to Llama 3.1 model
- **Response Formatting**: Structures AI output for presentation

#### 3. **Data Layer**
- **Vector Database (ChromaDB)**: Stores embeddings of travel documents
- **Relational Database (SQLite)**: Persists conversations and user data
- **API Cache**: Temporary storage for API responses

#### 4. **External Services**
- **Amadeus API**: Flight and hotel data
- **Open-Meteo API**: Weather information
- **ExchangeRate-API**: Currency rates
- **Hugging Face Inference**: LLM hosting

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Core development language |
| **LLM** | Llama 3.1 8B (Hugging Face) | Natural language understanding and generation |
| **Vector Database** | ChromaDB | Semantic search over travel documents |
| **UI Framework** | Streamlit | Interactive web interface |
| **Database** | SQLite | Conversation persistence |

### Key Libraries

```python
# AI & ML
huggingface-hub==0.20.0      # LLM inference client
chromadb==0.4.22             # Vector database
sentence-transformers         # Text embeddings

# APIs & Data
amadeus==8.1.0               # Flight/hotel search
requests==2.31.0             # HTTP client
python-dotenv==1.0.0         # Environment management

# Web Framework
streamlit==1.28.0            # UI framework

# Utilities
sqlite3                       # Built-in database
json                          # Data serialization
```

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 500 MB free space
- **Internet**: Stable connection for API calls

### API Keys Required
- **Hugging Face API Key** (free tier available)
- **Amadeus API Key & Secret** (free test environment)
- **Optional**: Pexels API Key (for image features)

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/travel-itinerary-chatbot.git
cd travel-itinerary-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required
HUGGINGFACE_API_KEY=your_huggingface_key_here
AMADEUS_API_KEY=your_amadeus_key_here
AMADEUS_API_SECRET=your_amadeus_secret_here

# Optional
PEXELS_API_KEY=your_pexels_key_here
```

### 5. Populate Vector Database

```bash
python src/populate_vector_db.py
```

Expected output:
```
Adding 20 documents to vector database...
✅ Successfully added 20 documents to the database!
```

---

## ⚙️ Configuration

### API Setup Instructions [web:32]

#### Hugging Face
1. Sign up at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token with "Read" permission
4. Copy to `.env` file

#### Amadeus
1. Register at https://developers.amadeus.com
2. Create a new app in "Self-Service" workspace
3. Copy API Key and API Secret
4. Add to `.env` file

#### Pexels (Optional)
1. Visit https://www.pexels.com/api
2. Click "Get Started" and sign up
3. Create an API application
4. Copy API key to `.env`

---

## 🚀 Usage

### Start the Application

```bash
streamlit run src/app.py
```

The app will open in your default browser at `http://localhost:8501`

### Example Queries

**Flight Search:**
```
Show me flights from DEL to CDG on 2026-03-15
```

**Hotel Search:**
```
Find hotels in Paris from 2026-03-15 to 2026-03-20
```

**Weather & Planning:**
```
What's the weather like in Tokyo? Best time to visit?
```

**Budget & Currency:**
```
What's the budget for a 5-day trip to London? Currency rates?
```

**General Advice:**
```
What should I pack for a winter trip to Paris?
```

---

## 📁 Project Structure

```
travel-itinerary-chatbot/
│
├── src/
│   ├── app.py                      # Main Streamlit application
│   ├── rag_engine.py               # Core RAG logic and LLM integration
│   ├── database.py                 # SQLite database manager
│   ├── populate_vector_db.py       # Script to populate ChromaDB
│   │
│   └── apis/
│       ├── __init__.py
│       ├── travel_data.py          # Amadeus, weather, currency APIs
│       └── image_service.py        # Pexels image integration (optional)
│
├── data/
│   ├── chroma_db/                  # ChromaDB vector store
│   └── user_data.db                # SQLite conversation database
│
├── .env                            # Environment variables (not in repo)
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🔌 API Integration

### Amadeus API [web:11]

**Endpoints Used:**
- `shopping.flight-offers-search` - Real-time flight prices
- `shopping.hotel-offers-search` - Hotel availability
- `reference-data.locations` - Airport/city lookup

**Rate Limits (Free Tier):**
- 2,000 API calls per month
- 10 queries per second

### Open-Meteo API [web:16]

**Features:**
- No API key required
- Unlimited free access
- 7-day weather forecasts
- Historical data available

### ExchangeRate-API [web:20]

**Features:**
- 1,500 requests/month (free)
- 160+ currencies
- Daily updates

---

## 🔄 Data Flow

### Query Processing Pipeline

```
User Input
    │
    ▼
1. Query Analysis (detect cities, dates, intent)
    │
    ▼
2. Real-Time Data Fetch (flights, weather, currency)
    │
    ▼
3. Vector Search (retrieve relevant travel docs from ChromaDB)
    │
    ▼
4. Context Assembly (combine real-time data + retrieved docs)
    │
    ▼
5. LLM Prompt Construction (structured prompt with context)
    │
    ▼
6. Llama 3.1 Generation (AI reasoning and response)
    │
    ▼
7. Response Formatting (display in chat UI)
    │
    ▼
User Output
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Add docstrings to functions
- Include type hints where applicable

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Collection not found" error**
```bash
# Solution: Reinitialize vector database
python src/populate_vector_db.py
```

**Issue: "Amadeus API 400 error"**
- Check airport codes are valid (use NRT for Tokyo, not TOK)
- Verify date format is YYYY-MM-DD
- Ensure date is not too far in future (< 330 days)

**Issue: Weather data slightly off**
- This is normal - different sources update at different times
- Data is approximate and sufficient for travel planning

---

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Visual destination images (Pexels integration)
- [ ] Interactive maps with route visualization
- [ ] PDF itinerary export
- [ ] User authentication and saved trips
- [ ] Budget calculator with detailed breakdown
- [ ] Multi-turn itinerary builder
- [ ] Integration with booking platforms
- [ ] Mobile-responsive PWA version

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📧 Contact

**Developer:** Jugal Patel  

**GitHub:**  https://github.com/jugal1997

**LinkedIn:** https://www.linkedin.com/in/jugal-patel-30a230190/

---

## 🙏 Acknowledgments

- **Amadeus** for travel API access
- **Open-Meteo** for free weather data
- **Hugging Face** for LLM hosting
- **Streamlit** for the amazing UI framework

---

**⭐ If you find this project helpful, please star the repository!**
