import re

class DocumentChunker:
    def __init__(self, chunk_size=450, overlap=75):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_documents(self, documents):
        """
        Chunk documents with semantic splitting and metadata
        Returns list of dicts with text, metadata
        """
        chunks = []
        
        for doc_idx, document in enumerate(documents):
            doc_chunks = self._chunk_text(document, doc_idx)
            chunks.extend(doc_chunks)
        
        return chunks
    
    def _chunk_text(self, text, doc_idx):
        """Split text into semantic chunks with overlap"""
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'source_id': doc_idx,
                        'chunk_id': chunk_id,
                        'source_title': f'Document {doc_idx + 1}'
                    }
                })
                
                # Start new chunk with overlap
                overlap_text = chunk_text[-self.overlap:] if len(chunk_text) > self.overlap else chunk_text
                current_chunk = [overlap_text, sentence]
                current_length = len(overlap_text) + sentence_length
                chunk_id += 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'source_id': doc_idx,
                    'chunk_id': chunk_id,
                    'source_title': f'Document {doc_idx + 1}'
                }
            })
        
        return chunks
