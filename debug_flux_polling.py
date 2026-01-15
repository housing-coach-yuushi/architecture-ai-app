import requests
import json
import base64
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def verify_flux_polling():
    print("1. Uploading tiny image...")
    # ... (Same upload logic) ...
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}" }
    res = requests.post(upload_url, headers=headers, json={"base64Data": base64_image, "filename": "t.png", "uploadPath": "temp"})
    img_url = res.json()["data"]["downloadUrl"]
    
    print("2. Creating Flux 2 task...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "flux-2/flex-image-to-image",
        "input": {
            "input_urls": [img_url],
            "prompt": "test",
            "aspect_ratio": "1:1",
            "resolution": "1K",
            "strength": 0.55
        }
    }
    create_res = requests.post(create_url, headers=headers, json=payload)
    print(create_res.text)
    task_id = create_res.json()["data"]["taskId"]
    print(f"Flux Task ID: {task_id}")
    
    # 3. Test Polling
    print("3. Testing polling endpoints for Flux...")
    endpoints = [
        f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}",
        f"https://api.kie.ai/api/v1/flux-2/record-info?taskId={task_id}",
        f"https://api.kie.ai/api/v1/flux/record-info?taskId={task_id}",
        f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}"
    ]
    
    for i in range(10): # 30s
        found = False
        for url in endpoints:
            try:
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json().get("data")
                    if data:
                        print(f"!!! SUCCESS !!! {url}")
                        print(data)
                        found = True
                        break
            except: pass
        if found: break
        time.sleep(3)
    
    print("Done Flux Check.")

if __name__ == "__main__":
    verify_flux_polling()
