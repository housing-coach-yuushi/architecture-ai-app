import streamlit as st
import time
import toml
import drive_utils
import db
import google.generativeai as genai
import json
import sys

# Mock st.secrets
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets_dict = toml.load(f)
    st.secrets = secrets_dict
    print("Available keys:", list(secrets_dict.keys()))
except Exception as e:
    print(f"Error loading secrets: {e}")
    sys.exit(1)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
FOLDER_ID = "1Oyu6_6TaR-zaeBfMnkKfK9SLycLCaRIm"

if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found in secrets.")
    sys.exit(1)

def categorize_image_with_gemini(image_bytes):
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
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        return json.loads(text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def main():
    print(f"Starting auto-categorization for folder: {FOLDER_ID}")
    
    # List files
    print("Listing files...")
    files = drive_utils.list_images_in_folder(FOLDER_ID, limit=20)
    print(f"Found {len(files)} files.")
    
    for i, file in enumerate(files):
        time.sleep(4) # Rate limit handling
        print(f"Processing {i+1}/{len(files)}: {file['name']}")
        
        # Download
        img_data = drive_utils.get_image_data(file['id'])
        if not img_data:
            print("  Failed to download.")
            continue
            
        # Categorize
        result = categorize_image_with_gemini(img_data)
        if result:
            category = result.get("category", "その他")
            description = result.get("description", "")
            print(f"  Category: {category}, Desc: {description}")
            
            # Save
            img_url = file.get('thumbnailLink', '').replace("=s220", "=s1024")
            db.save_categorized_image(file['id'], img_url, category, description, FOLDER_ID)
            print("  Saved to DB.")
        else:
            print("  Failed to categorize.")

if __name__ == "__main__":
    main()
