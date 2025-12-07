import requests
import json
import base64
import io
from PIL import Image

API_KEY = "e93182223f9c247b808eea4199889ce2"

def create_dummy_image():
    img = Image.new('RGB', (1024, 1024), color = 'white')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def test_create_task():
    print("Testing createTask endpoint...")
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    base64_image = create_dummy_image()
    
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": "Modern minimal house architecture, photorealistic, 8k, sunny day, blue sky, wooden facade, garden with trees",
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
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and "taskId" in result["data"]:
                task_id = result["data"]["taskId"]
                print(f"Task ID: {task_id}")
                
                # Try polling guess 1
                poll_url = f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}"
                print(f"Polling {poll_url}...")
                poll_response = requests.get(poll_url, headers=headers)
                print(f"Poll Status: {poll_response.status_code}")
                print(f"Poll Response: {poll_response.text}")

    except Exception as e:
        print(f"Error: {e}")

def test_nano_banana_on_flux():
    print("\nTesting Nano Banana on Flux endpoint...")
    url = "https://api.kie.ai/api/v1/flux/kontext/generate"
    base64_image = create_dummy_image()
    
    payload = {
        "prompt": "Modern minimal house",
        "image": base64_image,
        "strength": 0.6,
        "aspectRatio": "16:9",
        "model": "nano-banana-pro", # Trying this model on Flux endpoint
        "outputFormat": "png"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_create_task_brute_force_polling():
    print("\nTesting createTask with brute force polling...")
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
        print(f"Create Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result:
                task_id = result["data"].get("taskId")
                record_id = result["data"].get("recordId")
                print(f"Task ID: {task_id}, Record ID: {record_id}")
                
                endpoints = [
                    f"https://api.kie.ai/api/v1/jobs/getTask?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/detail?id={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/status?id={task_id}",
                    f"https://api.kie.ai/api/v1/task/info?taskId={task_id}",
                    f"https://api.kie.ai/api/v1/jobs/{task_id}",
                    f"https://api.kie.ai/api/v1/jobs/record-info?taskId={task_id}", # Retrying
                    f"https://api.kie.ai/api/v1/jobs/record-info?recordId={record_id}", # Trying recordId
                ]
                
                for poll_url in endpoints:
                    print(f"Trying {poll_url}...")
                    try:
                        poll_response = requests.get(poll_url, headers=headers)
                        print(f"Status: {poll_response.status_code}")
                        if poll_response.status_code == 200:
                            print(f"Response: {poll_response.text}")
                    except Exception as e:
                        print(f"Error: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nano_banana_on_flux()
    test_create_task_brute_force_polling()
