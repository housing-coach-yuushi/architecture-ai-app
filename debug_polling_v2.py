import requests
import json
import base64
import io
from PIL import Image
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def create_dummy_image():
    img = Image.new('RGB', (1024, 1024), color = 'white')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def test_polling_brute_force():
    print("Creating task to get a valid Task ID...")
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    base64_image = create_dummy_image()
    
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": "Modern minimal house",
            "image": base64_image,
            "strength": 0.6,
            "aspect_ratio": "16:9",
            "output_format": "png"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Create Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result:
                task_id = result["data"].get("taskId")
                record_id = result["data"].get("recordId")
                print(f"Task ID: {task_id}, Record ID: {record_id}")
                
                # List of potential polling endpoints
                endpoints = [
                    # Generic jobs/task endpoints
                    f"https://api.kie.ai/api/v1/jobs/getTask?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/detail?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/details?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/status?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/{task_id}",
                    
                    # 4o Image style endpoints (guessing)
                    f"https://api.kie.ai/api/v1/4o/image/details?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/4o/image/getTask?taskId={task_id}",
                    
                    # Nano Banana specific guessing
                    f"https://api.kie.ai/api/v1/nano-banana/details?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/nano-banana/getTask?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/nano/details?taskId={task_id}",
                    
                    # Image generic
                    f"https://api.kie.ai/api/v1/image/details?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/image/getTask?taskId={task_id}",
                    
                    # Record info variants
                    f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/record-info?recordId={record_id}",
                    f"https://api.kie.ai/api/v1/task/details?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/tasks/{task_id}",
                    f"https://api.kie.ai/api/v1/tasks/status?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/img2img/task/info?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/img2img/getTask?taskId={task_id}",
                ]
                
                for poll_url in endpoints:
                    print(f"Trying {poll_url}...")
                    try:
                        poll_response = requests.get(poll_url, headers=headers)
                        print(f"Status: {poll_response.status_code}")
                        if poll_response.status_code == 200:
                            print(f"Response: {poll_response.text}")
                            print("FOUND IT! ^^^")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("No data in response")
                print(response.text)
        else:
            print(f"Create Failed: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_polling_brute_force()
