import streamlit as st


def load_styles():
    """Inject custom CSS styles."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&family=Noto+Serif+JP:wght@600;700&display=swap');

            :root {
                --surface: rgba(255, 252, 247, 0.84);
                --ink: #1f2933;
                --muted: #6f6b64;
                --line: rgba(128, 101, 73, 0.16);
                --brand: #8f4c2b;
                --brand-strong: #6d3116;
                --brand-soft: #f7e7dd;
                --shadow: 0 22px 60px rgba(53, 39, 26, 0.12);
            }

            html, body, [class*="css"] {
                font-family: 'Noto Sans JP', sans-serif;
                color: var(--ink);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(214, 229, 216, 0.45), transparent 34%),
                    radial-gradient(circle at top right, rgba(247, 231, 221, 0.9), transparent 36%),
                    linear-gradient(180deg, #f7f2ea 0%, #f2ede5 46%, #f9f6f1 100%);
            }

            .main .block-container {
                max-width: 1240px;
                padding-top: 1.8rem;
                padding-bottom: 4rem;
                padding-left: 1.4rem;
                padding-right: 1.4rem;
            }

            h1, h2, h3 {
                letter-spacing: -0.02em;
            }

            div[data-testid="stHeadingWithActionElements"] h1,
            div[data-testid="stHeadingWithActionElements"] h2,
            div[data-testid="stHeadingWithActionElements"] h3 {
                font-family: 'Noto Serif JP', serif;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 28px;
                box-shadow: var(--shadow);
            }

            div[data-testid="stFileUploader"] section {
                background: rgba(255, 255, 255, 0.8);
                border: 1.5px dashed rgba(143, 76, 43, 0.32);
                border-radius: 22px;
                padding: 1rem;
            }

            div[data-testid="stTextArea"] textarea {
                background: rgba(255, 255, 255, 0.84);
                border-radius: 22px;
                border: 1px solid rgba(143, 76, 43, 0.18);
                line-height: 1.7;
                padding: 1rem 1.05rem;
            }

            div[data-baseweb="select"] > div,
            div[data-testid="stTextInputRootElement"] > div,
            div[data-testid="stNumberInputContainer"] > div {
                background: rgba(255, 255, 255, 0.84);
                border-radius: 18px;
                border-color: rgba(143, 76, 43, 0.18);
            }

            div[data-testid="stAlert"] {
                border-radius: 20px;
                border: 1px solid rgba(143, 76, 43, 0.12);
            }

            .stButton > button {
                border-radius: 999px;
                padding: 0.75rem 1.4rem;
                font-weight: 800;
                border: none;
                transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
            }

            .stButton > button[kind="primary"],
            .stButton > button[data-testid="baseButton-primary"] {
                background: linear-gradient(135deg, var(--brand) 0%, var(--brand-strong) 100%);
                color: #fffaf5;
                box-shadow: 0 16px 34px rgba(109, 49, 22, 0.24);
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.02);
            }

            .stMultiSelect [data-baseweb="tag"] {
                background: var(--brand-soft);
                border-radius: 999px;
                border: 1px solid rgba(143, 76, 43, 0.18);
                color: var(--brand-strong);
            }

            details {
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(143, 76, 43, 0.1);
                border-radius: 18px;
                padding: 0.2rem 0.5rem;
            }

            div[data-testid="stImage"] img,
            div[data-testid="stVideo"] video {
                border-radius: 18px;
                box-shadow: 0 16px 30px rgba(53, 39, 26, 0.14);
            }

            .hero-shell {
                position: relative;
                overflow: hidden;
                border-radius: 36px;
                padding: 2rem;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(248, 242, 235, 0.88) 54%, rgba(220, 232, 223, 0.7) 100%);
                border: 1px solid rgba(143, 76, 43, 0.14);
                box-shadow: var(--shadow);
            }

            .hero-title {
                margin: 0;
                font-family: 'Noto Serif JP', serif;
                font-size: clamp(2rem, 3.8vw, 3.4rem);
                line-height: 1.08;
                color: #241b14;
            }

            .hero-copy {
                max-width: 680px;
                margin: 0.8rem 0 0 0;
                color: #4f4a44;
                font-size: 1rem;
                line-height: 1.8;
            }

            .hero-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
                margin-top: 1rem;
            }

            .hero-chip {
                display: inline-flex;
                align-items: center;
                padding: 0.5rem 0.85rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(143, 76, 43, 0.12);
                color: #5d5148;
                font-size: 0.9rem;
                font-weight: 700;
            }

            .panel-note {
                color: #655b55;
                font-size: 0.92rem;
                line-height: 1.7;
            }

            .result-placeholder {
                border-radius: 24px;
                padding: 1.2rem;
                min-height: 420px;
                background:
                    linear-gradient(180deg, rgba(255,255,255,0.6), rgba(252, 247, 242, 0.95)),
                    radial-gradient(circle at top right, rgba(220, 232, 223, 0.6), transparent 42%);
                border: 1px dashed rgba(143, 76, 43, 0.22);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                gap: 1rem;
            }

            .result-placeholder-visual {
                min-height: 250px;
                border-radius: 20px;
                background:
                    linear-gradient(135deg, rgba(143, 76, 43, 0.1), rgba(220, 232, 223, 0.45)),
                    linear-gradient(180deg, rgba(255,255,255,0.24), rgba(255,255,255,0));
            }

            .result-placeholder-title {
                font-family: 'Noto Serif JP', serif;
                font-size: 1.2rem;
                font-weight: 700;
                color: #231914;
            }

            .result-placeholder-copy {
                color: #625851;
                line-height: 1.8;
                font-size: 0.95rem;
            }

            .result-label {
                margin-top: 0.75rem;
                color: #3a2d24;
                font-weight: 800;
            }

            .gallery-heading {
                color: #655b55;
                font-size: 0.92rem;
                line-height: 1.7;
            }

            @media (max-width: 900px) {
                .hero-shell {
                    padding: 1.45rem;
                    border-radius: 28px;
                }

                .result-placeholder {
                    min-height: 300px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """Render the main application header."""
    st.markdown(
        """
        <section class="hero-shell">
            <h1 class="hero-title">AIパース生成</h1>
            <p class="hero-copy">
                元画像の形状や構図を保ったまま、質感と光だけをフォトリアルに整えます。
            </p>
            <div class="hero-meta">
                <div class="hero-chip">Image to Image</div>
                <div class="hero-chip">Nano Banana 2</div>
                <div class="hero-chip">GPT Image 1.5</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_result_placeholder():
    """Render the empty state for the image generation result panel."""
    st.markdown(
        """
        <div class="result-placeholder">
            <div class="result-placeholder-visual"></div>
            <div>
                <div class="result-placeholder-title">結果</div>
                <p class="result-placeholder-copy">
                    生成を開始すると、ここに結果が表示されます。
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gallery_grid(images, columns=2):
    """Render a grid of images using columns."""
    cols = st.columns(columns, gap="large")
    for idx, img_data in enumerate(images):
        with cols[idx % columns]:
            if img_data.get("video_url"):
                st.video(img_data["video_url"])
                st.markdown(f"[🔗 Open Video]({img_data['video_url']})")
            elif img_data.get("image_url"):
                st.image(img_data["image_url"], use_container_width=True)

            if img_data.get("label"):
                st.markdown(f'<div class="result-label">{img_data["label"]}</div>', unsafe_allow_html=True)

            if img_data.get("status") == "failed":
                st.error(f"{img_data.get('label', 'Task')}: Failed")
            elif img_data.get("status") == "pending":
                st.info(f"{img_data.get('label', 'Task')}: Generating...")
