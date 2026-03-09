# 🌴 AI Travel Planner - Advanced RAG System

A comprehensive multimodal RAG (Retrieval-Augmented Generation) travel chatbot with intelligent itinerary generation, conversational memory, and hybrid retrieval capabilities.

## ✨ Features

### 🎯 Core RAG Capabilities
- **Hybrid Retrieval System**: FAISS vector search + BM25 sparse retrieval with Reciprocal Rank Fusion (RRF)
- **Semantic Search**: HuggingFace embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- **Smart Chunking**: Overlapping chunks for better context preservation
- **Conversational Memory**: Session-based chat history (stores last 5 exchanges)
- **Source Citations**: Transparent retrieval with confidence scores

### 🗺️ Complete Travel Package Generation
- **✈️ Flight Recommendations**: Cost estimates, airlines, and duration
- **🏨 Hotel Suggestions**: Budget/mid-range/luxury options with amenities and ratings
- **🚗 Transportation Planning**: Airport transfers and local transport options
- **📅 Themed Daily Itineraries**: Adventure, Heritage, Beach, Nightlife, Relaxation days
- **🍽️ Meal Recommendations**: Breakfast, lunch, and dinner suggestions
- **💰 Complete Cost Breakdown**: Flights, accommodation, activities, meals, and transport

### 📄 Multimodal Document Support
- **PDF Upload**: Extract and index travel guides, brochures, itineraries
- **Image Upload with Captions**: Upload photos with descriptions for visual references
- **Text Input**: Direct text document ingestion
- **Automatic Processing**: Smart chunking and indexing

### 🎤 User Experience
- **Voice Input**: Hands-free interaction using Web Speech API (works on localhost)
- **Modern UI**: Travel-themed design with glassmorphism effects
- **Real-time Chat**: Instant responses with loading indicators
- **Session Persistence**: Chat history saved in localStorage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd travelrag
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📖 Usage

### Adding Travel Documents

**1. Upload PDF**
- Click "📄 Upload PDF"
- Select travel guide, brochure, or itinerary
- System extracts and indexes text automatically

**2. Upload Image with Caption**
- Click "🖼️ Upload Image"
- Select image (beach, landmark, menu, map)
- Provide detailed description
- Example: "Palolem Beach in South Goa with white sand, palm trees, and calm waters perfect for swimming and kayaking"

**3. Add Text Directly**
- Type or paste travel information
- One document per line
- Click "Add Text Documents"

### Asking Questions

**Simple Queries:**
- "What are the best beaches in Goa?"
- "Tell me about Fort Aguada"
- "Where can I find authentic Goan food?"

**Itinerary Requests:**
- "Plan a 5-day trip to Goa"
- "Create a 3-day itinerary for Goa with a budget of ₹30000"
- "Plan a week-long adventure trip to Goa"

**Image-Based Queries:**
- Upload beach image with caption
- Ask: "Plan activities around this beach"
- Ask: "What can I do at this location?"

### Voice Input

1. Click the "🎤 Voice" button
2. Allow microphone access when prompted
3. Speak your question
4. Text appears automatically in the input box

**Note**: Voice input requires HTTPS or localhost. Use `http://localhost:5000` instead of IP address.

## 🏗️ Architecture

### Backend Components

```
app.py                      # Flask application entry point
routes.py                   # API endpoints and request handling
config.py                   # Configuration management

RAG Pipeline:
├── embeddings.py          # HuggingFace embedding service
├── vector_store.py        # FAISS vector database
├── bm25_store.py          # BM25 sparse retrieval
├── retrieval.py           # Hybrid retrieval with RRF
├── chunking.py            # Document chunking strategies
└── ingestion.py           # Text document ingestion

LLM & Agents:
├── llm.py                 # Groq LLM integration
├── itinerary_agent.py     # Complete travel package generator
└── memory.py              # Conversational memory

Multimodal Processing:
├── multimodal_ingestion.py # PDF and image ingestion orchestrator
├── pdf_processor.py        # PDF text extraction (PyPDF2)
└── image_handler.py        # Image storage and caption processing

Frontend:
├── templates/index.html    # Main UI
├── static/script.js        # Client-side logic
└── static/style.css        # Travel-themed styling
```

### Key Technologies

- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Embeddings**: HuggingFace sentence-transformers
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Sparse Retrieval**: BM25 (Okapi BM25)
- **PDF Processing**: PyPDF2
- **Image Processing**: Pillow (PIL)
- **Web Framework**: Flask
- **Frontend**: Vanilla JavaScript with Web Speech API

## 🎨 Features in Detail

### Hybrid Retrieval System

The system uses a sophisticated two-stage retrieval:

1. **FAISS Vector Search**: Semantic similarity using embeddings
2. **BM25 Keyword Search**: Traditional keyword matching
3. **Reciprocal Rank Fusion (RRF)**: Combines both results intelligently

This ensures both semantic understanding and exact keyword matches.

### Intelligent Itinerary Generation

The itinerary agent creates comprehensive travel packages with:

- **Themed Days**: Each day has a clear theme (Adventure, Heritage, Beach, etc.)
- **Geographical Clustering**: Activities grouped by location to minimize travel
- **Energy Flow**: Morning (active) → Afternoon (moderate) → Evening (relaxed)
- **Variety**: Mix of adventure, culture, nightlife, and relaxation
- **Realistic Timing**: Practical schedules with buffer time
- **Complete Logistics**: Flights, hotels, transport, and meals

### Session Management

- Each user gets a unique session ID
- Chat history persists across page refreshes
- Last 5 exchanges stored for context
- Clear chat option to start fresh

### Image Upload with Captions

Instead of unreliable OCR or vision models, the system uses user-provided captions:

1. User uploads image
2. User describes the image in detail
3. System creates searchable document from caption
4. Image becomes queryable through RAG system

This approach is more reliable and gives users control over how images are indexed.

## 📊 API Endpoints

### POST `/ingest`
Ingest text documents
```json
{
  "documents": ["Document 1 text", "Document 2 text"]
}
```

### POST `/query`
Query the RAG system
```json
{
  "question": "What are the best beaches?",
  "session_id": "optional-session-id"
}
```

### POST `/upload_pdf`
Upload PDF document
- Form data with `file` field
- Returns chunks created and metadata

### POST `/upload_image`
Upload image with caption
- Form data with `file` and `caption` fields
- Returns image URL and chunks created

### POST `/clear_session`
Clear conversation history
```json
{
  "session_id": "session-id-to-clear"
}
```

## 💡 Tips for Best Results

### Writing Good Captions
❌ Bad: "beach"
✅ Good: "Palolem Beach in South Goa with white sand, palm trees, calm blue waters, perfect for swimming and kayaking"

### Asking for Itineraries
- Specify number of days: "5-day trip"
- Include budget: "with a budget of ₹50000"
- Mention preferences: "adventure-focused" or "relaxing beach vacation"

### Using Voice Input
- Speak clearly and at normal pace
- Use localhost URL (not IP address)
- Allow microphone permissions when prompted

## 🔧 Configuration

### Environment Variables (.env)
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Customization
- Chunk size: Edit `chunking.py`
- Retrieval count: Edit `retrieval.py`
- Memory size: Edit `memory.py` (default: 5 exchanges)
- Itinerary themes: Edit `itinerary_agent.py`

## 📦 Dependencies

```
flask
groq
sentence-transformers
faiss-cpu
rank-bm25
PyPDF2
Pillow
python-dotenv
numpy
```

## 🚨 Troubleshooting

### Voice Input Not Working
- Use `http://localhost:5000` instead of IP address
- Check browser microphone permissions
- Supported browsers: Chrome, Edge, Safari

### PDF Upload Fails
- Check file size (max 10MB)
- Ensure PDF contains extractable text (not scanned images)

### Image Upload Issues
- Provide detailed captions (minimum 10 words recommended)
- Supported formats: JPG, PNG, GIF, BMP, WEBP
- Max file size: 5MB

### No Results for Queries
- Add more documents to the system
- Try different phrasings
- Check if documents were successfully ingested

## 🎯 Future Enhancements

- [ ] CSV/Excel upload for structured data
- [ ] URL scraping for travel websites
- [ ] YouTube transcript extraction
- [ ] Multi-language support
- [ ] Export itineraries to PDF
- [ ] Integration with booking APIs
- [ ] Weather information
- [ ] Currency conversion

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 💬 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ for travelers by travelers**
