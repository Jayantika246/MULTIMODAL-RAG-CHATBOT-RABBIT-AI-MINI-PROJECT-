from PIL import Image
from io import BytesIO
import base64
from groq import Groq
from config import Config

class ImageProcessor:
    """Process images and generate descriptions using Groq vision model"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
    
    def describe_image(self, image_bytes):
        """
        Generate a detailed description of the image using Groq vision model
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Description text as string
        """
        try:
            # Convert to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Use Groq's vision model to describe the image
            response = self.groq_client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail. If it's a travel destination, landmark, restaurant, hotel, or tourist attraction, provide comprehensive information including: location, notable features, atmosphere, activities, and any visible text or signage. Be specific and descriptive."
                            },
                            {
                                "type": "image_url",
                           