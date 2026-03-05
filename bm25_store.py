from rank_bm25 import BM25Okapi
import pickle
import os
from config import Config

class BM25Store:
    def __init__(self):
        self.bm25 = None
        self.documents = []
        self.tokenized_corpus = []
    
    def create_index(self, chunks):
        """Create BM25 index from text chunks"""
        self.documents = chunks
        
        # Tokenize documents for BM25
        self.tokenized_corpus = [
            self._tokenize(chunk['text']) 
            for chunk in chunks
        ]
        
        # Create BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print(f"Created BM25 index with {len(self.documents)} documents")
    
    def add_chunks(self, chunks):
        """Add new chunks to existing BM25 index"""
        if self.bm25 is None:
            self.create_index(chunks)
            return
        
        # Add new documents
        self.documents.extend(chunks)
        
        # Tokenize new documents
        new_tokenized = [self._tokenize(chunk['text']) for chunk in chunks]
        self.tokenized_corpus.extend(new_tokenized)
        
        # Recreate BM25 index (BM25 doesn't support incremental updates)
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print(f"Updated BM25 index. Now has {len(self.documents)} documents")
    
    def search(self, query, k=10):
        """Search for top k documents using BM25"""
        if self.bm25 is None or not self.documents:
            return []
        
        # Tokenize query
        tokenized_query = self._tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        # Return results with scores
        results = []
        for idx in top_indices:
            if idx < len(self.documents):
                results.append({
                    'text': self.documents[idx]['text'],
                    'score': float(scores[idx]),
                    'metadata': self.documents[idx]['metadata'],
                    'index': idx
                })
        
        return results
    
    def _tokenize(self, text):
        """Simple tokenization (lowercase and split by whitespace)"""
        return text.lower().split()
    
    def save(self, path=Config.BM25_INDEX_PATH):
        """Save BM25 index and documents to disk"""
        os.makedirs(path, exist_ok=True)
        
        data = {
            'documents': self.documents,
            'tokenized_corpus': self.tokenized_corpus
        }
        
        with open(f'{path}/bm25_data.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Saved BM25 index to {path}")
    
    def load(self, path=Config.BM25_INDEX_PATH):
        """Load BM25 index and documents from disk"""
        data_path = f'{path}/bm25_data.pkl'
        
        if os.path.exists(data_path):
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
            
            self.documents = data['documents']
            self.tokenized_corpus = data['tokenized_corpus']
            
            # Recreate BM25 index
            if self.tokenized_corpus:
                self.bm25 = BM25Okapi(self.tokenized_corpus)
                print(f"Loaded BM25 index with {len(self.documents)} documents")
                return True
        
        return False
