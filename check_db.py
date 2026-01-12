import db
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

results = db.get_categorized_images(limit=100)
print(f"Total categorized images in DB: {len(results)}")
for r in results[:5]:
    print(f"- {r['category']}: {r['description']}")
