import streamlit as st
import requests
import json
import base64
import time
from PIL import Image
import io

# --- 設定 ---
# APIキーは st.secrets から取得 (ローカルでは .streamlit/secrets.toml, クラウドではSecrets管理画面で設定)
# APIキーは st.secrets から取得 (ローカルでは .streamlit/secrets.toml, クラウドではSecrets管理画面で設定)
# またはサイドバーから入力
try:
    if "KIEAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["KIEAI_API_KEY"]
    else:
        API_KEY = None
except FileNotFoundError:
    API_KEY = None
except Exception:
    API_KEY = None

if not API_KEY:
    API_KEY = st.sidebar.text_input("KIEAI API Key", type="password")
    if not API_KEY:
        st.error("APIキーが設定されていません。secrets.tomlに設定するか、サイドバーに入力してください。")
        st.stop()

CREATE_TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"

# --- 関数: 画像をBase64文字列に変換 ---
def image_to_base64(image):
    buffered = io.BytesIO()
    # JPEG形式で軽量化して変換（API制限対策）
    image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

# --- 関数: 画像アップロード ---
def upload_image_to_kieai(headers, base64_image):
    upload_url = "https://kieai.redpandaai.co/api/file-base64-upload"
    upload_payload = {
        "base64Data": base64_image,
        "filename": "upload.jpg",
        "uploadPath": "temp"
    }
    try:
        res = requests.post(upload_url, headers=headers, json=upload_payload)
        if res.status_code == 200:
            data = res.json()
            if data.get("success"):
                return data["data"]["downloadUrl"]
    except Exception as e:
        st.error(f"Upload error: {e}")
    return None

# --- 関数: Webhookトークン取得 ---
def get_webhook_token():
    try:
        res = requests.post("https://webhook.site/token")
        if res.status_code in [200, 201]:
            data = res.json()
            return data["uuid"]
    except:
        pass
    return None

# --- UI構築 ---
st.set_page_config(page_title="ishitomo-home AI パース β版", layout="wide")

# カスタムCSSの注入
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', sans-serif;
    }
    
    /* ヘッダーのスタイル */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #eee;
        padding-bottom: 1rem;
    }
    
    /* サブヘッダーのスタイル */
    .sub-header {
        font-size: 1.2rem;
        color: #7F8C8D;
        margin-bottom: 2rem;
    }
    
    /* ボタンのスタイル */
    .stButton > button {
        background-color: #2C3E50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #34495E;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* カード風コンテナ */
    .css-1r6slb0 {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">ishitomo-home AI パース <span style="font-size: 1rem; color: #e74c3c; vertical-align: middle;">β版</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">手書きスケッチや簡易モデルから、フォトリアルな建築パースを生成します。</div>', unsafe_allow_html=True)

# 2カラムレイアウト
col_input, col_result = st.columns([1, 1])

with col_input:
    st.subheader("1. 画像アップロード")
    uploaded_files = st.file_uploader("下絵となる画像をアップロードしてください (複数可)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    # プロンプト設定
    # プロンプト設定
    st.subheader("2. 設定")
    default_prompt = """Create a photorealistic version of the input image.

Do NOT alter or modify the building geometry, proportions, dimensions, window placement, roof line, entrance area, exterior wall lines, or foundation height.  
Preserve every edge, perspective, and shadow boundary exactly as in the input image.  
Keep the original camera position, field of view, and composition unchanged.  
Do NOT crop, rotate, rescale, stretch, or recompose the image.

Render on a **horizontal 4:3 rectangular canvas (landscape orientation, wider than tall)**.  
If the model defaults to square, **expand horizontally** by extending neutral background areas (sky, road, or vegetation) until the exact 4:3 ratio is achieved.  
Do NOT crop or distort the building to fit the ratio.

The building’s front façade (entrance side) must remain perfectly parallel to the road,  
and the road edge must stay perfectly horizontal along the bottom of the frame.  
The camera must face the building front perpendicularly (no diagonal or angled view).  
No tilt-shift or perspective correction.

---

### 🌿 Exterior & Lighting – Luxury Emphasis
Do **not** include any vehicles.  
Focus entirely on **landscaping, lighting, and material realism** to convey luxury and architectural refinement.  

Design the **exterior space** (driveway, entrance approach, garden, boundary area)  
to reflect a **high-end Japanese residence** — elegant, calm, and spatially balanced.  
Use a **concrete or stone-paved forecourt** with clean, precise joint lines.  
Add tasteful exterior elements such as **low walls (H=0.6–0.9 m), stone planters, bollard or post lights, and minimalist gate posts**,  
all aligned parallel to the building and the road.

Use **soft directional daylight** from SE–SW (45–60° azimuth, 30–45° altitude).  
Simulate gentle **“komorebi” dappled sunlight** filtering through nearby trees,  
creating dynamic shadows that reveal surface depth and material richness.  
Let the light emphasize the geometry and edges of the architecture."""

    prompt = st.text_area(
        "プロンプト (どのような建物にしたいか)", 
        value=default_prompt,
        height=300
    )
    
    # 重要なパラメータ
    # パラメータ設定
    col1, col2 = st.columns(2)
    with col1:
        strength = st.slider("プロンプトの影響度 (Strength)", 0.0, 1.0, 0.55, help="0に近いほど元画像に忠実、1に近いほどプロンプト重視")
    with col2:
        resolution = st.selectbox("解像度 (Resolution)", ["1K", "2K"], index=0, help="Flux 2のみ有効")
    
    aspect_ratio = st.selectbox("アスペクト比", ["16:9", "1:1", "9:16", "4:3", "3:4"], index=0)
    
    # エンジン選択
    engine_display = st.selectbox(
        "生成エンジン", 
        ["nano-banana-pro", "flux-2/flex-image-to-image", "Seedream 4.5", "Z-Image"], 
        index=2
    )
    
    # 表示名からモデルIDへのマッピング
    if "nano-banana" in engine_display:
        engine = "nano-banana-pro"
    elif "flux-2/flex" in engine_display:
        engine = "flux-2/flex-image-to-image"
    elif "Seedream" in engine_display:
        engine = "seedream/4.5-text-to-image"
    elif "Z-Image" in engine_display:
        engine = "z-image"
    else:
        engine = "nano-banana-pro" # Default fallback

    run_button = st.button("パースを生成する", type="primary")

# --- 実行処理 ---
if run_button and uploaded_files:
    with col_result:
        st.subheader("3. 結果")
        
        try:
            with st.spinner('画像を処理してAPIに送信中...'):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }

                # 1. 画像の前処理 & アップロード (複数対応)
                input_urls = []
                
                # Seedream/Z-Imageはtext-to-imageモデルだが、アプリのフロー上画像アップロードがある。
                # 現状のドキュメントにはimage inputがないが、他のモデルと同様にアップロード処理は残しておく
                
                for i, uploaded_file in enumerate(uploaded_files):
                    image = Image.open(uploaded_file)
                    
                    # デバッグ: 画像表示
                    with st.expander(f"送信画像を確認 ({i+1})"):
                        st.image(image, caption=f"Image {i+1}", use_container_width=True)
                    
                    # リサイズ
                    image.thumbnail((1024, 1024)) 
                    base64_image = image_to_base64(image)
                    
                    # アップロード (共通)
                    st.text(f"画像をアップロード中 ({i+1})...")
                    img_url = upload_image_to_kieai(headers, base64_image)
                    if img_url:
                        input_urls.append(img_url)
                    else:
                        st.error(f"画像のアップロードに失敗しました ({i+1})")
                        st.stop()
                
                if not input_urls:
                     st.error("画像が正しくアップロードされませんでした。")
                     st.stop()
                
                st.success(f"{len(input_urls)} 枚の画像をアップロードしました。")

                # B. Webhookトークン取得
                wh_uuid = get_webhook_token()
                if not wh_uuid:
                    st.error("Webhookトークンの取得に失敗しました。")
                    st.stop()
                callback_url = f"https://webhook.site/{wh_uuid}"
                
                # C. ペイロード作成 (エンジン別)
                url = "https://api.kie.ai/api/v1/jobs/createTask"
                
                if engine == "nano-banana-pro":
                    payload = {
                        "model": "nano-banana-pro",
                        "callBackUrl": callback_url,
                        "input": {
                            "prompt": prompt,
                            "image_input": input_urls, # リストを渡す
                            "aspect_ratio": aspect_ratio,
                            "output_format": "png"
                        }
                    }
                elif engine == "seedream/4.5-text-to-image":
                    payload = {
                        "model": "seedream/4.5-text-to-image",
                        "callBackUrl": callback_url,
                        "input": {
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio,
                            "quality": "high" # Default to high
                        }
                    }
                elif engine == "z-image":
                    # Z-Image has a max prompt length of 1000 characters
                    truncated_prompt = prompt[:1000]
                    if len(prompt) > 1000:
                        st.warning("⚠️ Z-Imageの制限により、プロンプトが1000文字に短縮されました。")
                    
                    payload = {
                        "model": "z-image",
                        "callBackUrl": callback_url,
                        "input": {
                            "prompt": truncated_prompt,
                            "aspect_ratio": aspect_ratio
                        }
                    }
                else: # Flux 2 Flex
                    payload = {
                        "model": engine,
                        "callBackUrl": callback_url,
                        "input": {
                            "input_urls": input_urls, # リストを渡す
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio if aspect_ratio != "auto" else "1:1",
                            "resolution": resolution,
                            "strength": strength
                        }
                    }
                        

                # デバッグ: ペイロード確認
                with st.expander("デバッグ情報 (JSON Payload)"):
                    debug_payload = payload.copy()
                    if "image" in debug_payload:
                        debug_payload["image"] = debug_payload["image"][:50] + "..."
                    st.json(debug_payload)

                # 3. API送信
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                # 4. レスポンス処理
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("code") == 200 and "data" in result:
                        task_id = result["data"]["taskId"]
                        st.info(f"タスクが開始されました。ID: {task_id}")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # ポーリング処理
                        if engine in ["nano-banana-pro", "flux-2/flex-image-to-image", "seedream/4.5-text-to-image", "z-image"]:
                            # Webhookをポーリング
                            poll_wh_url = f"https://webhook.site/token/{wh_uuid}/requests"
                            
                            st.write(f"Webhook モニター: [リンク](https://webhook.site/#!/{wh_uuid})")
                            
                            # 手動入力フォールバック
                            with st.expander("⚠️ 結果が反映されない場合 (手動入力)"):
                                st.markdown("Webhook Monitorに届いたJSON全体をここに貼り付けてください。")
                                manual_json = st.text_area("コールバック JSON", height=150)
                                if st.button("JSONから結果を表示"):
                                    try:
                                        body = json.loads(manual_json)
                                        data = body.get("data", {})
                                        
                                        # resultUrlsが直接ある場合 (一部のエンジン)
                                        if "resultUrls" in data and isinstance(data["resultUrls"], list):
                                            result_urls = data["resultUrls"]
                                            if result_urls:
                                                cols = st.columns(2)
                                                for idx, url in enumerate(result_urls):
                                                    with cols[idx % 2]:
                                                        st.image(url, caption=f"生成結果 {idx+1}")
                                                st.success("生成完了！")
                                                progress_bar.progress(1.0)
                                        
                                        # resultJson文字列がある場合 (標準)
                                        elif "resultJson" in data:
                                            res_json_str = data["resultJson"]
                                            if res_json_str:
                                                res_json = json.loads(res_json_str)
                                                if "resultUrls" in res_json and res_json["resultUrls"]:
                                                    image_url = res_json["resultUrls"][0]
                                                    st.image(image_url, caption="生成結果 (手動読込)")
                                                    st.success("生成完了！")
                                                    progress_bar.progress(1.0)
                                    except Exception as e:
                                        st.error(f"JSON解析エラー: {e}")

                            with st.expander("Webhook ポーリングログ"):
                                log_container = st.empty()
                                logs = []
                                logs.append(f"タスクIDを検索中: {task_id}")

                            for i in range(150): # 最大300秒待機 (2s * 150)
                                try:
                                    wh_reqs = requests.get(poll_wh_url, timeout=10)
                                    if wh_reqs.status_code == 200:
                                        reqs_data = wh_reqs.json()
                                        data_list = reqs_data.get("data", [])
                                        
                                        found = False
                                        if data_list:
                                            for req in data_list:
                                                content = req.get("content")
                                                if content:
                                                    try:
                                                        body = json.loads(content)
                                                        received_task_id = body.get("data", {}).get("taskId")
                                                        
                                                        # ログに記録（最新のものをいくつか）
                                                        if len(logs) < 10:
                                                            logs.append(f"タスクIDのリクエストを発見: {received_task_id}")
                                                        
                                                        if received_task_id == task_id:
                                                            found = True
                                                            
                                                            # 共通の判定 (stateがある)
                                                            state = body.get("data", {}).get("state")
                                                            status_text.text(f"生成中... (状態: {state})")
                                                            
                                                            logs.append(f"一致! 状態: {state}")
                                                            log_container.write(logs)
                                                            
                                                            if state == "success":
                                                                res_json_str = body["data"].get("resultJson")
                                                                if res_json_str:
                                                                    res_json = json.loads(res_json_str)
                                                                    if "resultUrls" in res_json and res_json["resultUrls"]:
                                                                        image_url = res_json["resultUrls"][0]
                                                                        st.image(image_url, caption="生成結果")
                                                                        st.success("生成完了！")
                                                                        progress_bar.progress(1.0)
                                                                        break
                                                            elif state == "fail":
                                                                st.error(f"生成に失敗しました: {body.get('msg')}")
                                                                break
                                                    except:
                                                        pass
                                        if found:
                                            break
                                            
                                    status_text.text(f"生成中... ({i*2}秒経過)")
                                    log_container.write(logs)
                                    time.sleep(2)
                                except Exception as e:
                                    status_text.text(f"待機中... ({e})")
                                    logs.append(f"エラー: {e}")
                                    log_container.write(logs)
                                    time.sleep(2)
                            else:
                                st.error("タイムアウトしました（300秒）。Webhook Monitorリンクから結果が届いているか確認してください。")
                    else:
                        st.error("APIエラー: " + result.get("msg", "不明なエラー"))
                        st.json(result)

                else:
                    st.error(f"APIエラーが発生しました (Status: {response.status_code})")
                    st.text(response.text)

        except Exception as e:
            st.error(f"システムエラー: {e}")

elif run_button and not uploaded_files:
    st.warning("画像をアップロードしてください。")

# --- フッター (Credits) ---
st.markdown("""
<div style="
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: rgba(255, 255, 255, 0.9);
    color: #95a5a6;
    text-align: center;
    padding: 10px;
    font-size: 0.8rem;
    border-top: 1px solid #eee;
    z-index: 999;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: 1px;
">
    <span style="font-weight: 600;">Produced by WebTeam Naka</span>
    <span style="margin: 0 10px;">|</span>
    <span>Contact: naka / nakashima</span>
</div>
<div style="margin-bottom: 60px;"></div>
""", unsafe_allow_html=True)
