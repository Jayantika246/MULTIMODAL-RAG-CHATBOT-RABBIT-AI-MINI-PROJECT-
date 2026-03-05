import os
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO

class ImageHandler:
    """Handle image uploads with user-provided captions"""
    
    def __init__(self, upload_folder='static/uploads'):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def save_image(self, image_bytes, filename):
        """
        Save uploaded image to disk
        
        Args:
            image_bytes: Image file as bytes
            filename: Original filename
            
        Returns:
            Path to saved image
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = filename.rsplit('.', 1)[-1].lower()
            new_filename = f"img_{timestamp}.{ext}"
            filepath = os.path.join(self.upload_folder, new_filename)
            
            # Validate and save image
            image = Image.open(BytesIO(image_bytes))
            
            # Resize if too large (max 1920px width)
            max_width = 1920
            if image.width > max_width:
                ratio = max_width / image.width
                new_size = (max_width, int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # Save as JPEG
            image.save(filepath, 'JPEG', quality=85, optimize=True)
            
            return f"/static/uploads/{new_filename}"
            
        except Exception as e:
            raise Exception(f"Failed to save image: {str(e)}")
    
    def create_image_document(self, caption, image_url, filename):
        """
        Create a document chunk from image caption
        
        Args:
            caption: User-provided description
            image_url: Path to saved image
            filename: Original filename
            
        Returns:
            Document text with metadata
        """
        title = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
        
        # Create a rich, searchable document
        document = f"""[TRAVEL IMAGE: {title}]

IMAGE DESCRIPTION: {caption}

VISUAL CONTENT: This is a travel photograph showing {caption.lower()}. 

LOCATION/SUBJECT: {caption}

KEYWORDS: {caption.lower()}, {title.lower()}, travel photo, destination image

IMAGE FILE: {filename}
IMAGE URL: {image_url}

This image can be used to answer questions about: {caption.lower()}, places to visit, travel destinations, visual references, location information.

When asked about "{caption.lower()}" or similar queries, refer to this image as a visual reference for the location or subject matter.
"""
        return document
    
    def validate_image(self, image_bytes):
        """Check if file is a valid image"""
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            return True
        except:
            return False
    
    def get_image_info(self, image_bytes):
        """Get image dimensions and format"""
        try:
            image = Image.open(BytesIO(image_bytes))
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode
            }
        except:
            return None
