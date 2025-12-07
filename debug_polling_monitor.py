import requests
import json
import time
import uuid

API_KEY = "e93182223f9c247b808eea4199889ce2"

def test_polling_monitor():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 1. Test Random ID
    random_id = str(uuid.uuid4()).replace("-", "")
    print(f"Testing Random ID: {random_id}")
    url = f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={random_id}"
    try:
        res = requests.get(url, headers=headers)
        print(f"Random ID Status: {res.status_code}")
        print(f"Random ID Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Create Real Task
    print("\nCreating Real Task...")
    # Upload image
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    upload_payload = {
        "base64Data": base64_image,
        "filename": "test.png",
        "uploadPath": "temp"
    }
    
    upload_res = requests.post(upload_url, headers=headers, json=upload_payload)
    image_url = upload_res.json()["data"]["downloadUrl"]
    
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
    task_id = create_res.json()["data"]["taskId"]
    print(f"Real Task ID: {task_id}")
    
    # 3. Monitor Real Task
    print("Monitoring Real Task...")
    poll_url = f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}"
    
    for i in range(10): # Monitor for 20 seconds
        try:
            res = requests.get(poll_url, headers=headers)
            print(f"Poll {i+1}: {res.status_code} - {res.text}")
            
            if res.status_code == 200:
                body = res.json()
                data = body.get("data")
                if data:
                    print("DATA RECEIVED!")
                    break
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    test_polling_monitor()
