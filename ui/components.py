import streamlit as st

def load_styles():
    """Inject custom CSS styles."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Noto Sans JP', sans-serif;
        }
        
        /* Header */
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2C3E50;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #eee;
            padding-bottom: 1rem;
        }
        
        /* Sub-header */
        .sub-header {
            font-size: 1.2rem;
            color: #7F8C8D;
            margin-bottom: 2rem;
        }
        
        /* Buttons */
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
        
        /* Gallery */
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
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main application header."""
    st.markdown('<div class="main-header">ishitomo-home AI パース <span style="font-size: 1rem; color: #e74c3c; vertical-align: middle;">β版</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">手書きスケッチや簡易モデルから、フォトリアルな建築パースを生成します。</div>', unsafe_allow_html=True)

def render_gallery_grid(images, columns=2):
    """Render a grid of images using columns."""
    cols = st.columns(columns)
    for idx, img_data in enumerate(images):
        with cols[idx % columns]:
            if img_data.get("video_url"):
                st.video(img_data["video_url"])
                st.markdown(f"[🔗 Open Video]({img_data['video_url']})")
            elif img_data.get("image_url"):
                st.image(img_data["image_url"], use_container_width=True)
            
            if img_data.get("label"):
                st.markdown(f"**{img_data['label']}**")
            
            if img_data.get("status") == "failed":
                st.error(f"{img_data.get('label', 'Task')}: Failed")
            elif img_data.get("status") == "pending":
                st.info(f"{img_data.get('label', 'Task')}: Generating...")
