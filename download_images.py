import os
import requests

# Mapping of food names to Unsplash Image URLs (same as before)
FOOD_IMAGES = {
    # Kimchi Stew / Jjigae (Pixabay - usually reliable)
    "kimchi_stew": "https://cdn.pixabay.com/photo/2015/09/23/10/20/kimchi-953113_1280.jpg",
    "bibimbap": "https://images.unsplash.com/photo-1590301157890-4810ed352733?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    # Bulgogi (Pixabay)
    "bulgogi": "https://cdn.pixabay.com/photo/2016/03/31/21/53/food-1296658_1280.jpg", 
    # Tteokbokki (Pixabay)
    "tteokbokki": "https://cdn.pixabay.com/photo/2020/06/07/16/32/korean-food-5270967_1280.jpg",
    "japchae": "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1553621042-f6e147245754?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
}

SAVE_DIR = "streamlit_app/assets/images"

def download_images():
    print(f"Downloading images to {SAVE_DIR}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    for name, url in FOOD_IMAGES.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                file_path = os.path.join(SAVE_DIR, f"{name}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded {name}.jpg")
            else:
                print(f"Failed to download {name}: Status {response.status_code}")
        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == "__main__":
    download_images()
