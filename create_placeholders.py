from PIL import Image, ImageDraw, ImageFont
import os

def create_image(filename, text, color):
    img = Image.new('RGB', (800, 600), color=color)
    d = ImageDraw.Draw(img)
    
    # Draw text roughly in center
    d.text((50, 250), text, fill=(255, 255, 255))
    
    img.save(filename)
    print(f"Created {filename}")

os.makedirs("streamlit_app/assets/images", exist_ok=True)

# Create placeholders for missing images
create_image("streamlit_app/assets/images/kimchi_stew.jpg", "Kimchi Stew", "#CC3300") # Red
create_image("streamlit_app/assets/images/bulgogi.jpg", "Bulgogi", "#663300") # Brown
create_image("streamlit_app/assets/images/tteokbokki.jpg", "Tteokbokki", "#FF3300") # Bright Red
