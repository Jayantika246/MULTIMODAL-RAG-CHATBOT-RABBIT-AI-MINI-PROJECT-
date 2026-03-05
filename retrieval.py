from embeddings import EmbeddingService
from config import Config
import numpy as np

class RetrievalService:
    def __init__(self, vector_store, bm25_store):
        self.embedding_service = EmbeddingService()
        self.vector_store = vector_store
        self.bm25_store = bm25_store
    
    def retrieve(self, query, top_k=10, final_k=3):
        """
        Hybrid retrieval using FAISS + BM25 with Reciprocal Rank Fusion
        1. Enhance query for better retrieval
        2. Get top_k from FAISS (dense)
        3. Get top_k from BM25 (sparse)
        4. Apply RRF to fuse results
        5. Return best final_k chunks
        """
        # Check if stores have documents
        if (self.vector_store.index is None or len(self.vector_store.documents) == 0) and \
           (self.bm25_store.bm25 is None or len(self.bm25_store.documents) == 0):
            print("No documents in stores")
            return []
        
        print(f"Vector store: {len(self.vector_store.documents)} docs, BM25 store: {len(self.bm25_store.documents)} docs")
        
        # Enhance query with context hints
        enhanced_query = self._enhance_query(query)
        
        # Retrieve from FAISS
        faiss_results = []
        if self.vector_store.index is not None and len(self.vector_store.documents) > 0:
            query_embedding = self.embedding_service.encode([enhanced_query])[0]
            faiss_results = self.vector_store.search(query_embedding, k=top_k)
            print(f"FAISS retrieved {len(faiss_results)} results")
        
        # Retrieve from BM25
        bm25_results = []
        if self.bm25_store.bm25 is not None and len(self.bm25_store.documents) > 0:
            bm25_results = self.bm25_store.search(enhanced_query, k=top_k)
            print(f"BM25 retrieved {len(bm25_results)} results")
        
        # Apply Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(faiss_results, bm25_results)
        
        print(f"RRF fused to {len(fused_results)} results")
        
        # Return top final_k
        return fused_results[:final_k]
    
    def _reciprocal_rank_fusion(self, faiss_results, bm25_results, k=Config.RRF_K):
        """
        Combine FAISS and BM25 results using Reciprocal Rank Fusion
        
        RRF score = sum(1 / (k + rank_i)) for each retrieval method
        
        Args:
            faiss_results: Results from FAISS
            bm25_results: Results from BM25
            k: RRF constant (default 60)
        """
        # Create a dictionary to store RRF scores
        rrf_scores = {}
        
        # Process FAISS results
        for rank, result in enumerate(faiss_results, start=1):
            doc_id = result['text']  # Use text as unique identifier
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    'score': 0,
                    'text': result['text'],
                    'metadata': result['metadata'],
                    'faiss_rank': rank,
                    'bm25_rank': None
                }
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
            rrf_scores[doc_id]['faiss_rank'] = rank
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results, start=1):
            doc_id = result['text']
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    'score': 0,
                    'text': result['text'],
                    'metadata': result['metadata'],
                    'faiss_rank': None,
                    'bm25_rank': rank
                }
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
            rrf_scores[doc_id]['bm25_rank'] = rank
        
        # Sort by RRF score (descending)
        sorted_results = sorted(rrf_scores.values(), key=lambda x: x['score'], reverse=True)
        
        # Format results
        final_results = []
        for result in sorted_results:
            final_results.append({
                'text': result['text'],
                'score': result['score'],
                'metadata': result['metadata']
            })
        
        return final_results
    
    def _enhance_query(self, query):
        """Enhance query with contextual hints for better retrieval"""
        query_lower = query.lower()
        
        # Detect query intent and add context
        if any(word in query_lower for word in ['cafe', 'restaurant', 'food', 'eat', 'dining']):
            return f"{query}. Looking for cafe names, restaurants, and food specialties."
        elif any(word in query_lower for word in ['hotel', 'stay', 'accommodation', 'resort']):
            return f"{query}. Looking for hotels, accommodations, and lodging options."
        elif any(word in query_lower for word in ['visit', 'see', 'attraction', 'landmark', 'place']):
            return f"{query}. Looking for tourist attractions, landmarks, and places to visit."
        elif any(word in query_lower for word in ['beach', 'water', 'ocean', 'sea']):
            return f"{query}. Looking for beaches, water activities, and coastal areas."
        else:
            return query
