import os

# Base path for images
IMAGE_DIR = "streamlit_app/assets/images"

# Mapping of food names to Local Image Filenames
FOOD_IMAGE_FILES = {
    # Kimchi Stew
    "김치찌개": "kimchi_stew.jpg",
    "kimchi stew": "kimchi_stew.jpg",
    "된장찌개": "kimchi_stew.jpg", # Fallback to similar stew
    "doenjang stew": "kimchi_stew.jpg",
    
    # Bibimbap
    "비빔밥": "bibimbap.jpg",
    "bibimbap": "bibimbap.jpg",
    
    # Bulgogi
    "불고기": "bulgogi.jpg",
    "bulgogi": "bulgogi.jpg",
    "갈비": "bulgogi.jpg",
    
    # Tteokbokki
    "떡볶이": "tteokbokki.jpg",
    "tteokbokki": "tteokbokki.jpg",
    
    # Noodles
    "잡채": "japchae.jpg",
    "japchae": "japchae.jpg",
    
    # Default
    "default": "default.jpg"
}

def get_food_image_url(food_name: str) -> str:
    """
    Returns the local file path for the given food name.
    """
    # Helper to check if file exists
    def get_path(filename):
        # Streamlit runs from root, so path should be relative to root
        return os.path.join(IMAGE_DIR, filename)

    if not food_name:
        return get_path(FOOD_IMAGE_FILES["default"])
        
    name_lower = food_name.lower().strip()
    
    # Exact match
    if name_lower in FOOD_IMAGE_FILES:
        return get_path(FOOD_IMAGE_FILES[name_lower])
        
    # Partial match
    for key, filename in FOOD_IMAGE_FILES.items():
        if key in name_lower:
            return get_path(filename)
            
    return get_path(FOOD_IMAGE_FILES["default"])
