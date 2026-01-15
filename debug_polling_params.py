import requests
import json
import base64
import io
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def debug_polling_params():
    print("1. Uploading tiny image...")
    # ... Upload logic ...
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}" }
    res = requests.post(upload_url, headers=headers, json={"base64Data": base64_image, "filename": "t.png", "uploadPath": "temp"})
    img_url = res.json()["data"]["downloadUrl"]
    
    print("2. Creating Nano Banana Pro task...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": "test", "image_input": [img_url], "aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"
        }
    }
    create_res = requests.post(create_url, headers=headers, json=payload)
    task_id = create_res.json()["data"]["taskId"]
    print(f"Task ID: {task_id}")
    
    print("3. Polling with params...")
    base_urls = [
        "https://api.kie.ai/api/v1/gpt4o-image/record-info",
        "https://api.kie.ai/api/v1/jobs/record-info"
    ]
    
    for base in base_urls:
        url = f"{base}?taskId={task_id}&model=nano-banana-pro"
        print(f"Checking {url}")
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                print(f"!!! SUCCESS !!! {url}")
                print(r.text)
                js = r.json()
                if js.get("data"): return
            else:
                 print(f"  -> {r.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_polling_params()
