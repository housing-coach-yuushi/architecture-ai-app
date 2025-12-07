import requests
import json
import base64
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def test_polling_advanced():
    print("1. Uploading image...")
    # Upload image first
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    # Create a tiny dummy base64 image
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
        print(f"Create status: {create_res.status_code}")
        print(f"Create response: {create_res.text}")
        
        if create_res.status_code != 200:
            return
            
        task_id = create_res.json()["data"]["taskId"]
        print(f"Task created: {task_id}")
        
        print("3. Brute forcing polling endpoints...")
        
        domains = [
            "https://api.kie.ai",
            "https://kieai.redpandaai.co"
        ]
        
        paths = [
            # Generic
            "/api/v1/jobs/getTask",
            "/api/v1/jobs/detail",
            "/api/v1/jobs/status",
            "/api/v1/jobs/record-info",
            "/api/v1/task/info",
            "/api/v1/task/query",
            "/api/v1/tasks",
            
            # Model specific
            "/api/v1/nano-banana/record-info",
            "/api/v1/nano-banana-pro/record-info",
            "/api/v1/nano-banana/getTask",
            "/api/v1/nano-banana/detail",
            "/api/v1/gemini/record-info",
            "/api/v1/gemini-3/record-info",
            
            # Playground
            "/api/v1/playground/getTask",
            "/api/v1/playground/record-info",
            
            # Without v1
            "/api/jobs/getTask",
            "/api/jobs/record-info",
        ]
        
        for domain in domains:
            for path in paths:
                url = f"{domain}{path}"
                # Try with id and taskId params
                for param in ["id", "taskId"]:
                    poll_url = f"{url}?{param}={task_id}"
                    try:
                        res = requests.get(poll_url, headers=headers)
                        print(f"{poll_url}: {res.status_code}")
                        if res.status_code == 200:
                            print(f"FOUND! {poll_url}")
                            print(res.text)
                            return
                    except Exception as e:
                        print(f"{poll_url}: Error {e}")
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_polling_advanced()
