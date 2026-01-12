import google.generativeai as genai
import toml
import streamlit as st
import sys

# Mock st.secrets
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets_dict = toml.load(f)
    st.secrets = secrets_dict
except Exception as e:
    print(f"Error loading secrets: {e}")
    sys.exit(1)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
