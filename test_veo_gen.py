
import requests
import toml
import time
import json
import os

# 1. API Keyの取得
secrets_path = ".streamlit/secrets.toml"
api_key = None

try:
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            secrets = toml.load(f)
            if "KIEAI_API_KEY" in secrets:
                api_key = secrets["KIEAI_API_KEY"]
            else:
                 # Check nested dicts just in case, though usually flat or specific sections
                 pass
except Exception as e:
    print(f"Error reading secrets: {e}")

if not api_key:
    print("Error: Could not find KIEAI_API_KEY in .streamlit/secrets.toml")
    exit(1)

print(f"API Key found (length: {len(api_key)})")

# 2. テスト用ペイロード (Text to Video)
url = "https://api.kie.ai/api/v1/veo/generate"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "veo3", # Use quality for testing (fast failed)
    "prompt": "A cinematic drone shot of a modern minimalist house in a forest, sunny day, 4k, high quality",
    "aspectRatio": "16:9",
    "callBackUrl": "https://webhook.site/dummy-callback-for-test"
}

print("Sending request...")
try:
    res = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        if data.get("code") == 200:
            task_id = data["data"]["taskId"]
            print(f"Task ID: {task_id}")
            
            # 3. ポーリング
            poll_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
            
            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                if elapsed > 300: # 5 mins timeout
                    print("Timeout")
                    break
                
                print(f"Polling... ({int(elapsed)}s)")
                p_res = requests.get(poll_url, headers=headers)
                if p_res.status_code == 200:
                    p_data = p_res.json()
                    success_flag = p_data["data"].get("successFlag")
                    
                    if success_flag == 1:
                        print("生成成功！ (Success)")
                        print("Result URLs:", p_data["data"].get("resultUrls"))
                        break
                    elif success_flag in [2, 3]:
                        print("生成失敗 (Failed)")
                        print("Full Response:", json.dumps(p_data, indent=2))
                        break
                
                time.sleep(5)
        else:
            print("API Error:", data)
    else:
        print("HTTP Error:", res.text)
        
except Exception as e:
    print(f"Exception: {e}")
