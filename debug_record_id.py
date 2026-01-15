import requests
import json
import base64
import io

API_KEY = "e93182223f9c247b808eea4199889ce2"

def check_record_id():
    print("1. Uploading tiny image...")
    # ... (Same upload logic) ...
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}" }
    res = requests.post(upload_url, headers=headers, json={"base64Data": base64_image, "filename": "t.png", "uploadPath": "temp"})
    img_url = res.json()["data"]["downloadUrl"]
    
    print("2. Creating task...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": "test", "image_input": [img_url], "aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"
        }
    }
    create_res = requests.post(create_url, headers=headers, json=payload)
    print(f"Create Response Body: {create_res.text}")
    
    data = create_res.json().get("data", {})
    task_id = data.get("taskId")
    record_id = data.get("recordId")
    
    print(f"TaskID: {task_id}, RecordID: {record_id}")
    
    if record_id:
        print("3. Testing polling with recordId...")
        url = f"https://api.kie.ai/api/v1/jobs/record-info?recordId={record_id}"
        r = requests.get(url, headers=headers)
        print(f"Poll check: {r.status_code} - {r.text}")

if __name__ == "__main__":
    check_record_id()
