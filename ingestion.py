from embeddings import EmbeddingService
from chunking import DocumentChunker

class IngestionService:
    def __init__(self, vector_store, bm25_store):
        self.chunker = DocumentChunker(chunk_size=450, overlap=75)
        self.embedding_service = EmbeddingService()
        self.vector_store = vector_store
        self.bm25_store = bm25_store
    
    def ingest_documents(self, documents):
        """
        Ingest documents with chunking and embedding for both FAISS and BM25
        Returns number of chunks created
        """
        # Chunk documents
        chunks = self.chunker.chunk_documents(documents)
        
        # Extract text for embedding
        chunk_texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings for FAISS
        embeddings = self.embedding_service.encode(chunk_texts)
        
        # Add to FAISS vector database
        self.vector_store.add_chunks(embeddings, chunks)
        self.vector_store.save()
        
        # Add to BM25 index
        self.bm25_store.add_chunks(chunks)
        self.bm25_store.save()
        
        return len(chunks)
