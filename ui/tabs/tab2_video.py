import streamlit as st
import time
from PIL import Image
from services import kie_api
from ui import components

def render(api_key):
    """Render Tab 2: Video Generation (Veo 3.1)"""
    st.subheader("🎥 動画生成 (Veo 3.1)")
    
    gen_type = st.radio("生成タイプ", ["Text to Video", "Image to Video"], horizontal=True)
    model_options = {"Veo 3.1 Fast": "veo3_fast", "Veo 3.1 Quality": "veo3"}
    selected_model_name = st.radio("モデル", list(model_options.keys()), horizontal=True)
    selected_model_id = model_options[selected_model_name]

    input_image_url = None
    v_uploaded_file = None
    
    if gen_type == "Image to Video":
        st.markdown("### 画像 (Image)")
        v_uploaded_file = st.file_uploader("開始フレーム画像をアップロード", type=["jpg", "png", "jpeg", "webp"], key="veo_uploader")
        if v_uploaded_file:
            st.image(v_uploaded_file, caption="Input Image", width=300)

    st.markdown("### 生成プロンプト (Prompt)")
    v_prompt = st.text_area("動画の内容を記述してください", height=100, placeholder="A cinematic shot of...")
    
    col_ar, col_seed = st.columns(2)
    with col_ar:
        aspect_ratio = st.selectbox("比率", ["16:9", "9:16", "1:1", "4:3", "3:4"], index=0, key="veo_ar")
    with col_seed:
        seed = st.number_input("シード (任意, 0=Random)", min_value=0, value=0)
        
    run_btn = st.button("動画を生成する", type="primary", use_container_width=True)
    
    if run_btn:
        if not api_key:
            st.error("API Keyが必要です")
            st.stop()
        if not v_prompt:
            st.error("プロンプトが必要です")
            st.stop()
            
        result_container = st.container()
        with result_container:
            status = st.empty()
            prog = st.progress(0)
            
            try:
                # 1. Image Upload
                image_urls = []
                if gen_type == "Image to Video" and v_uploaded_file:
                    with st.spinner("Uploading image..."):
                        img = Image.open(v_uploaded_file)
                        b64 = kie_api.image_to_base64(img)
                        url = kie_api.upload_image_to_kieai(api_key, b64)
                        if url: image_urls.append(url)
                        else: st.stop()
                
                # 2. Task
                wh_uuid = kie_api.get_webhook_token()
                payload = {
                    "prompt": v_prompt,
                    "model": selected_model_id,
                    "aspectRatio": aspect_ratio,
                    "callBackUrl": kie_api.get_callback_url(wh_uuid)
                }
                if image_urls: payload["imageUrls"] = image_urls
                if seed > 0: payload["seed"] = seed
                
                status.info("Sending task...")
                tid, err = kie_api.create_veo_task(api_key, payload)
                
                if err:
                    st.error(f"Error: {err}")
                    st.stop()
                    
                st.toast(f"Task Started: {tid}")
                
                # 3. Poll
                start_ts = time.time()
                status.markdown(f"**Generating...** (ID: `{tid}`)")
                
                while True:
                    elapsed = time.time() - start_ts
                    if elapsed > 600: break
                    
                    est = 120 if "fast" in selected_model_id else 300
                    prog.progress(min(elapsed / est, 0.95))
                    
                    data = kie_api.poll_veo_task(api_key, tid)
                    if data:
                        flag = data.get("successFlag")
                        if flag == 1:
                            prog.progress(1.0)
                            status.success("Complete!")
                            
                            # Extract URLs
                            # Logic similar to original app.py
                            v_urls = []
                            if "response" in data and "resultUrls" in data["response"]:
                                v_urls = data["response"]["resultUrls"]
                            elif "resultUrls" in data:
                                if isinstance(data["resultUrls"], str):
                                    v_urls = json.loads(data["resultUrls"])
                                else:
                                    v_urls = data["resultUrls"]
                                    
                            for v_url in v_urls:
                                st.video(v_url)
                                st.markdown(f"[Download]({v_url})")
                            break
                        elif flag in [2, 3]:
                            st.error("Failed")
                            break
                    time.sleep(5)
            except Exception as e:
                st.error(f"Error: {e}")
