import requests
import json
import base64
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def verify_callback():
    print("1. getting webhook token...")
    try:
        res = requests.post("https://webhook.site/token")
        if res.status_code not in [200, 201]:
            print(f"Failed to get token: {res.status_code}")
            return
        uuid = res.json()["uuid"]
        callback_url = f"https://webhook.site/{uuid}"
        poll_url = f"https://webhook.site/token/{uuid}/requests"
        print(f"Callback registered: {callback_url}")
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return

    print("2. Uploading tiny image...")
    # ... Upload logic ...
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}" }
    res = requests.post(upload_url, headers=headers, json={"base64Data": base64_image, "filename": "t.png", "uploadPath": "temp"})
    img_url = res.json()["data"]["downloadUrl"]
    
    print("3. Creating Nano Banana Pro task with callback...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    payload = {
        "model": "nano-banana-pro",
        "callBackUrl": callback_url,
        "input": {
            "prompt": "test", "image_input": [img_url], "aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"
        }
    }
    create_res = requests.post(create_url, headers=headers, json=payload)
    if create_res.status_code != 200:
        print(f"Create failed: {create_res.text}")
        return
    task_id = create_res.json()["data"]["taskId"]
    print(f"Task created: {task_id}")
    
    print("4. Waiting for callback (60s)...")
    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            r = requests.get(poll_url)
            if r.status_code == 200:
                data = r.json()["data"]
                # Filter for this task if multiple
                for req in data:
                    content = req.get("content")
                    if content and task_id in content:
                        print("!!! SUCCESS !!! Callback received!")
                        print(content)
                        return
                    elif content:
                         print(f"Msg: {content[:50]}...")
            else:
                print(f"Poll check: {r.status_code}")
        except Exception as e:
            print(f"Poll error: {e}")
        time.sleep(5)
    
    print("Timed out waiting for callback.")

if __name__ == "__main__":
    verify_callback()
