import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google Sheetsの設定
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

def get_connection():
    """Google Sheetsへの接続を確立する"""
    try:
        # st.secretsから認証情報を取得
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            client = gspread.authorize(creds)
            return client
        else:
            return None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_db(sheet_name="gallery_data"):
    """シートが存在しない場合は作成し、ヘッダーを設定する (簡易版)"""
    client = get_connection()
    if not client:
        return None
        
    try:
        # スプレッドシートを開く (名前で指定、なければエラーになるので運用時は事前に作成推奨)
        # ここでは既存のシート "architecture-app-db" を想定、または secrets で指定
        sheet_key = st.secrets.get("SHEET_KEY") # シートIDがあれば確実
        if sheet_key:
            try:
                sh = client.open_by_key(sheet_key)
            except:
                st.warning(f"指定されたシートキー {sheet_key} が見つかりません。")
                return None
        else:
            # 名前で検索 (ユニークな名前推奨)
            try:
                sh = client.open("architecture-app-db")
            except gspread.SpreadsheetNotFound:
                # シートがない場合は作成する (サービスアカウントのドライブに作成される)
                try:
                    sh = client.create("architecture-app-db")
                    # 誰でも閲覧可能にする（オプション: 必要に応じて変更）
                    sh.share(None, perm_type='anyone', role='reader')
                    st.toast("新しいデータベース(スプレッドシート)を作成しました。")
                except Exception as e:
                    if "quota" in str(e).lower():
                        st.error("⚠️ Google Driveの容量制限により、自動作成に失敗しました。")
                        st.info(f"""
                        **手動での作成をお願いします:**
                        1. Googleスプレッドシートで新しいシートを作成し、名前を `architecture-app-db` にしてください。
                        2. そのシートを以下のメールアドレスに「編集者」として共有してください。
                        
                        `{client.auth.service_account_email}`
                        """)
                    else:
                        st.error(f"スプレッドシートの作成に失敗しました: {e}")
                    return None
            
        # ワークシート取得 (なければ作成)
        try:
            worksheet = sh.worksheet(sheet_name)
        except:
            worksheet = sh.add_worksheet(title=sheet_name, rows=1000, cols=10)
            # ヘッダー作成
            if sheet_name == "gallery_data":
                worksheet.append_row(["timestamp", "image_url", "prompt", "engine", "user_id"])
            elif sheet_name == "categorized_images":
                worksheet.append_row(["timestamp", "file_id", "image_url", "category", "description", "source_folder_id"])
            
        return worksheet
    except Exception as e:
        # st.error(f"Sheet init error: {e}")
        return None

def save_result(image_url, prompt, engine, user_id="anonymous"):
    """生成結果をDB(Sheet)に保存"""
    worksheet = init_db("gallery_data")
    if worksheet:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([timestamp, image_url, prompt, engine, user_id])
            return True
        except Exception as e:
            st.error(f"Save error: {e}")
            return False
    return False

def get_recent_results(limit=50):
    """最新の生成結果を取得"""
    worksheet = init_db("gallery_data")
    if worksheet:
        try:
            # 全データを取得 (行数が多いと遅くなるので注意。本番ではAPIで範囲指定推奨)
            all_records = worksheet.get_all_records()
            # 新しい順にソート
            sorted_records = sorted(all_records, key=lambda x: x['timestamp'], reverse=True)
            return sorted_records[:limit]
        except Exception as e:
            # st.error(f"Fetch error: {e}")
            return []
    return []

def save_categorized_image(file_id, image_url, category, description, source_folder_id):
    """カテゴリ分けされた画像をDBに保存"""
    worksheet = init_db("categorized_images")
    if worksheet:
        try:
            # 重複チェック (簡易)
            # 全件取得してfile_idがあるか確認するのは非効率だが、小規模ならOK
            # 本来はDB側でユニーク制約をかけたいが、Spreadsheetなのでコードでチェック
            try:
                cell = worksheet.find(file_id)
                if cell:
                    return True # 既に存在するのでスキップ
            except:
                pass # 見つからない場合は続行

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            worksheet.append_row([timestamp, file_id, image_url, category, description, source_folder_id])
            return True
        except Exception as e:
            st.error(f"Save categorized image error: {e}")
            return False
    return False

def get_categorized_images(category=None, limit=100):
    """カテゴリ分けされた画像を取得"""
    worksheet = init_db("categorized_images")
    if worksheet:
        try:
            all_records = worksheet.get_all_records()
            if category and category != "All":
                filtered_records = [r for r in all_records if r.get('category') == category]
            else:
                filtered_records = all_records
            
            # 新しい順
            sorted_records = sorted(filtered_records, key=lambda x: x['timestamp'], reverse=True)
            return sorted_records[:limit]
        except Exception as e:
            return []
    return []
