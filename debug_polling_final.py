import requests
import json
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def test_polling_final():
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
        print(f"Create status: {create_res.status_code}")
        
        if create_res.status_code != 200:
            print(f"Create failed: {create_res.text}")
            return
            
        task_id = create_res.json()["data"]["taskId"]
        print(f"Task created: {task_id}")
        
        print("3. Brute forcing polling endpoints (Final - skipping false positives)...")
        
        endpoints = [
            # Runway
            f"https://api.kie.ai/api/v1/runway/record-detail?taskId={task_id}",
            
            # Query variants
            f"https://api.kie.ai/api/v1/query/task?taskId={task_id}",
            f"https://api.kie.ai/api/v1/task/query?taskId={task_id}",
            f"https://api.kie.ai/api/v1/jobs/query?taskId={task_id}",
            f"https://api.kie.ai/api/v1/jobs/check?taskId={task_id}",
            f"https://api.kie.ai/api/v1/tasks/query?taskId={task_id}",
            
            # Playground variants
            f"https://api.kie.ai/api/v1/playground/getTask?taskId={task_id}",
            f"https://api.kie.ai/api/v1/playground/record-info?taskId={task_id}",
            f"https://api.kie.ai/api/v1/playground/query?taskId={task_id}",
            f"https://api.kie.ai/api/v1/playground/task?taskId={task_id}",
            
            # Nano/Gemini variants
            f"https://api.kie.ai/api/v1/nano-banana/query?taskId={task_id}",
            f"https://api.kie.ai/api/v1/gemini/query?taskId={task_id}",
            
            # Status variants
            f"https://api.kie.ai/api/v1/status?taskId={task_id}",
            f"https://api.kie.ai/api/v1/job/status?taskId={task_id}",
            
            # ID in path
            f"https://api.kie.ai/api/v1/tasks/{task_id}",
            f"https://api.kie.ai/api/v1/jobs/{task_id}",
            
            # Redpanda domain
            f"https://kieai.redpandaai.co/api/v1/task/query?taskId={task_id}",
        ]
        
        for url in endpoints:
            try:
                res = requests.get(url, headers=headers)
                print(f"{url}: {res.status_code}")
                if res.status_code == 200:
                    try:
                        body = res.json()
                        if body.get("code") == 200:
                            print(f"FOUND! {url}")
                            print(res.text)
                            return
                        else:
                            print(f"Logical error at {url}: {body.get('msg')}")
                    except:
                        print(f"Response not JSON at {url}")
            except Exception as e:
                print(f"{url}: Error {e}")
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_polling_final()
