import requests
import json
import base64
import io
import time
import streamlit as st
from PIL import Image

# --- API Constants ---
CREATE_TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"
UPLOAD_URL = "https://kieai.redpandaai.co/api/file-base64-upload"
VEO_GEN_URL = "https://api.kie.ai/api/v1/veo/generate"
JOBS_RECORD_INFO_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"

# --- Image Processing ---
def image_to_base64(image):
    """Convert PIL Image to Base64 string (JPEG format)."""
    buffered = io.BytesIO()
    # RGBA (Transparency) -> RGB (JPEG compatible)
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")
    # Optimize as JPEG with 90% quality
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def upload_image_to_kieai(api_key, base64_image):
    """Upload base64 image to KIE AI temporary storage."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    upload_payload = {
        "base64Data": base64_image,
        "filename": "upload.jpg",
        "uploadPath": "temp"
    }
    try:
        res = requests.post(UPLOAD_URL, headers=headers, json=upload_payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                return data["data"]["downloadUrl"]
        else:
            st.error(f"Upload failed: {res.status_code} - {res.text}")
    except Exception as e:
        st.error(f"Upload error: {e}")
    return None

def get_webhook_token():
    """Get a fresh webhook token from webhook.site with retries."""
    for i in range(3):
        try:
            res = requests.post("https://webhook.site/token", timeout=10)
            if res.status_code in [200, 201]:
                data = res.json()
                return data["uuid"]
        except Exception as e:
            print(f"Webhook token fetch error (attempt {i+1}): {e}")
        time.sleep(1)
    return None

def get_callback_url(uuid):
    return f"https://webhook.site/{uuid}"

def get_poll_url(uuid):
    return f"https://webhook.site/token/{uuid}/requests"

# --- Task Execution ---
def create_kie_task(api_key, payload):
    """Create a generic KIE AI task."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        print(f"[DEBUG] Sending request to {CREATE_TASK_URL}")
        print(f"[DEBUG] Model: {payload.get('model')}")
        res = requests.post(CREATE_TASK_URL, headers=headers, json=payload, timeout=30)
        print(f"[DEBUG] Response status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"[DEBUG] Response data: {data}")
            if data.get("code") == 200:
                return data["data"]["taskId"], None
            else:
                return None, data.get("msg")
        else:
            return None, f"HTTP {res.status_code}: {res.text[:200]}"
    except Exception as e:
        print(f"[DEBUG] Exception in create_kie_task: {type(e).__name__}: {e}")
        return None, f"{type(e).__name__}: {str(e)}"

def create_veo_task(api_key, payload):
    """Create a Veo 3.1 video generation task."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        res = requests.post(VEO_GEN_URL, headers=headers, json=payload, timeout=30)
        if res.status_code != 200:
            return None, f"API Error ({res.status_code}): {res.text}"
        
        data = res.json()
        if data.get("code") != 200:
            return None, f"Request Failed: {data.get('msg')}"
            
        return data["data"]["taskId"], None
    except Exception as e:
        return None, str(e)

def poll_veo_task(api_key, task_id):
    """Poll status for Veo task."""
    url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200:
                return data["data"]
    except:
        pass
    return None

def poll_task(api_key, task_id):
    """Poll task status directly from KIE AI API."""
    # Note: verified that gpt4o-image endpoint works for polling generically
    url = f"https://api.kie.ai/api/v1/gpt4o-image/record-info?taskId={task_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200:
                return data["data"]
    except:
        pass
    return None

def create_kling3_video_task(api_key, input_payload, callback_url=None):
    """Create a Kling 3.0 video generation task."""
    payload = {
        "model": "kling-3.0/video",
        "input": input_payload
    }
    if callback_url:
        payload["callBackUrl"] = callback_url
    return create_kie_task(api_key, payload)

def poll_job_record(api_key, task_id):
    """Poll generic KIE jobs record-info endpoint."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    url = f"{JOBS_RECORD_INFO_URL}?taskId={task_id}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None, f"HTTP {res.status_code}: {res.text[:200]}"
        body = res.json()
        if body.get("code") != 200:
            return None, body.get("msg", "Unknown API error")
        return body.get("data", {}), None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def extract_result_urls(task_data):
    """Normalize result URLs from task payload variations."""
    if not isinstance(task_data, dict):
        return []

    urls = []
    raw_result_json = task_data.get("resultJson")
    if isinstance(raw_result_json, str) and raw_result_json.strip():
        try:
            parsed = json.loads(raw_result_json)
            parsed_urls = parsed.get("resultUrls")
            if isinstance(parsed_urls, list):
                urls.extend([u for u in parsed_urls if isinstance(u, str) and u.strip()])
            elif isinstance(parsed_urls, str) and parsed_urls.strip():
                urls.append(parsed_urls)
        except Exception:
            pass

    direct_urls = task_data.get("resultUrls")
    if isinstance(direct_urls, list):
        urls.extend([u for u in direct_urls if isinstance(u, str) and u.strip()])
    elif isinstance(direct_urls, str) and direct_urls.strip():
        try:
            parsed_direct = json.loads(direct_urls)
            if isinstance(parsed_direct, list):
                urls.extend([u for u in parsed_direct if isinstance(u, str) and u.strip()])
            else:
                urls.append(direct_urls)
        except Exception:
            urls.append(direct_urls)

    deduped = []
    seen = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped
