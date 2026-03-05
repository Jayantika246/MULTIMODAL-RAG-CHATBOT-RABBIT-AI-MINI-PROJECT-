# MULTIMODAL RAG TRAVEL CHATBOT

A comprehensive multimodal RAG (Retrieval-Augmented Generation) travel chatbot using Flask, Groq API, HuggingFace embeddings, FAISS vector store, and BM25 hybrid retrieval.

## Features

- Hybrid retrieval (FAISS + BM25 with Reciprocal Rank Fusion)
- Conversational memory with session management
- Premium itinerary generation with budget optimization
- Multimodal support (PDF, images with OCR)
- Voice input capability
- Modern travel-themed UI

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Install Tesseract OCR for image text extraction:

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`
- The app will work without Tesseract, but image OCR will be unavailable

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_api_key_here
```

## Run

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## Usage

1. Upload travel documents (PDF or images) or add text directly
2. Ask questions about destinations, attractions, or request itineraries
3. Use voice input for hands-free interaction
4. Get personalized travel recommendations with budget estimates

## Architecture

### Core Components
- `app.py` - Flask application entry point
- `routes.py` - API endpoints and request handling
- `config.py` - Configuration management

### RAG Pipeline
- `rag_pipeline.py` - Main RAG orchestration
- `embeddings.py` - HuggingFace embedding service
- `vector_store.py` - FAISS vector database
- `bm25_store.py` - BM25 sparse retrieval
- `retrieval.py` - Hybrid retrieval with RRF
- `chunking.py` - Document chunking strategies

### LLM & Agents
- `llm.py` / `llm_service.py` - Groq LLM integration
- `itinerary_agent.py` - Premium itinerary generation
- `vision_agent.py` - Landmark detection
- `memory.py` - Conversational memory

### Multimodal Processing
- `ingestion.py` - Text document ingestion
- `multimodal_ingestion.py` - PDF and image ingestion
- `pdf_processor.py` - PDF text extraction
- `image_processor.py` - OCR text extraction (optional Tesseract)

### Frontend
- `templates/index.html` - Main UI
- `static/script.js` - Client-side logic
- `static/style.css` - Travel-themed styling

## Notes

- Image OCR requires Tesseract installation (optional)
- Without Tesseract, images can still be uploaded but text extraction will be limited
- All prices are in Indian Rupees (₹)
