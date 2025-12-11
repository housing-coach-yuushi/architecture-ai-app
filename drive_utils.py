import streamlit as st
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import io
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API Scope
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Google Drive APIサービスを取得する"""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            
            # oauth2clientのcredsを使ってserviceをビルド
            http = creds.authorize(httplib2.Http())
            service = build('drive', 'v3', http=http)
            
            return service, creds.service_account_email
        else:
            return None, None
    except Exception as e:
        st.error(f"Drive connection error: {e}")
        return None, None

def list_images_in_folder(folder_id, limit=20):
    """指定フォルダ内の画像ファイルをリストする"""
    service, _ = get_drive_service()
    if not service:
        return []

    try:
        # 画像ファイルのみ検索
        # thumbnailLinkを取得するには fields に含める必要がある
        query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        results = service.files().list(
            q=query,
            pageSize=limit,
            fields="nextPageToken, files(id, name, mimeType, webContentLink, webViewLink, thumbnailLink)"
        ).execute()
        items = results.get('files', [])
        return items
    except Exception as e:
        st.error(f"Error listing files: {e}")
        return []

def get_image_data(file_id):
    """Google Driveから画像データをバイナリとして取得する"""
    service, _ = get_drive_service()
    if not service:
        return None

    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        return fh.getvalue()
    except Exception as e:
        st.error(f"Error downloading file {file_id}: {e}")
        return None
