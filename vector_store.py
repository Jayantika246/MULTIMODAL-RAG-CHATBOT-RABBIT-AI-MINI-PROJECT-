import faiss
import numpy as np
import pickle
import os
from config import Config

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        
    def create_index(self, embeddings, chunks):
        """Create FAISS index from embeddings and chunks (only called once)"""
        self.documents = chunks
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        print(f"Created new index with {self.index.ntotal} vectors")
    
    def add_chunks(self, embeddings, chunks):
        """Add new chunks to existing index"""
        # Create index if it doesn't exist
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Add chunks to documents list
        self.documents.extend(chunks)
        
        print(f"Added {len(chunks)} chunks. Index now has {self.index.ntotal} vectors")
    
    def search(self, query_embedding, k=Config.TOP_K):
        """Search for top k similar chunks"""
        if self.index is None:
            return []
        
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), k
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                chunk = self.documents[idx]
                results.append({
                    'text': chunk['text'],
                    'score': float(distance),
                    'metadata': chunk['metadata']
                })
        return results
    
    def save(self, path=Config.FAISS_INDEX_PATH):
        """Save index and documents to disk"""
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f'{path}/index.faiss')
        with open(f'{path}/documents.pkl', 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load(self, path=Config.FAISS_INDEX_PATH):
        """Load index and documents from disk"""
        if os.path.exists(f'{path}/index.faiss'):
            self.index = faiss.read_index(f'{path}/index.faiss')
            with open(f'{path}/documents.pkl', 'rb') as f:
                loaded_docs = pickle.load(f)
            
            # Migrate old format (plain strings) to new format (dicts with metadata)
            if loaded_docs and isinstance(loaded_docs[0], str):
                print("Migrating old document format to new chunked format...")
                self.documents = []
                for idx, doc in enumerate(loaded_docs):
                    self.documents.append({
                        'text': doc,
                        'metadata': {
                            'source_id': idx,
                            'chunk_id': 0,
                            'source_title': f'Document {idx + 1}'
                        }
                    })
                # Save migrated format
                self.save(path)
            else:
                self.documents = loaded_docs
            
            return True
        return False
