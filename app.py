import streamlit as st
import requests
import json
import base64
import time
from PIL import Image
import io
import db  # Import database module
import drive_utils # Import drive utils
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
tab1, tab2 = st.tabs(["🏠 AIパース生成", "📂 ギャラリー & Drive"])

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
        
        # パラメータ設定
        col1, col2 = st.columns(2)
        with col1:
            strength = st.slider("プロンプトの影響度 (Strength)", 0.0, 1.0, 0.55, help="0に近いほど元画像に忠実、1に近いほどプロンプト重視")
        with col2:
            resolution = st.selectbox("解像度 (Resolution)", ["1K", "2K"], index=0, help="Flux 2のみ有効")
        
        aspect_ratio = st.selectbox("アスペクト比", ["16:9", "1:1", "9:16", "4:3", "3:4"], index=0)
        
        st.info("ℹ️ 'Nano Banana Pro' と 'Flux 2 Flex' の2つのエンジンで同時に生成します。")

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
                    
                    # C. タスク作成 (2つのエンジン)
                    url = "https://api.kie.ai/api/v1/jobs/createTask"
                    
                    tasks = {} # {task_id: {"engine": name, "status": "pending", "result_url": None}}
                    
                    # Engine 1: Nano Banana Pro
                    payload_nano = {
                        "model": "nano-banana-pro",
                        "callBackUrl": callback_url,
                        "input": {
                            "prompt": prompt,
                            "image_input": input_urls,
                            "aspect_ratio": aspect_ratio,
                            "output_format": "png"
                        }
                    }
                    
                    # Engine 2: Flux 2 Flex
                    payload_flux = {
                        "model": "flux-2/flex-image-to-image",
                        "callBackUrl": callback_url,
                        "input": {
                            "input_urls": input_urls,
                            "prompt": prompt,
                            "aspect_ratio": aspect_ratio if aspect_ratio != "auto" else "1:1",
                            "resolution": resolution,
                            "strength": strength
                        }
                    }

                    # Send Requests
                    for engine_name, payload in [("Nano Banana Pro", payload_nano), ("Flux 2 Flex", payload_flux)]:
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
                        st.image(record['image_url'], use_container_width=True)
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
with tab2:
    st.subheader("📂 Google Drive 画像連携 & 自動カテゴリ分け")

    with st.expander("Google Drive 連携の使い方"):
        service, sa_email = drive_utils.get_drive_service()
        if sa_email:
            st.markdown(f"""
            1. Google Driveで対象のフォルダを右クリックし、「共有」を選択します。
            2. 以下のメールアドレスを「閲覧者」として追加してください。
            
            `{sa_email}`
            
            3. フォルダのURLからIDをコピーします。
            4. **Gemini API Key** が設定されていることを確認してください（自動カテゴリ分けに必要です）。
            """)
        else:
            st.warning("サービスアカウントの設定が見つかりません。")

    folder_id = st.text_input("Google Drive フォルダIDを入力", placeholder="例: 1A2B3C...")

    col_drive_ops, col_drive_filter = st.columns([1, 2])

    with col_drive_ops:
        load_btn = st.button("画像を読み込む (一覧表示)")
        auto_cat_btn = st.button("自動カテゴリ分けを実行 (Gemini)", type="primary")

    if folder_id:
        # 1. 画像読み込み (一覧表示)
        if load_btn:
            with st.spinner("Google Driveから画像を検索中..."):
                files = drive_utils.list_images_in_folder(folder_id, limit=20)
                if files:
                    st.success(f"{len(files)} 枚の画像が見つかりました。")
                    cols = st.columns(4)
                    for idx, file in enumerate(files):
                        with cols[idx % 4]:
                            if 'thumbnailLink' in file:
                                thumb_url = file['thumbnailLink'].replace("=s220", "=s1024")
                                st.image(thumb_url, caption=file['name'], use_container_width=True)
                            else:
                                st.write(file['name'])
                else:
                    st.warning("画像が見つかりませんでした。")

        # 2. 自動カテゴリ分け
        if auto_cat_btn:
            if not GEMINI_API_KEY:
                st.error("Gemini API Keyが設定されていません。サイドバーまたはsecretsで設定してください。")
            else:
                with st.spinner("画像を解析してカテゴリ分け中... (これには時間がかかります)"):
                    files = drive_utils.list_images_in_folder(folder_id, limit=20) # 制限付き
                    if files:
                        progress_bar = st.progress(0)
                        count = 0
                        
                        # 既存のカテゴリ済みデータを取得して重複回避（簡易）
                        # existing = db.get_categorized_images(limit=1000)
                        # existing_ids = [e['file_id'] for e in existing]
                        
                        for i, file in enumerate(files):
                            # if file['id'] in existing_ids:
                            #     continue
                            
                            # 画像データ取得
                            img_data = drive_utils.get_image_data(file['id'])
                            if img_data:
                                # Geminiで解析
                                result, error = categorize_image_with_gemini(img_data)
                                if result:
                                    category = result.get("category", "その他")
                                    description = result.get("description", "")
                                    
                                    # サムネイルURLを保存用URLとして使用 (本来は永続的なURLが望ましいがDriveの場合はこれで)
                                    img_url = file.get('thumbnailLink', '').replace("=s220", "=s1024")
                                    
                                    # DB保存
                                    db.save_categorized_image(file['id'], img_url, category, description, folder_id)
                                    count += 1
                                else:
                                    st.warning(f"解析失敗 ({file['name']}): {error}")
                            
                            progress_bar.progress((i + 1) / len(files))
                        
                        st.success(f"{count} 枚の画像をカテゴリ分けして保存しました！")
                    else:
                        st.warning("画像が見つかりませんでした。")

    # 3. カテゴリ別ギャラリー表示
    st.markdown("### 🗂 カテゴリ別ギャラリー")

    # カテゴリフィルタ
    categories = ["すべて", "リビング", "ダイニング", "キッチン", "寝室", "バスルーム", "玄関", "外観", "庭", "その他"]
    selected_category = st.selectbox("カテゴリを選択", categories)

    if db.get_connection():
        # "すべて" の場合は None を渡すか、DB側で処理
        cat_filter = None if selected_category == "すべて" else selected_category
        cat_images = db.get_categorized_images(cat_filter, limit=50)
        
        if cat_images:
            st.markdown(f"**{len(cat_images)}** 枚の画像を表示中")
            
            cols = st.columns(4)
            for idx, img_data in enumerate(cat_images):
                with cols[idx % 4]:
                    try:
                        # カード風デザインで表示
                        st.markdown(f"""
                        <div class="gallery-card">
                            <img src="{img_data['image_url']}" style="width:100%">
                            <div class="gallery-content">
                                <div class="gallery-title">{img_data['category']}</div>
                                <div class="gallery-desc">{img_data['description']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        pass
        else:
            st.info("このカテゴリの画像はまだありません。")
    else:
        st.info("データベースに接続されていません。")


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
