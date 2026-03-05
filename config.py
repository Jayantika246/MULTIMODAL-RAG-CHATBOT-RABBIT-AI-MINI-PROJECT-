import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    TOP_K = 10
    MMR_K = 5
    FINAL_K = 3
    CHUNK_SIZE = 450
    CHUNK_OVERLAP = 75
    MMR_LAMBDA = 0.7  # Balance between relevance (1.0) and diversity (0.0)
    FAISS_INDEX_PATH = 'faiss_index'
    BM25_INDEX_PATH = 'bm25_index'
    RRF_K = 60  # Reciprocal Rank Fusion constant
