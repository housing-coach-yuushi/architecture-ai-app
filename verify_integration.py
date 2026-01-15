
import sys
import os
import time

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import kie_api
import requests

API_KEY = "e93182223f9c247b808eea4199889ce2"

def verify_integration():
    print("1. Uploading image...")
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    img_url = kie_api.upload_image_to_kieai(API_KEY, base64_image)
    if not img_url:
        print("Upload failed")
        return
    print(f"Image uploaded: {img_url}")
    
    print("2. Creating task via kie_api...")
    tid, msg = kie_api.create_kie_task(API_KEY, {
        "model": "nano-banana-pro",
        "callBackUrl": "", # Use empty as per new implementation
        "input": {
            "prompt": "test",
            "image_input": [img_url],
            "aspect_ratio": "1:1",
            "resolution": "1K",
            "output_format": "png"
        }
    })
    
    if not tid:
        print(f"Create task failed: {msg}")
        return
        
    print(f"Task created: {tid}")
    
    print("3. Testing poll_task function...")
    for i in range(5):
        print(f"Polling attempt {i+1}...")
        data = kie_api.poll_task(API_KEY, tid)
        if data:
            print("SUCCESS! Data received:")
            print(data)
            return
        else:
            print("No data yet (or failed poll)")
        time.sleep(2)
        
    print("Verification loop finished.")

if __name__ == "__main__":
    verify_integration()
