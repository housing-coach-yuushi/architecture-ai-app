import requests
import json
import time
import base64
import io

API_KEY = "e93182223f9c247b808eea4199889ce2"

def debug_polling_deep_v2():
    print("1. Uploading tiny image...")
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    upload_res = requests.post(upload_url, headers=headers, json={
        "base64Data": base64_image, "filename": "test.png", "uploadPath": "temp"
    })
    img_url = upload_res.json()["data"]["downloadUrl"]
    
    print("2. Creating Nano Banana Pro task...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": "test",
            "image_input": [img_url],
            "aspect_ratio": "1:1",
            "resolution": "1K",
            "output_format": "png"
        }
    }
    create_res = requests.post(create_url, headers=headers, json=payload)
    task_id = create_res.json()["data"]["taskId"]
    print(f"Task ID: {task_id}")
    
    # 3. Candidate Endpoints
    # "gpt4o-image" returned 200/null. Maybe a different one works.
    candidates = [
        # Common patterns
        "https://api.kie.ai/api/v1/jobs/record-info?taskId={taskId}",
        "https://api.kie.ai/api/v1/jobs/getTask?taskId={taskId}",
        "https://api.kie.ai/api/v1/task/query?taskId={taskId}",
        "https://api.kie.ai/api/v1/tasks/{taskId}",
        
        # Specific models
        "https://api.kie.ai/api/v1/nano-banana-pro/record-info?taskId={taskId}",
        "https://api.kie.ai/api/v1/nano-banana/record-info?taskId={taskId}",
        "https://api.kie.ai/api/v1/flux-2/record-info?taskId={taskId}",
        
        # Legacy / Other
        "https://api.kie.ai/api/v1/img/record-info?taskId={taskId}",
        "https://api.kie.ai/api/v1/image/record-info?taskId={taskId}",
        "https://api.kie.ai/api/v1/banana/record-info?taskId={taskId}",
        
        # Without V1
        "https://api.kie.ai/api/jobs/record-info?taskId={taskId}",
    ]
    
    print("3. Polling candidates...")
    
    for url_tmpl in candidates:
        url = url_tmpl.format(taskId=task_id)
        print(f"Checking: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                try:
                    js = r.json()
                    data = js.get("data")
                    if data:
                        print(f"!!! SUCCESS !!! Found data at: {url}")
                        print(f"Data: {data}")
                        return
                    else:
                         print(f"  -> 200 OK but data is {data}")
                except:
                    print(f"  -> 200 OK but invalid JSON")
            else:
                print(f"  -> {r.status_code}")
        except Exception as e:
            print(f"  -> Error: {e}")
            
    print("No working endpoint found.")

if __name__ == "__main__":
    debug_polling_deep_v2()
