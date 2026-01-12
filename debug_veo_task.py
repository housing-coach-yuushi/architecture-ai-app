import requests
import time
import os
import json
import streamlit as st # Mocking st.secrets if needed but better to use env vars or hardcode for debug script
from db import get_connection

# Load secrets manually or hardcode for testing
try:
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    API_KEY = secrets["KIEAI_API_KEY"]
except:
    API_KEY = os.environ.get("KIEAI_API_KEY")

if not API_KEY:
    print("API Key not found")
    exit(1)

def get_webhook_token():
    try:
        res = requests.post("https://webhook.site/token")
        if res.status_code in [200, 201]:
            data = res.json()
            return data["uuid"]
    except:
        pass
    return None

def test_veo_generation():
    print("Starting Veo Generation Test...")
    
    wh_uuid = get_webhook_token()
    if not wh_uuid:
        print("Failed to get webhook token")
        return

    callback_url = f"https://webhook.site/{wh_uuid}"
    print(f"Callback URL: {callback_url}")

    generate_url = "https://api.kie.ai/api/v1/veo/generate"
    
    payload = {
        "prompt": "A cinematic drone shot of a modern house in a forest, sunny day, 4k",
        "model": "veo3_fast",
        "aspectRatio": "16:9",
        "callBackUrl": callback_url
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")

    try:
        res = requests.post(generate_url, headers=headers, json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code != 200:
            return

        resp_data = res.json()
        if resp_data.get("code") != 200:
            print("API Error Code")
            return

        task_id = resp_data["data"]["taskId"]
        print(f"Task ID: {task_id}")

        # Polling
        start_ts = time.time()
        poll_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
        
        while True:
            elapsed = time.time() - start_ts
            if elapsed > 180: # 3 mins for fast
                print("Timeout")
                break
            
            try:
                poll_res = requests.get(poll_url, headers=headers)
                if poll_res.status_code == 200:
                    poll_data = poll_res.json()
                    # print(f"Poll Data: {poll_data}")
                    
                    if poll_data.get("code") == 200:
                        data = poll_data["data"]
                        success_flag = data.get("successFlag")
                        print(f"Status: {success_flag}, Msg: {poll_data.get('msg')}")
                        
                        if success_flag == 1:
                            print("Success!")
                            print(f"Full Data: {json.dumps(data, indent=2)}")
                            if "resultUrls" in data:
                                print(f"URLs: {data['resultUrls']}")
                            break
                        elif success_flag in [2, 3]:
                            print(f"Failed: {poll_data.get('msg')}")
                            break
            except Exception as e:
                print(f"Polling error: {e}")
            
            time.sleep(5)

    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_veo_generation()
