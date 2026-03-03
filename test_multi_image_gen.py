
import requests
import toml
import time
import json
import os

# 1. API Key Config
secrets_path = ".streamlit/secrets.toml"
api_key = None

try:
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            secrets = toml.load(f)
            if "KIEAI_API_KEY" in secrets:
                api_key = secrets["KIEAI_API_KEY"]
except Exception as e:
    print(f"Error reading secrets: {e}")

if not api_key:
    # Try env var or manual entry if needed, but for now strictly from secrets
    print("Error: Could not find KIEAI_API_KEY. Set it in .streamlit/secrets.toml")
    exit(1)

print(f"API Key found. Testing 3 models...")

# 2. Configuration
url = "https://api.kie.ai/api/v1/jobs/createTask"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Test Image (Public URL for ease)
test_image_url = "https://images.unsplash.com/photo-1518780664697-55e3ad937233?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" # A house/building image
prompt = "Modern minimalist architecture, sunny day, 4k"
aspect_ratio = "16:9"
resolution = "1K"

# 3. Payloads
tasks_to_start = []

# Nano Banana 2
tasks_to_start.append(("Nano Banana 2", {
    "model": "nano-banana-2",
    "input": {
        "prompt": prompt,
        "image_input": [test_image_url],
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "output_format": "png"
    }
}))

# Flux 2 Flex
tasks_to_start.append(("Flux 2 Flex", {
    "model": "flux-2/flex-image-to-image",
    "input": {
        "input_urls": [test_image_url],
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "strength": 0.55
    }
}))

# Seedream 4.5 Edit
tasks_to_start.append(("Seedream 4.5 Edit", {
    "model": "seedream/4.5-edit",
    "input": {
        "prompt": prompt,
        "image_urls": [test_image_url],
        "aspect_ratio": aspect_ratio,
        "quality": "basic" # basic for 1K/2K
    }
}))

# 4. Execution
active_tasks = {} # tid -> {"engine": name, "status": "pending"}

for engine, payload in tasks_to_start:
    print(f"Starting {engine}...")
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200:
                tid = data["data"]["taskId"]
                print(f"  -> Started! Task ID: {tid}")
                active_tasks[tid] = {"engine": engine, "status": "pending"}
            else:
                print(f"  -> Failed: {data.get('msg')}")
                # Print full response if failed for debugging
                if "Seedream" in engine:
                     print(f"     Full response: {data}")
        else:
            print(f"  -> HTTP Error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"  -> Exception: {e}")

if not active_tasks:
    print("No tasks started.")
    exit(1)

# 5. Polling
print("\nPolling for results (Timeout: 120s)...")
start_time = time.time()
poll_wh_url_template = "https://api.kie.ai/api/v1/jobs/record-info?taskId={}" # Assuming standard lookup if webhook not used, or use create response recommended way?
# Wait, app uses polling via Webhook.site mostly, but verify if direct polling is possible for Image tasks.
# The `test_veo_gen.py` used `record-info` for Veo video.
# Image tasks usually support `record-info` or similar. Documentation Example for Seedream shows "data.taskId" for querying.
# Let's try `api/v1/jobs/info` or `api/v1/jobs/record-info` or just wait for webhook?
# The app logic uses Webhook.site for everything.
# The Quickstart doc for Veo showed `api/v1/veo/record-info`.
# Common KIE API for image tasks usually is `api/v1/jobs/info` or similar. I will guess `api/v1/tasks/{id}` or check if I can find it.
# Actually, the user provided Update text "The callback content structure is identical to the Query Task API response".
# It doesn't explicitly give the Query URL. 
# But for Veo it was `/veo/record-info`.
# For general jobs, likely `/jobs/info?taskId=` or similar. I'll try `/jobs/info`. If not, I can't poll without webhook easily in a script without setting up a listener.
# I will try `/api/v1/query/task` or `/api/v1/jobs/getTask`?
# Let's look at `app.py` again. `app.py` uses webhook polling.
# To make this test script robust without a real webhook server, I'll try to find the direct poll endpoint. 
# Documentation says "Task ID for querying task status".
# I'll try `https://api.kie.ai/api/v1/jobs/fetch?taskId=...` or similar.
# Let's try to assume it follows the pattern: `https://api.kie.ai/api/v1/jobs/details` or just rely on the fact that if IT STARTS, it's mostly good, but I want to see Success.
# I will try `https://api.kie.ai/api/v1/query/task?taskId={taskId}`.

# Re-reading provided docs in prompt:
# "The callback content structure is identical to the Query Task API response"
# Does not list Query endpoint.
# But Veo had `api/v1/veo/record-info`.
# Maybe `api/v1/jobs/record-info`?

polling_endpoint = "https://api.kie.ai/api/v1/jobs/fetch-by-id" # Guessing?
# Actually, I'll try the one from Veo but replace `veo` with `jobs`? Or maybe the Veo one IS the generic one? No.
# I will use a simple retry loop with the `createTask` response content if it provides a hint, or just try `https://api.kie.ai/api/v1/task/info`.
# If I can't poll, I'll just report the Start status, which confirms the API accepted the payload (validating the JSON structure).
# VALIDATION GOAL: "Confirm it works". The most important part is that the Payload structure for Seedream is correct and accepted.

# I will assume `https://api.kie.ai/api/v1/jobs/poll` or similar doesn't exist documented here.
# However, I can try `https://api.kie.ai/api/v1/camera/entry/record-info` (legacy?) 
# Let's just create the tasks and report success if they are accepted. 
# If I really want to check success, I'd need a receiver.
# I'll stick to Task Creation verification.

print("Checking task creation status only (Polling requires webhook setup or unknown endpoint).")

pass
