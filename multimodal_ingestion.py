from pdf_processor import PDFProcessor
from image_handler import ImageHandler
from ingestion import IngestionService

class MultimodalIngestion:
    """Handle ingestion of multiple document types (text, PDF, images with captions)"""
    
    def __init__(self, vector_store, bm25_store):
        self.pdf_processor = PDFProcessor()
        self.image_handler = ImageHandler()
        self.text_ingestion = IngestionService(vector_store, bm25_store)
    
    def ingest_pdf(self, pdf_bytes, filename):
        """
        Extract text from PDF and ingest into vector stores
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename
            
        Returns:
            Number of chunks created
        """
        print(f"Processing PDF: {filename}")
        
        # Validate PDF
        if not self.pdf_processor.validate_pdf(pdf_bytes):
            raise Exception("Invalid PDF file")
        
        # Extract text and metadata
        data = self.pdf_processor.extract_with_metadata(pdf_bytes, filename)
        
        print(f"Extracted {len(data['text'])} characters from {data['metadata']['pages']} pages")
        
        # Check if text was extracted
        if not data['text'].strip():
            raise Exception("No text could be extracted from PDF. It might be an image-based PDF.")
        
        # Create document with metadata
        document_text = f"[PDF: {data['metadata']['title']}]\n\n{data['text']}"
        
        # Ingest as text document
        chunks_created = self.text_ingestion.ingest_documents([document_text])
        
        print(f"Created {chunks_created} chunks from PDF")
        
        return {
            'chunks_created': chunks_created,
            'pages': data['metadata']['pages'],
            'title': data['metadata']['title'],
            'characters': len(data['text'])
        }
    
    def ingest_image_with_caption(self, image_bytes, filename, caption):
        """
        Save image and ingest with user-provided caption
        
        Args:
            image_bytes: Image file as bytes
            filename: Original filename
            caption: User-provided description/tags
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing Image: {filename}")
        
        # Validate image
        if not self.image_handler.validate_image(image_bytes):
            raise Exception("Invalid image file")
        
        # Validate caption
        if not caption or not caption.strip():
            raise Exception("Caption is required. Please describe the image.")
        
        # Save image to disk
        image_url = self.image_handler.save_image(image_bytes, filename)
        print(f"Image saved to: {image_url}")
        
        # Create document from caption
        document_text = self.image_handler.create_image_document(
            caption.strip(), 
            image_url, 
            filename
        )
        
        # Get image info
        image_info = self.image_handler.get_image_info(image_bytes)
        
        # Ingest as text document
        chunks_created = self.text_ingestion.ingest_documents([document_text])
        
        print(f"Created {chunks_created} chunks from image with caption")
        
        return {
            'chunks_created': chunks_created,
            'title': filename.rsplit('.', 1)[0].replace('_', ' ').title(),
            'caption': caption.strip(),
            'image_url': image_url,
            'width': image_info['width'] if image_info else 'unknown',
            'height': image_info['height'] if image_info else 'unknown',
            'format': image_info['format'] if image_info else 'unknown'
        }
    
    def ingest_text(self, text_content, source_name="text_document"):
        """
        Ingest plain text (existing functionality wrapper)
        
        Args:
            text_content: Text string or list of text strings
            source_name: Source identifier
            
        Returns:
            Number of chunks created
        """
        if isinstance(text_content, str):
            text_content = [text_content]
        
        return self.text_ingestion.ingest_documents(text_content)
