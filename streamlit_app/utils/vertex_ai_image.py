import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from pathlib import Path
import streamlit as st

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GENERATED_IMAGES_DIR = "streamlit_app/assets/images/generated"

def init_vertex_ai():
    """Initialize Vertex AI SDK."""
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        return True
    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return False

def generate_food_image(food_name: str, save_dir: str = GENERATED_IMAGES_DIR) -> str | None:
    """
    Generate an image for the given food name using Vertex AI Imagen 3.
    
    Args:
        food_name: The name of the food to generate an image for.
        save_dir: The directory to save the generated image.
        
    Returns:
        The path to the generated image, or None if generation failed.
    """
    # Create directory if it doesn't exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_name = "".join([c if c.isalnum() else "_" for c in food_name]).lower()
    file_path = os.path.join(save_dir, f"{safe_name}.png")
    
    # Check if image already exists (Simple Caching)
    if os.path.exists(file_path):
        return file_path
        
    if not init_vertex_ai():
        return None

    try:
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        prompt = f"A delicious traditional Korean dish called {food_name}. Professional food photography, top-down view, served in authentic Korean ceramic bowl or plate, steam rising, vibrant colors, studio lighting, 4k resolution, appetizing Korean cuisine."
        
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )
        
        if images:
            images[0].save(location=file_path, include_generation_parameters=False)
            return file_path
            
    except Exception as e:
        print(f"Error generating image for {food_name}: {e}")
        return None
    
    return None
