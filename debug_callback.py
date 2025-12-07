import requests
import json
import time

API_KEY = "e93182223f9c247b808eea4199889ce2"

def test_webhook_callback():
    # 1. Create Webhook Token
    print("1. Creating Webhook Token...")
    try:
        wh_res = requests.post("https://webhook.site/token")
        if wh_res.status_code != 201 and wh_res.status_code != 200:
            print(f"Failed to create webhook token: {wh_res.status_code} {wh_res.text}")
            return
        
        wh_data = wh_res.json()
        uuid = wh_data["uuid"]
        callback_url = f"https://webhook.site/{uuid}"
        print(f"Webhook URL: {callback_url}")
        
    except Exception as e:
        print(f"Error creating webhook: {e}")
        return

    # 2. Upload Image
    print("2. Uploading Image...")
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    base64_image = f"data:image/png;base64,{base64_data}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    upload_payload = {
        "base64Data": base64_image,
        "filename": "test.png",
        "uploadPath": "temp"
    }
    
    upload_res = requests.post(upload_url, headers=headers, json=upload_payload)
    image_url = upload_res.json()["data"]["downloadUrl"]
    
    # 3. Create Task with Callback
    print("3. Creating Task with Callback...")
    create_url = "https://api.kie.ai/api/v1/jobs/createTask"
    create_payload = {
        "model": "nano-banana-pro",
        "callBackUrl": callback_url, # Add callback URL
        "input": {
            "prompt": "test",
            "image_input": [image_url],
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
    }
    
    create_res = requests.post(create_url, headers=headers, json=create_payload)
    print(f"Create Status: {create_res.status_code}")
    if create_res.status_code != 200:
        print(f"Create Failed: {create_res.text}")
        return
        
    task_id = create_res.json()["data"]["taskId"]
    print(f"Task ID: {task_id}")
    
    # 4. Poll Webhook for Result
    print("4. Polling Webhook for Result...")
    poll_wh_url = f"https://webhook.site/token/{uuid}/requests"
    
    for i in range(20): # Wait up to 40 seconds
        print(f"Polling webhook attempt {i+1}...")
        try:
            wh_reqs = requests.get(poll_wh_url)
            if wh_reqs.status_code == 200:
                reqs_data = wh_reqs.json()
                data_list = reqs_data.get("data", [])
                
                if data_list:
                    # Check if any request contains our task ID or looks like a callback
                    for req in data_list:
                        content = req.get("content")
                        if content:
                            try:
                                # Content might be JSON string
                                body = json.loads(content)
                                print("Received Callback Body:")
                                print(json.dumps(body, indent=2))
                                
                                # Check for result URL
                                if "data" in body and "resultJson" in body["data"]:
                                    res_json = json.loads(body["data"]["resultJson"])
                                    if "resultUrls" in res_json:
                                        print(f"IMAGE URL FOUND: {res_json['resultUrls'][0]}")
                                        return
                            except:
                                pass
        except Exception as e:
            print(f"Webhook poll error: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    test_webhook_callback()
