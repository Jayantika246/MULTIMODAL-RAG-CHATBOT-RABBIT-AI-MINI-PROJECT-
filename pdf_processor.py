import PyPDF2
from io import BytesIO

class PDFProcessor:
    """Extract text from PDF documents"""
    
    def extract_text_from_pdf(self, pdf_bytes):
        """
        Extract text from PDF file
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            Extracted text as string
        """
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_with_metadata(self, pdf_bytes, filename):
        """
        Extract text and metadata from PDF
        
        Args:
            pdf_bytes: PDF file as bytes
            filename: Original filename
            
        Returns:
            Dictionary with text, metadata
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_bytes)
            
            # Get PDF info
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = {
                'source': filename,
                'type': 'pdf',
                'pages': len(pdf_reader.pages),
                'title': filename.rsplit('.', 1)[0].replace('_', ' ').title()
            }
            
            return {
                'text': text,
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def validate_pdf(self, pdf_bytes):
        """Check if file is a valid PDF"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            # Try to access pages to validate
            _ = len(pdf_reader.pages)
            return True
        except:
            return False
