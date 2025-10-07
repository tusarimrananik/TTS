import requests
import os

# Your Pexels API Key
PEXELS_API_KEY = "H6QIDEaVv717Xbq5MZCfG6xtEbKkNACYPHrsIgUf2MS93FQY7NVFSZbZ"


# Function to download images from Pexels
def download_images(query, per_page=5, save_folder="assets/images/"):
    # Ensure the save folder exists
    os.makedirs(save_folder, exist_ok=True)

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        photos = data.get("photos", [])
        if not photos:
            print("No images found.")
            return

        for idx, photo in enumerate(photos, start=1):
            img_url = photo["src"]["original"]
            img_data = requests.get(img_url).content
            file_path = os.path.join(save_folder, f"{idx}.jpg")

            with open(file_path, "wb") as f:
                f.write(img_data)

            print(f"✅ Saved: {file_path}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
