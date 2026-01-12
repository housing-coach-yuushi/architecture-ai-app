import streamlit as st
import time
import json
from PIL import Image
from services import kie_api
from ui import components
import db

def render(api_key):
    """Render Tab 1: AI Parse Generation"""
    col_input, col_result = st.columns([1, 1])

    with col_input:
        st.subheader("1. 画像アップロード")
        uploaded_files = st.file_uploader("下絵となる画像をアップロードしてください (複数可)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        # プロンプト設定
        st.subheader("2. 設定")
        default_prompt = """添付の建築パースをフォトリアルにしてください。
建物の形状・構成・アングル・奥行・カメラ位置・パースラインは絶対に変更しないでください。
素材・質感・光の表現だけを実写に寄せてください。

【必ず守ってほしい内容】
・外観の形状を一切変えない
・窓の位置、壁のライン、屋根形状、陰影の付き方の方向はそのまま
・広角率を変えない
・縦横比（例：3:4、横長）を維持
・背景の構成を変えない（変更したい場合は指定する）

【今回のフォトリアル化条件】
・外壁は窯業系サイディングの質感を出す
・道路はアスファルトの質感を出す
・背景：住宅街
・コンクリート反射：なし
・窓ガラス反射：あり
・天候：晴れ
・人物：不要

【重要】
建物の形状や寸法感が変わるような解釈は絶対にしないでください。
元画像の輪郭線と構造はそのまま、質感だけを高精細フォトリアルに仕上げてください。"""

        prompt = st.text_area(
            "プロンプト (どのような建物にしたいか)", 
            value=default_prompt,
            height=300
        )
        
        # パラメータ設定
        col1, col2 = st.columns(2)
        with col1:
            strength = st.slider("プロンプトの影響度 (Strength)", 0.0, 1.0, 0.55, help="0に近いほど元画像に忠実、1に近いほどプロンプト重視")
        with col2:
            resolution = st.selectbox("解像度 (Resolution)", ["1K", "2K", "4K"], index=0, help="Seedream / Nano Banana Pro / Flux 2")
        
        aspect_ratio = st.selectbox("アスペクト比", ["16:9", "1:1", "9:16", "4:3", "3:4"], index=0)
        
        # モデル選択
        model_options = ["Nano Banana Pro", "Flux 2 Flex", "Seedream 4.5 Edit", "GPT Image 1.5"]
        selected_models = st.multiselect("使用するモデル (複数選択可)", model_options, default=["Seedream 4.5 Edit", "Nano Banana Pro", "Flux 2 Flex"])
        
        st.info(f"ℹ️ 選択された {len(selected_models)} つのエンジンで同時に生成します。")

        run_button = st.button("パースを生成する", type="primary")

    # --- 実行処理 ---
    if run_button and uploaded_files:
        if not api_key:
            st.error("KIEAI API Keyが必要です。")
            st.stop()

        with col_result:
            st.subheader("3. 結果ギャラリー")
            
            try:
                with st.spinner('画像を処理してAPIに送信中...'):
                    # 1. 画像アップロード
                    input_urls = []
                    for i, uploaded_file in enumerate(uploaded_files):
                        image = Image.open(uploaded_file)
                        image.thumbnail((1024, 1024)) 
                        base64_image = kie_api.image_to_base64(image)
                        
                        img_url = kie_api.upload_image_to_kieai(api_key, base64_image)
                        if img_url:
                            input_urls.append(img_url)
                        else:
                            st.error(f"画像のアップロードに失敗しました ({i+1})")
                            st.stop()
                    
                    if not input_urls:
                         st.stop()
                    
                    # 2. Webhook
                    wh_uuid = kie_api.get_webhook_token()
                    if not wh_uuid:
                        st.error("Webhookトークンの取得に失敗しました。")
                        st.stop()
                    callback_url = kie_api.get_callback_url(wh_uuid)
                    
                    # 3. タスク作成
                    tasks = {} 
                    
                    for img_idx, single_img_url in enumerate(input_urls):
                        img_label = f"#{img_idx + 1}"
                        single_input_list = [single_img_url]

                        if "Nano Banana Pro" in selected_models:
                            tid, msg = kie_api.create_kie_task(api_key, {
                                "model": "nano-banana-pro",
                                "callBackUrl": callback_url,
                                "input": {
                                    "prompt": prompt,
                                    "image_input": single_input_list,
                                    "aspect_ratio": aspect_ratio,
                                    "resolution": resolution,
                                    "output_format": "png"
                                }
                            })
                            if tid: tasks[tid] = {"engine": f"Nano Banana Pro {img_label}", "status": "pending", "result_url": None}

                        if "Flux 2 Flex" in selected_models:
                            flux_resolution = "2K" if resolution == "4K" else resolution
                            tid, msg = kie_api.create_kie_task(api_key, {
                                "model": "flux-2/flex-image-to-image",
                                "callBackUrl": callback_url,
                                "input": {
                                    "input_urls": single_input_list,
                                    "prompt": prompt,
                                    "aspect_ratio": aspect_ratio if aspect_ratio != "auto" else "1:1",
                                    "resolution": flux_resolution,
                                    "strength": strength
                                }
                            })
                            if tid: tasks[tid] = {"engine": f"Flux 2 Flex {img_label}", "status": "pending", "result_url": None}

                        if "Seedream 4.5 Edit" in selected_models:
                            sd_quality = "high" if resolution == "4K" else "basic"
                            tid, msg = kie_api.create_kie_task(api_key, {
                                "model": "seedream/4.5-edit",
                                "callBackUrl": callback_url,
                                "input": {
                                    "prompt": prompt,
                                    "image_urls": single_input_list,
                                    "aspect_ratio": aspect_ratio,
                                    "quality": sd_quality
                                }
                            })
                            if tid: tasks[tid] = {"engine": f"Seedream 4.5 Edit {img_label}", "status": "pending", "result_url": None}
                            
                        if "GPT Image 1.5" in selected_models:
                            gpt_ar_mapping = {"16:9": "3:2", "9:16": "2:3", "1:1": "1:1", "4:3": "3:2", "3:4": "2:3"}
                            gpt_aspect = gpt_ar_mapping.get(aspect_ratio, "3:2")
                            gpt_quality = "high" if resolution == "4K" else "medium"
                            gpt_prompt = prompt[:1000] if len(prompt) > 1000 else prompt
                            
                            tid, msg = kie_api.create_kie_task(api_key, {
                                "model": "gpt-image/1.5-image-to-image",
                                "callBackUrl": callback_url,
                                "input": {
                                    "input_urls": single_input_list,
                                    "prompt": gpt_prompt,
                                    "aspect_ratio": gpt_aspect,
                                    "quality": gpt_quality
                                }
                            })
                            if tid: tasks[tid] = {"engine": f"GPT Image 1.5 {img_label}", "status": "pending", "result_url": None}

                    if not tasks:
                        st.stop()
                        
                    st.toast(f"{len(tasks)}件のタスクを開始しました")

                    # 4. ポーリングループ
                    poll_loop(tasks, wh_uuid, prompt, col_result)
                    
            except Exception as e:
                st.error(f"システムエラー: {e}")

    elif run_button and not uploaded_files:
        st.warning("画像をアップロードしてください。")

    # --- Community Gallery ---
    st.markdown("---")
    st.subheader("🌐 コミュニティギャラリー")
    render_community_gallery()

def poll_loop(tasks, wh_uuid, prompt, container):
    """Polling logic for tasks."""
    progress_bar = st.progress(0)
    gallery_placeholder = st.empty()
    poll_url = kie_api.get_poll_url(wh_uuid)
    
    start_time = time.time()
    while True:
        if time.time() - start_time > 300:
            st.error("タイムアウトしました。")
            break
            
        pending_tasks = [tid for tid, info in tasks.items() if info["status"] == "pending"]
        if not pending_tasks:
            progress_bar.progress(1.0)
            st.success("全タスク完了！")
            break
        
        # update UI
        elapsed = time.time() - start_time
        progress_bar.progress(min(elapsed / 60, 0.95))
        
        # Fetch webhooks
        try:
            res = requests.get(poll_url, timeout=10)
            if res.status_code == 200:
                data_list = res.json().get("data", [])
                for req in data_list:
                    content = req.get("content")
                    if content:
                        try:
                            body = json.loads(content)
                            data_body = body.get("data", {})
                            rec_tid = data_body.get("taskId")
                            
                            if rec_tid in tasks and tasks[rec_tid]["status"] == "pending":
                                state = data_body.get("state")
                                if state == "success":
                                    res_url = None
                                    if "resultUrls" in data_body and data_body["resultUrls"]:
                                        res_url = data_body["resultUrls"][0]
                                    elif "resultJson" in data_body:
                                         rj = json.loads(data_body["resultJson"])
                                         if "resultUrls" in rj: res_url = rj["resultUrls"][0]
                                    
                                    if res_url:
                                        tasks[rec_tid]["status"] = "success"
                                        tasks[rec_tid]["result_url"] = res_url
                                        tasks[rec_tid]["image_url"] = res_url # for unified UI
                                        tasks[rec_tid]["label"] = tasks[rec_tid]["engine"]
                                        st.toast(f"{tasks[rec_tid]['engine']} 完了！")
                                        db.save_result(res_url, prompt, tasks[rec_tid]['engine'])
                                elif state == "fail":
                                    tasks[rec_tid]["status"] = "failed"
                                    tasks[rec_tid]["label"] = tasks[rec_tid]["engine"]
                        except: pass
        except: pass
        
        # Render Gallery
        with gallery_placeholder.container():
            components.render_gallery_grid(list(tasks.values()))
        
        time.sleep(3)

def render_community_gallery():
    if not db.get_connection():
         st.warning("DB未接続のためギャラリーは表示されません")
         return
         
    recent_results = db.get_recent_results(limit=50) # This will be cached later
    if recent_results:
        cols = st.columns(4)
        for idx, record in enumerate(recent_results):
            with cols[idx % 4]:
                try:
                    url = record['image_url']
                    if url and (url.endswith(".mp4") or url.endswith(".mov")):
                        st.video(url)
                    else:
                        st.image(url, use_container_width=True)
                    st.caption(f"{record['engine']}")
                except: pass
    else:
        st.info("No records found.")
