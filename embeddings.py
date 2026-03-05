from sentence_transformers import SentenceTransformer
from config import Config

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
    
    def encode(self, texts):
        """Generate embeddings for a list of texts"""
        return self.model.encode(texts, convert_to_numpy=True)
