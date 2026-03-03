import streamlit as st
import db
from ui import components
from ui.tabs import tab1_ai_parse, tab2_video

# --- Page Config ---
st.set_page_config(page_title="ishitomo-home AI パース β版", layout="wide")

# --- Load Styles ---
components.load_styles()

# --- Auth ---
try:
    if "KIEAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["KIEAI_API_KEY"]
    else:
        API_KEY = None
except:
    API_KEY = None

if not API_KEY:
    API_KEY = st.sidebar.text_input("KIEAI API Key", type="password")
    if not API_KEY:
        st.warning("KIEAI APIキーが設定されていません。画像生成機能は使用できません。")

# --- Header ---
components.render_header()

# --- Tabs ---
tab1, tab2 = st.tabs(["🏠 AIパース生成", "🎥 動画生成"])

with tab1:
    tab1_ai_parse.render(API_KEY)

with tab2:
    tab2_video.render(API_KEY)
