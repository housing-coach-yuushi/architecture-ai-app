import streamlit as st
import toml
import drive_utils
import sys

# Mock st.secrets
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets_dict = toml.load(f)
    st.secrets = secrets_dict
except Exception as e:
    print(f"Error loading secrets: {e}")
    sys.exit(1)

def main():
    service, email = drive_utils.get_drive_service()
    print(f"Service Account Email: {email}")
    
    # List files in specific folder
    folder_id = "11gZm07ntZpy5fgqPul_chlouxlXVNswC"
    print(f"Listing files in folder {folder_id}...")
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, pageSize=10, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found in folder.')
    else:
        print('Files in folder:')
        for item in items:
            print(f"{item['name']} ({item['id']}) - {item['mimeType']}")

if __name__ == "__main__":
    main()
