import streamlit as st


def load_styles():
    """Inject custom CSS styles."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

            :root {
                --bg: #f3f6fb;
                --bg-soft: #eef2f8;
                --surface: rgba(255, 255, 255, 0.9);
                --surface-strong: #ffffff;
                --ink: #111827;
                --muted: #5b6474;
                --line: rgba(148, 163, 184, 0.28);
                --line-strong: rgba(100, 116, 139, 0.24);
                --accent: #0f172a;
                --accent-soft: #e7edf6;
                --accent-glow: rgba(15, 23, 42, 0.06);
                --shadow: 0 18px 48px rgba(15, 23, 42, 0.06);
            }

            html, body, [class*="css"] {
                font-family: 'Instrument Sans', sans-serif;
                color: var(--ink);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(191, 219, 254, 0.24), transparent 26%),
                    radial-gradient(circle at top right, rgba(226, 232, 240, 0.72), transparent 32%),
                    linear-gradient(180deg, #f8fafd 0%, var(--bg) 48%, #edf2f8 100%);
            }

            .main .block-container {
                max-width: 1280px;
                padding-top: 1.25rem;
                padding-bottom: 4rem;
                padding-left: 1.2rem;
                padding-right: 1.2rem;
            }

            h1, h2, h3, label, p, span, div {
                letter-spacing: -0.02em;
            }

            div[data-testid="stHeadingWithActionElements"] h1,
            div[data-testid="stHeadingWithActionElements"] h2,
            div[data-testid="stHeadingWithActionElements"] h3 {
                font-family: 'Instrument Sans', sans-serif;
                font-weight: 650;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 24px;
                box-shadow: var(--shadow);
                backdrop-filter: blur(18px);
                animation: surface-in 320ms ease-out;
            }

            div[data-testid="stFileUploader"] section {
                background: rgba(248, 250, 252, 0.92);
                border: 1.5px dashed rgba(100, 116, 139, 0.34);
                border-radius: 18px;
                padding: 1.05rem;
                transition: border-color 0.18s ease, background 0.18s ease;
            }

            div[data-testid="stTextArea"] textarea {
                background: rgba(248, 250, 252, 0.98);
                border-radius: 18px;
                border: 1px solid var(--line);
                line-height: 1.7;
                padding: 1rem 1.05rem;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
            }

            div[data-baseweb="select"] > div,
            div[data-testid="stTextInputRootElement"] > div,
            div[data-testid="stNumberInputContainer"] > div {
                background: rgba(248, 250, 252, 0.98);
                border-radius: 16px;
                border-color: var(--line);
            }

            div[data-testid="stAlert"] {
                border-radius: 18px;
                border: 1px solid var(--line);
            }

            .stButton > button {
                border-radius: 14px;
                padding: 0.76rem 1.1rem;
                font-weight: 650;
                border: 1px solid transparent;
                transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease, background 0.16s ease;
            }

            .stButton > button[kind="primary"],
            .stButton > button[data-testid="baseButton-primary"] {
                background: linear-gradient(180deg, #1f2937 0%, #0f172a 100%);
                color: #f8fafc;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.18);
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.02);
            }

            .stButton > button[kind="secondary"],
            .stButton > button[data-testid="baseButton-secondary"] {
                background: rgba(248, 250, 252, 0.98);
                border-color: var(--line);
                color: var(--ink);
            }

            .stMultiSelect [data-baseweb="tag"] {
                background: var(--accent-soft);
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.28);
                color: var(--accent);
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.74rem;
            }

            details {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 0.2rem 0.5rem;
            }

            div[data-testid="stImage"] img,
            div[data-testid="stVideo"] video {
                border-radius: 18px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            }

            .workspace-shell {
                position: relative;
                overflow: hidden;
                border-radius: 28px;
                padding: 1.35rem 1.45rem 1.45rem;
                background:
                    radial-gradient(circle at top right, rgba(148, 163, 184, 0.12), transparent 28%),
                    linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(246, 249, 252, 0.9) 100%);
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                animation: surface-in 380ms ease-out;
            }

            .workspace-kicker {
                display: inline-flex;
                align-items: center;
                gap: 0.55rem;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.73rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: #475569;
            }

            .workspace-kicker::before {
                content: "";
                width: 0.5rem;
                height: 0.5rem;
                border-radius: 999px;
                background: #111827;
                box-shadow: 0 0 0 6px rgba(15, 23, 42, 0.07);
            }

            .workspace-title {
                margin: 0;
                padding-top: 0.95rem;
                font-size: clamp(1.9rem, 3.1vw, 2.9rem);
                line-height: 1.04;
                font-weight: 680;
                color: #0f172a;
                max-width: 11ch;
            }

            .workspace-copy {
                max-width: 700px;
                margin: 0.8rem 0 0 0;
                color: var(--muted);
                font-size: 0.98rem;
                line-height: 1.8;
            }

            .workspace-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 1.1rem;
            }

            .workspace-chip {
                display: inline-flex;
                align-items: center;
                padding: 0.45rem 0.78rem;
                border-radius: 999px;
                background: rgba(248, 250, 252, 0.95);
                border: 1px solid var(--line);
                color: #334155;
                font-size: 0.78rem;
                font-weight: 560;
                font-family: 'IBM Plex Mono', monospace;
            }

            .panel-note {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.7;
            }

            .panel-heading {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
                margin-bottom: 1rem;
            }

            .panel-kicker {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #64748b;
            }

            .panel-title {
                margin: 0;
                font-size: 1.05rem;
                font-weight: 650;
                color: #0f172a;
            }

            .panel-copy {
                margin: 0;
                color: var(--muted);
                font-size: 0.93rem;
                line-height: 1.6;
            }

            .result-placeholder {
                border-radius: 22px;
                padding: 1.15rem;
                min-height: 420px;
                background:
                    radial-gradient(circle at top right, rgba(148, 163, 184, 0.18), transparent 28%),
                    linear-gradient(180deg, rgba(249, 250, 251, 0.95), rgba(241, 245, 249, 0.92));
                border: 1px dashed rgba(148, 163, 184, 0.34);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                gap: 1rem;
            }

            .result-placeholder-visual {
                min-height: 250px;
                border-radius: 20px;
                background:
                    linear-gradient(180deg, rgba(255, 255, 255, 0.5), rgba(226, 232, 240, 0.45)),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.45) 0%, rgba(226, 232, 240, 0.12) 100%);
                position: relative;
                overflow: hidden;
            }

            .result-placeholder-visual::after {
                content: "";
                position: absolute;
                inset: 0;
                background-image:
                    linear-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(148, 163, 184, 0.12) 1px, transparent 1px);
                background-size: 26px 26px;
                mask-image: linear-gradient(180deg, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.08));
            }

            .result-placeholder-title {
                font-size: 1.2rem;
                font-weight: 650;
                color: #0f172a;
            }

            .result-placeholder-copy {
                color: var(--muted);
                line-height: 1.8;
                font-size: 0.95rem;
            }

            .result-placeholder-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.55rem;
                margin-top: 0.9rem;
            }

            .result-placeholder-pill {
                display: inline-flex;
                align-items: center;
                padding: 0.42rem 0.68rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(148, 163, 184, 0.24);
                color: #475569;
                font-size: 0.74rem;
                font-family: 'IBM Plex Mono', monospace;
            }

            .result-label {
                margin-top: 0.75rem;
                color: #0f172a;
                font-weight: 650;
            }

            .gallery-heading {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.7;
            }

            hr {
                border: none;
                border-top: 1px solid rgba(148, 163, 184, 0.22);
                margin: 1.25rem 0 0.9rem;
            }

            @keyframes surface-in {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @media (max-width: 900px) {
                .workspace-shell {
                    padding: 1.2rem;
                    border-radius: 24px;
                }

                .workspace-title {
                    max-width: none;
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
        <section class="workspace-shell">
            <div class="workspace-kicker">Architecture AI Workspace</div>
            <h1 class="workspace-title">建築パースを崩さずに、実写へ寄せる。</h1>
            <p class="workspace-copy">
                元画像の構図、形状、寸法感を保ちながら、質感と光だけを現実寄りに調整する
                image-to-image ワークスペースです。
            </p>
            <div class="workspace-meta">
                <div class="workspace-chip">image-to-image</div>
                <div class="workspace-chip">nano-banana-2</div>
                <div class="workspace-chip">gpt-image-2</div>
                <div class="workspace-chip">local workflow</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_panel_header(kicker, title, copy):
    """Render a small workspace-style panel header."""
    st.markdown(
        f"""
        <div class="panel-heading">
            <div class="panel-kicker">{kicker}</div>
            <p class="panel-title">{title}</p>
            <p class="panel-copy">{copy}</p>
        </div>
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
                <div class="result-placeholder-title">Result canvas</div>
                <p class="result-placeholder-copy">
                    生成を開始すると、ここに各エンジンの出力が並びます。複数画像を入れた場合は、
                    元画像ごとに結果が追加されます。
                </p>
                <div class="result-placeholder-meta">
                    <div class="result-placeholder-pill">webhook polling</div>
                    <div class="result-placeholder-pill">parallel engines</div>
                    <div class="result-placeholder-pill">preview ready</div>
                </div>
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
