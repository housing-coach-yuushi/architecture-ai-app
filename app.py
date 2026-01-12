import streamlit as st
import requests
import json
import base64
import time
from PIL import Image
import io
import db  # Import database module

import google.generativeai as genai

# --- 設定 ---
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
        st.warning("KIEAI APIキーが設定されていません。画像生成機能は使用できません。")

# Gemini API Key
try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    else:
        GEMINI_API_KEY = None
except:
    GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("Gemini API Key (for Auto Categorization)", type="password")

CREATE_TASK_URL = "https://api.kie.ai/api/v1/jobs/createTask"

# --- 関数: 画像をBase64文字列に変換 ---
def image_to_base64(image):
    buffered = io.BytesIO()
    # RGBA (透過) 画像の場合はRGBに変換 (JPEG対応のため)
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGB")
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

# --- 関数: Geminiで画像を分類 ---
def categorize_image_with_gemini(image_bytes):
    if not GEMINI_API_KEY:
        return None, "API Key Missing"
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        
        prompt = """
        この画像を解析し、以下のカテゴリのいずれか1つに分類してください:
        [リビング, ダイニング, キッチン, 寝室, バスルーム, 玄関, 外観, 庭, その他]
        
        また、画像の内容を短い日本語で説明してください（最大20文字）。
        
        結果を以下のJSON形式で返してください:
        {
            "category": "カテゴリ名",
            "description": "短い説明"
        }
        """
        
        response = model.generate_content([prompt, image_part])
        text = response.text
        # JSON部分を抽出 (Markdownのコードブロックを除去)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        return json.loads(text)
    except Exception as e:
        return None, str(e)

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

    /* ギャラリーアイテムのスタイル改善 */
    .gallery-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s;
        margin-bottom: 1rem;
    }
    .gallery-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }
    .gallery-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .gallery-content {
        padding: 12px;
    }
    .gallery-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
        font-size: 1rem;
    }
    .gallery-desc {
        color: #666;
        font-size: 0.85rem;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">ishitomo-home AI パース <span style="font-size: 1rem; color: #e74c3c; vertical-align: middle;">β版</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">手書きスケッチや簡易モデルから、フォトリアルな建築パースを生成します。</div>', unsafe_allow_html=True)

# --- タブの作成 ---
# --- タブの作成 ---
tab1, tab2, tab3 = st.tabs(["🏠 AIパース生成", "🎥 動画生成", "📐 間取り作成"])

# ==========================================
# Tab 3: 間取り作成
# ==========================================
with tab3:
    st.subheader("📐 間取り作成")
    st.markdown("""
    ブラウザで動作する間取り作成ツールです。
    簡単な操作で平面図を作成し、AIパース生成や3D化に使用できます。
    """)
    
    st.markdown("### ✨ 機能")
    st.markdown("""
    - **ドラッグ&ドロップ**で部屋を配置
    - **ワンクリック**で窓やドアを追加
    - 作成した間取りを**画像としてダウンロード**して、このAIアプリでパース化可能
    """)
    
    st.link_button("間取り作成アプリを開く (marori app)", "https://blueprint-js-app.vercel.app/sales-mode.html", type="primary")
    
    st.info("💡 ヒント: 作成画面で「AIアプリへ送る」ボタンを押すと、画像がダウンロードされ、スムーズにこのアプリに取り込めます。")

# ==========================================
# Tab 1: AIパース生成
# ==========================================
with tab1:
    # 2カラムレイアウト
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
        if not API_KEY:
            st.error("KIEAI API Keyが必要です。")
            st.stop()

        with col_result:
            st.subheader("3. 結果ギャラリー")
            
            try:
                with st.spinner('画像を処理してAPIに送信中...'):
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    }

                    # 1. 画像の前処理 & アップロード (複数対応)
                    input_urls = []
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        image = Image.open(uploaded_file)
                        
                        # リサイズ
                        image.thumbnail((1024, 1024)) 
                        base64_image = image_to_base64(image)
                        
                        # アップロード (共通)
                        img_url = upload_image_to_kieai(headers, base64_image)
                        if img_url:
                            input_urls.append(img_url)
                        else:
                            st.error(f"画像のアップロードに失敗しました ({i+1})")
                            st.stop()
                    
                    if not input_urls:
                         st.error("画像が正しくアップロードされませんでした。")
                         st.stop()
                    
                    # B. Webhookトークン取得
                    wh_uuid = get_webhook_token()
                    if not wh_uuid:
                        st.error("Webhookトークンの取得に失敗しました。")
                        st.stop()
                    callback_url = f"https://webhook.site/{wh_uuid}"
                    
                    # C. タスク作成
                    url = "https://api.kie.ai/api/v1/jobs/createTask"
                    
                    tasks = {} # {task_id: {"engine": name, "status": "pending", "result_url": None}}
                    
                    # Payloads construction
                    payloads = []
                    
                    # Iterate over each uploaded image to create separate tasks
                    for img_idx, single_img_url in enumerate(input_urls):
                        img_label = f"#{img_idx + 1}"
                        single_input_list = [single_img_url] # API expects a list

                        # 1. Nano Banana Pro
                        if "Nano Banana Pro" in selected_models:
                            payloads.append((f"Nano Banana Pro {img_label}", {
                                "model": "nano-banana-pro",
                                "callBackUrl": callback_url,
                                "input": {
                                    "prompt": prompt,
                                    "image_input": single_input_list,
                                    "aspect_ratio": aspect_ratio,
                                    "resolution": resolution,
                                    "output_format": "png"
                                }
                            }))
                        
                        # 2. Flux 2 Flex
                        if "Flux 2 Flex" in selected_models:
                            # Fix: Flux 2 does not support 4K, so map 4K -> 2K
                            flux_resolution = "2K" if resolution == "4K" else resolution
                            
                            payloads.append((f"Flux 2 Flex {img_label}", {
                                "model": "flux-2/flex-image-to-image",
                                "callBackUrl": callback_url,
                                "input": {
                                    "input_urls": single_input_list,
                                    "prompt": prompt,
                                    "aspect_ratio": aspect_ratio if aspect_ratio != "auto" else "1:1",
                                    "resolution": flux_resolution,
                                    "strength": strength
                                }
                            }))

                        # 3. Seedream 4.5 Edit
                        if "Seedream 4.5 Edit" in selected_models:
                            # Quality param mapping
                            sd_quality = "high" if resolution == "4K" else "basic"
                            
                            payloads.append((f"Seedream 4.5 Edit {img_label}", {
                                "model": "seedream/4.5-edit",
                                "callBackUrl": callback_url,
                                "input": {
                                    "prompt": prompt,
                                    "image_urls": single_input_list,
                                    "aspect_ratio": aspect_ratio,
                                    "quality": sd_quality
                                }
                            }))
                        
                        # 4. GPT Image 1.5 (KIE AI)
                        if "GPT Image 1.5" in selected_models:
                            # GPT Image 1.5のアスペクト比マッピング (サポート: 1:1, 2:3, 3:2)
                            gpt_ar_mapping = {
                                "16:9": "3:2",  # 横長 -> 3:2
                                "9:16": "2:3",  # 縦長 -> 2:3
                                "1:1": "1:1",   # 正方形
                                "4:3": "3:2",   # 横長 -> 3:2
                                "3:4": "2:3"    # 縦長 -> 2:3
                            }
                            gpt_aspect = gpt_ar_mapping.get(aspect_ratio, "3:2")
                            
                            # Quality: 4Kの場合はhigh、それ以外はmedium
                            gpt_quality = "high" if resolution == "4K" else "medium"
                            
                            # プロンプトを最大1000文字に切り詰め (API制限)
                            gpt_prompt = prompt[:1000] if len(prompt) > 1000 else prompt
                            
                            payloads.append((f"GPT Image 1.5 {img_label}", {
                                "model": "gpt-image/1.5-image-to-image",
                                "callBackUrl": callback_url,
                                "input": {
                                    "input_urls": single_input_list,
                                    "prompt": gpt_prompt,
                                    "aspect_ratio": gpt_aspect,
                                    "quality": gpt_quality
                                }
                            }))

                    # Send Requests
                    for engine_name, payload in payloads:
                        try:
                            res = requests.post(url, headers=headers, data=json.dumps(payload))
                            if res.status_code == 200:
                                r_data = res.json()
                                if r_data.get("code") == 200:
                                    tid = r_data["data"]["taskId"]
                                    tasks[tid] = {"engine": engine_name, "status": "pending", "result_url": None}
                                    st.toast(f"{engine_name} タスク開始: {tid}")
                                else:
                                    st.error(f"{engine_name} 開始エラー: {r_data.get('msg')}")
                            else:
                                st.error(f"{engine_name} APIエラー: {res.status_code}")
                        except Exception as e:
                            st.error(f"{engine_name} 送信エラー: {e}")

                    if not tasks:
                        st.stop()

                    # D. ポーリング & ギャラリー表示
                    st.markdown("### 生成中...")
                    progress_bar = st.progress(0)
                    gallery_placeholder = st.empty()
                    
                    poll_wh_url = f"https://webhook.site/token/{wh_uuid}/requests"
                    
                    # ポーリングループ
                    start_time = time.time()
                    while True:
                        # タイムアウト判定 (300秒)
                        if time.time() - start_time > 300:
                            st.error("タイムアウトしました。")
                            break
                            
                        # 全タスク完了判定
                        pending_tasks = [tid for tid, info in tasks.items() if info["status"] == "pending"]
                        if not pending_tasks:
                            progress_bar.progress(1.0)
                            st.success("全タスク完了！")
                            break
                        
                        # 進捗バー更新 (簡易)
                        elapsed = time.time() - start_time
                        progress_bar.progress(min(elapsed / 60, 0.95)) # 60秒で95%まで
                        
                        try:
                            wh_reqs = requests.get(poll_wh_url, timeout=10)
                            if wh_reqs.status_code == 200:
                                reqs_data = wh_reqs.json()
                                data_list = reqs_data.get("data", [])
                                
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
                                                    # 結果URL取得
                                                    res_url = None
                                                    if "resultUrls" in data_body and data_body["resultUrls"]:
                                                        res_url = data_body["resultUrls"][0]
                                                    elif "resultJson" in data_body:
                                                        rj = json.loads(data_body["resultJson"])
                                                        if "resultUrls" in rj and rj["resultUrls"]:
                                                            res_url = rj["resultUrls"][0]
                                                    
                                                    if res_url:
                                                        tasks[rec_tid]["status"] = "success"
                                                        tasks[rec_tid]["result_url"] = res_url
                                                        st.toast(f"{tasks[rec_tid]['engine']} 完了！")
                                                        
                                                        # DBに保存
                                                        db.save_result(res_url, prompt, tasks[rec_tid]['engine'])
                                                
                                                elif state == "fail":
                                                    tasks[rec_tid]["status"] = "failed"
                                                    st.error(f"{tasks[rec_tid]['engine']} 失敗: {data_body.get('msg')}")
                                        except:
                                            pass
                        except Exception:
                            pass
                        
                        # ギャラリー更新 (Grid表示)
                        with gallery_placeholder.container():
                            # CSS Grid for Gallery
                            st.markdown("""
                            <style>
                            .gallery-container {
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                                gap: 1rem;
                                padding: 1rem 0;
                            }
                            .gallery-item {
                                background: white;
                                padding: 10px;
                                border-radius: 8px;
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                                text-align: center;
                            }
                            .gallery-item img {
                                width: 100%;
                                border-radius: 4px;
                                margin-bottom: 8px;
                            }
                            .gallery-label {
                                font-weight: bold;
                                color: #555;
                                font-size: 0.9rem;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            cols = st.columns(2) # 2列で表示
                            
                            # 表示順序: Nano, Flux
                            task_items = list(tasks.values())
                            
                            for idx, task_info in enumerate(task_items):
                                with cols[idx % 2]:
                                    if task_info["result_url"]:
                                        st.image(task_info["result_url"], use_container_width=True)
                                        st.markdown(f"**{task_info['engine']}**")
                                        # ダウンロードボタンなど追加可能
                                    elif task_info["status"] == "failed":
                                        st.error(f"{task_info['engine']}: 生成失敗")
                                    else:
                                        st.info(f"{task_info['engine']}: 生成中...")

                        time.sleep(3)

            except Exception as e:
                st.error(f"システムエラー: {e}")

    elif run_button and not uploaded_files:
        st.warning("画像をアップロードしてください。")
    
    # --- Community Gallery (Tab 1) ---
    st.markdown("---")
    st.subheader("🌐 コミュニティギャラリー")
    
    # DB接続チェック
    if not db.get_connection():
        st.warning("⚠️ ギャラリー機能を使用するには、Google Cloudの設定が必要です。")
        with st.expander("設定方法を見る"):
            st.markdown("""
            1. Google Cloud Consoleでプロジェクトを作成し、Sheets APIを有効化。
            2. サービスアカウントを作成し、JSONキーを取得。
            3. `.streamlit/secrets.toml` に `[gcp_service_account]` セクションを追加してJSONの内容を貼り付けてください。
            """)
    else:
        st.markdown("他のユーザーが生成したパース一覧 (最新50件)")

        # DBから取得
        recent_results = db.get_recent_results(limit=50)

        if recent_results:
            # CSS Grid for Gallery (Reusable)
            st.markdown("""
            <style>
            .community-gallery-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1rem;
                padding: 1rem 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Streamlitのcolumnsを使ってグリッド風に表示 (4列)
            cols = st.columns(4)
            for idx, record in enumerate(recent_results):
                with cols[idx % 4]:
                    try:
                        # 拡張子で判定して動画または画像を表示
                        url = record['image_url']
                        if url and (url.endswith(".mp4") or url.endswith(".mov") or url.endswith(".webm")):
                            st.video(url)
                            st.markdown(f"[🔗 動画を開く(保存)]({url})")
                        else:
                            st.image(url, use_container_width=True)
                            
                        st.caption(f"{record['engine']} | {record['timestamp']}")
                        with st.expander("プロンプト"):
                            st.text(record['prompt'])
                    except:
                        pass
        else:
            st.info("まだ生成結果がありません。")


# ==========================================
# Tab 2: ギャラリー & Drive
# ==========================================
# ==========================================
# Tab 2: 動画生成 (Video)
# ==========================================
# ==========================================
# Tab 2: 動画生成 (Veo 3.1)
# ==========================================
with tab2:
    st.subheader("🎥 動画生成 (Veo 3.1)")
    
    # --- UI Layout based on Veo 3.1 Playground ---
    
    # 1. Generation Type
    gen_type = st.radio("生成タイプ (Generation Type)", ["Text to Video", "Image to Video"], horizontal=True)
    
    # 2. Model Selection
    model_friendly_names = {"Veo 3.1 Fast": "veo3_fast", "Veo 3.1 Quality": "veo3"}
    selected_model_name = st.radio("モデル (Model)", list(model_friendly_names.keys()), horizontal=True)
    selected_model_id = model_friendly_names[selected_model_name]

    # Initialize Session State for Video Results
    if 'video_results' not in st.session_state:
        st.session_state.video_results = []

    # 3. Inputs
    input_image_url = None
    
    if gen_type == "Image to Video":
        st.markdown("### 画像 (Image)")
        v_uploaded_file = st.file_uploader("開始フレーム画像をアップロード", type=["jpg", "png", "jpeg", "webp"], key="veo_uploader")
        
        if v_uploaded_file:
            st.image(v_uploaded_file, caption="Input Image", width=300)
            
    # 4. Prompt
    st.markdown("### 生成プロンプト (Prompt)")
    v_prompt = st.text_area("動画の内容を記述してください", value="", height=100, placeholder="A cinematic shot of...", key="veo_prompt")
    
    # 5. Aspect Ratio
    col_ar, col_seed = st.columns(2)
    with col_ar:
        ar_options = ["16:9", "9:16", "1:1", "4:3", "3:4"]
        aspect_ratio = st.selectbox("比率 (Aspect Ratio)", ar_options, index=0)
        
    with col_seed:
        seed = st.number_input("シード (Seed, 任意)", min_value=0, value=0, help="0はランダム")
        if seed == 0:
            seed = None

    # --- Run Button ---
    run_veo_btn = st.button("動画を生成する (Generate Video)", type="primary", use_container_width=True)

    # --- Processing ---
    if run_veo_btn:
        if not API_KEY:
            st.error("API Keyが必要です。")
            st.stop()
            
        if not v_prompt:
             st.error("プロンプトを入力してください。")
             st.stop()
             
        if gen_type == "Image to Video" and not v_uploaded_file:
            st.error("画像をアップロードしてください。")
            st.stop()

        # Output Area
        result_container = st.container()
        
        with result_container:
            status_text = st.empty()
            prog_bar = st.progress(0)
            
            try:
                # 1. Upload Image (if needed)
                image_urls = []
                if gen_type == "Image to Video" and v_uploaded_file:
                    with st.spinner("画像をアップロード中..."):
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {API_KEY}"
                        }
                        
                        image = Image.open(v_uploaded_file)
                        if image_to_base64: 
                            b64_img = image_to_base64(image)
                            input_url = upload_image_to_kieai(headers, b64_img) 
                            
                            if input_url:
                                image_urls.append(input_url)
                            else:
                                st.error("画像のアップロードに失敗しました。")
                                st.stop()

                # 2. Prepare Payload
                wh_uuid = get_webhook_token()
                callback_url = f"https://webhook.site/{wh_uuid}"
                
                # API Endpoint
                generate_url = "https://api.kie.ai/api/v1/veo/generate"
                
                payload = {
                    "prompt": v_prompt,
                    "model": selected_model_id,
                    "aspectRatio": aspect_ratio,
                    "callBackUrl": callback_url
                }
                
                if image_urls:
                    payload["imageUrls"] = image_urls
                
                if seed:
                    payload["seed"] = seed

                # 3. Submit Task
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }
                
                status_text.info("タスクを送信中...")
                res = requests.post(generate_url, headers=headers, json=payload)
                
                if res.status_code != 200:
                    st.error(f"API Error ({res.status_code}): {res.text}")
                    st.stop()
                    
                resp_data = res.json()
                if resp_data.get("code") != 200:
                    st.error(f"Request Failed: {resp_data.get('msg')}")
                    st.stop()
                    
                task_id = resp_data["data"]["taskId"]
                st.toast(f"タスク開始: {task_id}")
                
                # 4. Polling
                start_ts = time.time()
                poll_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
                
                status_text.markdown(f"**生成中...** (Task ID: `{task_id}`)")
                
                while True:
                    elapsed = time.time() - start_ts
                    if elapsed > 600: # 10 minutes timeout
                        st.error("タイムアウトしました。")
                        break
                        
                    # Progress simulation (approx 2 mins for fast, 5 for quality)
                    estimated_duration = 120 if "fast" in selected_model_id else 300
                    prog_bar.progress(min(elapsed / estimated_duration, 0.95))
                    
                    try:
                        poll_res = requests.get(poll_url, headers=headers)
                        if poll_res.status_code == 200:
                            poll_data = poll_res.json()
                            if poll_data.get("code") == 200:
                                data = poll_data["data"]
                                success_flag = data.get("successFlag")
                                
                                # 0: Generating, 1: Success, 2/3: Failed
                                if success_flag == 1:
                                    prog_bar.progress(1.0)
                                    status_text.success("生成完了！")
                                    
                                    # Parse result URLs
                                    video_urls = []
                                    if "response" in data and "resultUrls" in data["response"]:
                                        video_urls = data["response"]["resultUrls"]
                                    elif "resultUrls" in data:
                                        # Fallback or older API style
                                        if isinstance(data["resultUrls"], str):
                                            video_urls = json.loads(data["resultUrls"])
                                        else:
                                            video_urls = data["resultUrls"]
                                    
                                    if video_urls:
                                        for i, v_url in enumerate(video_urls):
                                            st.video(v_url)
                                            
                                            # Fetch and Store for Persistence
                                            try:
                                                v_response = requests.get(v_url)
                                                if v_response.status_code == 200:
                                                    # Store in session state
                                                    st.session_state.video_results.append({
                                                        "url": v_url,
                                                        "content": v_response.content,
                                                        "prompt": v_prompt,
                                                        "model": selected_model_name,
                                                        "timestamp": int(time.time())
                                                    })
                                                    
                                                    # Show immediate download button
                                                    st.download_button(
                                                        label="📥 動画をダウンロード",
                                                        data=v_response.content,
                                                        file_name=f"veo_video_{int(time.time())}_{i+1}.mp4",
                                                        mime="video/mp4",
                                                        key=f"dl_btn_immediate_{task_id}_{i}"
                                                    )
                                            except Exception as e:
                                                print(f"Download preparation failed: {e}")

                                            st.success(f"Video URL: {v_url}")
                                            
                                            # Save to DB
                                            db.save_result(v_url, v_prompt, f"Veo 3.1 ({selected_model_name})")
                                            st.toast("コミュニティギャラリーに保存しました！")
                                    break
                                
                                elif success_flag in [2, 3]:
                                    st.error(f"生成失敗: {poll_data.get('msg', 'Unknown error')}")
                                    break
                    except Exception as e:
                        # print(f"Polling error: {e}")
                        pass
                    
                    time.sleep(5) # Poll every 5 seconds
                    
            except Exception as e:
                st.error(f"システムエラー: {e}")

    # --- Session Gallery ---
    st.markdown("---")
    st.subheader("🎥 生成ビデオギャラリー (Session)")

    if st.session_state.video_results:
        # Display in grid
        v_cols = st.columns(2)
        # Reverse to show newest first
        for i, v_item in enumerate(reversed(st.session_state.video_results)): 
            with v_cols[i % 2]:
                st.video(v_item["url"])
                
                col_dl, col_pmt = st.columns([1, 2])
                with col_dl:
                    if v_item.get("content"):
                        st.download_button(
                            label="📥 ダウンロード",
                            data=v_item["content"],
                            file_name=f"veo_{v_item['timestamp']}_{i}.mp4",
                            mime="video/mp4",
                            key=f"gallery_dl_{i}"
                        )
                with col_pmt:
                    with st.expander("プロンプト"):
                        st.caption(f"Model: {v_item.get('model', 'Unknown')}")
                        st.text(v_item["prompt"])
    else:
        st.info("まだ動画が生成されていません。")

    # --- History from DB ---
    st.markdown("---")
    st.subheader("🕑 過去の生成履歴 (Recent 10)")
    
    # DBから最新の動画を取得
    recent_videos = [r for r in db.get_recent_results(limit=20) if r['image_url'].endswith((".mp4", ".mov", ".webm"))]
    
    if recent_videos:
        h_cols = st.columns(2)
        for i, h_item in enumerate(recent_videos[:10]):
            with h_cols[i % 2]:
                st.video(h_item['image_url'])
                st.markdown(f"[🔗 動画を開く(保存)]({h_item['image_url']})")
                st.caption(f"{h_item['timestamp']}")
    else:
        st.write("履歴がありません。")


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
