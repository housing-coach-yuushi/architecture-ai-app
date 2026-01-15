import requests
import time
import json

def verify_webhook():
    print("1. getting token...")
    try:
        res = requests.post("https://webhook.site/token")
        if res.status_code not in [200, 201]:
            print(f"Failed to get token: {res.status_code}")
            return
        
        uuid = res.json()["uuid"]
        print(f"UUID: {uuid}")
        
        callback_url = f"https://webhook.site/{uuid}"
        poll_url = f"https://webhook.site/token/{uuid}/requests"
        
        print(f"Callback: {callback_url}")
        
        # Simulate callback
        print("2. Simulating callback...")
        requests.post(callback_url, json={"data": "test"})
        
        time.sleep(2)
        
        print("3. Checking requests...")
        res = requests.get(poll_url)
        print(f"Poll status: {res.status_code}")
        print(f"Poll content: {res.text[:200]}")
        
        data = res.json()["data"]
        if len(data) > 0:
            print("SUCCESS: Webhook received data.")
        else:
            print("FAILURE: No data in webhook.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_webhook()
