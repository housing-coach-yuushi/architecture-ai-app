import requests
import json
import time
import base64
import io

API_KEY = "e93182223f9c247b808eea4199889ce2"

def debug_polling_deep():
    print("1. Uploading tiny image...")
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    res = requests.post(upload_url, headers=headers, json={
        "base64Data": base64_image, "filename": "test.png", "uploadPath": "temp"
    })
    if res.status_code != 200:
        print(f"Upload failed: {res.text}")
        return
    img_url = res.json()["data"]["downloadUrl"]
    print(f"Uploaded: {img_url}")

    # Create Task
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
    if create_res.status_code != 200:
        print(f"Create failed: {create_res.text}")
        return
    task_id = create_res.json()["data"]["taskId"]
    print(f"Task ID: {task_id}")
    
    # Polling Candidates
    endpoints = [
        ("gpt4o-image", f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}"),
        ("nano-banana", f"https://api.kie.ai/api/v1/nano-banana/record-info?taskId={task_id}"), # Try without pro
        ("jobs-generic", f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}"),
        ("jobs-fetch", f"https://api.kie.ai/api/v1/jobs/fetch?taskId={task_id}"),
        ("task-info", f"https://api.kie.ai/api/v1/task/info?taskId={task_id}"),
        ("query-task", f"https://api.kie.ai/api/v1/query/task?taskId={task_id}")
    ]
    
    print("3. Polling loop (30s)...")
    for i in range(10):
        print(f"\n--- Attempt {i+1} ---")
        found_data = False
        for name, url in endpoints:
            try:
                r = requests.get(url, headers=headers, timeout=5)
                status = r.status_code
                try:
                    js = r.json()
                    data_val = js.get("data")
                    code_val = js.get("code")
                    msg_val = js.get("msg")
                    
                    short_js = str(js)
                    if len(short_js) > 200: short_js = short_js[:200] + "..."
                    
                    if status == 200:
                        print(f"[{name}] {status} | Code: {code_val} | DataType: {type(data_val)} | Msg: {msg_val}")
                        if data_val:
                            print(f"   >>> DATA FOUND in {name}: {data_val}")
                            found_data = True
                    else:
                        print(f"[{name}] {status}")
                        
                except Exception as e:
                     print(f"[{name}] {status} (Json Error: {e})")
            except Exception as e:
                print(f"[{name}] Request Error: {e}")
        
        if found_data:
            print("!!! SUCCESS: Found endpoint with data !!!")
            break
            
        time.sleep(3)

if __name__ == "__main__":
    debug_polling_deep()
