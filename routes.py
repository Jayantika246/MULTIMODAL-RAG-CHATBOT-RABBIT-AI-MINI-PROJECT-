from flask import request, jsonify, render_template
from ingestion import IngestionService
from retrieval import RetrievalService
from llm import LLMService
from vector_store import VectorStore
from bm25_store import BM25Store
from memory import ConversationMemory
from itinerary_agent import ItineraryAgent
from multimodal_ingestion import MultimodalIngestion

# Initialize shared stores (singleton)
vector_store = VectorStore()
vector_store.load()

bm25_store = BM25Store()
bm25_store.load()

# Initialize conversation memory
conversation_memory = ConversationMemory(max_exchanges=5)

# Initialize services with shared stores
ingestion_service = IngestionService(vector_store, bm25_store)
multimodal_ingestion = MultimodalIngestion(vector_store, bm25_store)
retrieval_service = RetrievalService(vector_store, bm25_store)
llm_service = LLMService()
itinerary_agent = ItineraryAgent()

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'})

    @app.route('/ingest', methods=['POST'])
    def ingest():
        """Ingest travel documents with chunking for FAISS and BM25"""
        data = request.get_json()
        
        if not data or 'documents' not in data:
            return jsonify({'error': 'documents field is required'}), 400
        
        documents = data['documents']
        if not isinstance(documents, list):
            return jsonify({'error': 'documents must be a list'}), 400
        
        try:
            chunk_count = ingestion_service.ingest_documents(documents)
            
            # Debug: print index sizes
            print(f"FAISS index: {vector_store.index.ntotal} vectors")
            print(f"BM25 index: {len(bm25_store.documents)} documents")
            
            return jsonify({
                'status': 'success',
                'documents_ingested': len(documents),
                'chunks_created': chunk_count,
                'total_vectors': vector_store.index.ntotal
            })
        except Exception as e:
            print(f"Ingestion error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/query', methods=['POST'])
    def query():
        """Query the RAG system with hybrid retrieval, conversational memory, and itinerary generation"""
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'question field is required'}), 400
        
        question = data['question']
        session_id = data.get('session_id')
        
        # Generate new session ID if not provided
        if not session_id:
            session_id = conversation_memory.generate_session_id()
        
        try:
            # Debug: print index sizes
            print(f"FAISS: {vector_store.index.ntotal if vector_store.index else 0} vectors")
            print(f"BM25: {len(bm25_store.documents)} documents")
            
            # Retrieve relevant chunks using hybrid retrieval
            retrieved_chunks = retrieval_service.retrieve(question)
            
            print(f"Retrieved {len(retrieved_chunks)} chunks via hybrid retrieval")
            
            # Get conversation history
            chat_history = conversation_memory.format_history(session_id)
            
            # Check if this is an itinerary request
            if itinerary_agent.is_itinerary_query(question):
                print("Detected itinerary query - using Itinerary Agent")
                
                # Generate itinerary
                itinerary_data = itinerary_agent.generate_itinerary(
                    question, 
                    retrieved_chunks, 
                    chat_history
                )
                
                # Format response
                response = itinerary_agent.format_itinerary_response(
                    itinerary_data, 
                    retrieved_chunks
                )
                
                # Save exchange to memory
                conversation_memory.add_exchange(session_id, question, response['answer'])
                
                response['session_id'] = session_id
                return jsonify(response)
            
            else:
                # Regular Q&A flow
                answer = llm_service.generate_response(question, retrieved_chunks, chat_history)
                
                # Save exchange to memory
                conversation_memory.add_exchange(session_id, question, answer)
                
                # Format response
                response_data = {
                    'answer': answer,
                    'session_id': session_id,
                    'response_type': 'Q&A',
                    'retrieval_type': 'Hybrid (FAISS + BM25 + RRF)',
                    'retrieved_sources': [
                        {
                            'text': chunk['text'],
                            'score': chunk['score'],
                            'metadata': chunk['metadata']
                        }
                        for chunk in retrieved_chunks
                    ]
                }
                
                return jsonify(response_data)
                
        except Exception as e:
            print(f"Query error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/clear_session', methods=['POST'])
    def clear_session():
        """Clear conversation history for a session"""
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id:
            conversation_memory.clear_session(session_id)
            return jsonify({'status': 'success', 'message': 'Session cleared'})
        
        return jsonify({'error': 'session_id required'}), 400
    
    @app.route('/upload_pdf', methods=['POST'])
    def upload_pdf():
        """Upload and process PDF document"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        try:
            print(f"Uploading PDF: {file.filename}")
            pdf_bytes = file.read()
            
            # Process PDF
            result = multimodal_ingestion.ingest_pdf(pdf_bytes, file.filename)
            
            print(f"PDF processed successfully: {result}")
            
            return jsonify({
                'status': 'success',
                'filename': file.filename,
                'chunks_created': result['chunks_created'],
                'pages': result['pages'],
                'title': result['title'],
                'characters': result['characters'],
                'message': f"Successfully processed {file.filename}"
            })
        except Exception as e:
            print(f"PDF upload error: {str(e)}")
            return jsonify({'error': str(e), 'status': 'failed'}), 500
    
    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        """Upload image with user-provided caption"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        caption = request.form.get('caption', '').strip()
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not caption:
            return jsonify({'error': 'Caption is required. Please describe the image.'}), 400
        
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Only image files are allowed (JPG, PNG, GIF, BMP, WEBP)'}), 400
        
        try:
            print(f"Uploading image: {file.filename} with caption: {caption}")
            image_bytes = file.read()
            
            # Process image with caption
            result = multimodal_ingestion.ingest_image_with_caption(
                image_bytes, 
                file.filename, 
                caption
            )
            
            print(f"Image processed successfully: {result}")
            
            return jsonify({
                'status': 'success',
                'filename': file.filename,
                'chunks_created': result['chunks_created'],
                'title': result['title'],
                'caption': result['caption'],
                'image_url': result['image_url'],
                'dimensions': f"{result['width']}x{result['height']}",
                'format': result['format'],
                'message': f"Successfully processed {file.filename}"
            })
        except Exception as e:
            print(f"Image upload error: {str(e)}")
            return jsonify({'error': str(e), 'status': 'failed'}), 500

