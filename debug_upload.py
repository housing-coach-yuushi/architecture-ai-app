import requests
import json
import base64
import io
from PIL import Image

API_KEY = "e93182223f9c247b808eea4199889ce2"

def create_dummy_image():
    img = Image.new('RGB', (100, 100), color = 'white')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str # Raw base64 string without prefix for some APIs, or with prefix? Usually raw.

def test_upload_brute_force():
    print("Testing upload endpoints...")
    base64_image = create_dummy_image()
    
    # Potential endpoints
    endpoints = [
        "https://api.kie.ai/api/file-base64-upload", # Trying standard domain first
        "https://kieai.redpandaai.co/api/file-base64-upload", # Found in search
        "https://api.kie.ai/api/v1/file-base64-upload",
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payloads = [
        {"base64Data": base64_image, "filename": "test.jpg", "uploadPath": "temp"},
        {"base64Data": base64_image, "filename": "test.jpg", "uploadPath": "images"},
        {"base64Data": base64_image, "filename": "test.jpg", "uploadPath": "/"},
    ]
    
    url = "https://kieai.redpandaai.co/api/file-base64-upload"
    print(f"Testing {url} with variations...")
    
    for p in payloads:
        print(f"Testing payload keys: {list(p.keys())}")
        try:
            response = requests.post(url, headers=headers, json=p)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text}")
                print("FOUND CORRECT PAYLOAD! ^^^")
                return
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_upload_brute_force()
