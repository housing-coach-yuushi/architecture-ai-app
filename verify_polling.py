import requests
import json
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def verify_polling():
    print("1. Uploading image...")
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    upload_payload = {
        "base64Data": base64_image,
        "filename": "test.png",
        "uploadPath": "temp"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        upload_res = requests.post(upload_url, headers=headers, json=upload_payload)
        if upload_res.status_code != 200:
            print(f"Upload failed: {upload_res.text}")
            return
            
        image_url = upload_res.json()["data"]["downloadUrl"]
        print(f"Image uploaded: {image_url}")
        
        print("2. Creating task...")
        create_url = "https://api.kie.ai/api/v1/jobs/createTask"
        create_payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": "test",
                "image_input": [image_url],
                "aspect_ratio": "1:1",
                "output_format": "png"
            }
        }
        
        create_res = requests.post(create_url, headers=headers, json=create_payload)
        if create_res.status_code != 200:
            print(f"Create task failed: {create_res.text}")
            return
            
        task_id = create_res.json()["data"]["taskId"]
        print(f"Task created: {task_id}")
        
        print("3. Testing Polling Endpoints...")
        
        candidates = [
            f"https://api.kie.ai/api/v1/jobs/fetch?taskId={task_id}",
            f"https://api.kie.ai/api/v1/query/task?taskId={task_id}",
            f"https://api.kie.ai/api/v1/task/info?taskId={task_id}",
            f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}",
            f"https://api.kie.ai/api/v1/jobs/detail?taskId={task_id}",
            f"https://api.kie.ai/api/v1/nano-banana-pro/record-info?taskId={task_id}",
            f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}"
        ]
        
        for url in candidates:
            print(f"Trying: {url}")
            try:
                res = requests.get(url, headers=headers)
                print(f"Status: {res.status_code}")
                if res.status_code == 200:
                    print("SUCCESS! Response:")
                    print(res.text[:500]) # First 500 chars
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Overall Error: {e}")

if __name__ == "__main__":
    verify_polling()
