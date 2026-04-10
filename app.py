import streamlit as st
from ui import components
from ui.tabs import tab1_ai_parse

# --- Page Config ---
st.set_page_config(
    page_title="AIパース生成",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Load Styles ---
components.load_styles()

# --- Auth ---
try:
    if "KIEAI_API_KEY" in st.secrets:
        API_KEY = st.secrets["KIEAI_API_KEY"]
    else:
        API_KEY = None
except Exception:
    API_KEY = None

if not API_KEY:
    API_KEY = st.sidebar.text_input("KIEAI API Key", type="password")
    if not API_KEY:
        st.warning("KIEAI APIキーが設定されていません。画像生成機能は使用できません。")

# --- Header ---
components.render_header()

# --- Main ---
tab1_ai_parse.render(API_KEY)
