import streamlit as st


def load_styles():
    """Inject custom CSS styles."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;800&family=Noto+Serif+JP:wght@600;700&display=swap');

            :root {
                --bg-base: #f4efe7;
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
                    radial-gradient(circle at top left, rgba(214, 229, 216, 0.5), transparent 34%),
                    radial-gradient(circle at top right, rgba(247, 231, 221, 0.9), transparent 36%),
                    linear-gradient(180deg, #f7f2ea 0%, #f2ede5 46%, #f9f6f1 100%);
            }

            .main .block-container {
                max-width: 1280px;
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

            div[data-testid="stTabs"] {
                margin-top: 1.1rem;
                margin-bottom: 1.1rem;
            }

            button[role="tab"] {
                background: rgba(255, 255, 255, 0.62);
                border: 1px solid transparent;
                border-radius: 999px;
                color: #5d5148;
                font-weight: 700;
                padding: 0.75rem 1rem;
                margin-right: 0.55rem;
                transition: all 0.18s ease;
            }

            button[role="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, rgba(143, 76, 43, 0.98), rgba(109, 49, 22, 0.98));
                color: #fffaf7;
                box-shadow: 0 14px 26px rgba(109, 49, 22, 0.22);
            }

            button[role="tab"]:hover {
                border-color: rgba(143, 76, 43, 0.18);
                color: var(--brand);
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
                padding: 2rem 2rem 1.9rem 2rem;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(248, 242, 235, 0.86) 52%, rgba(220, 232, 223, 0.72) 100%);
                border: 1px solid rgba(143, 76, 43, 0.14);
                box-shadow: var(--shadow);
            }

            .hero-shell::after {
                content: "";
                position: absolute;
                inset: auto -10% -45% auto;
                width: 320px;
                height: 320px;
                background: radial-gradient(circle, rgba(143, 76, 43, 0.18), transparent 66%);
                pointer-events: none;
            }

            .hero-eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                border-radius: 999px;
                padding: 0.42rem 0.8rem;
                background: rgba(255, 255, 255, 0.76);
                border: 1px solid rgba(143, 76, 43, 0.14);
                color: var(--brand-strong);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .hero-title {
                margin: 0.95rem 0 0.55rem 0;
                font-family: 'Noto Serif JP', serif;
                font-size: clamp(2rem, 3.8vw, 3.45rem);
                line-height: 1.08;
                color: #241b14;
            }

            .hero-copy {
                max-width: 720px;
                margin: 0;
                color: #4f4a44;
                font-size: 1rem;
                line-height: 1.8;
            }

            .hero-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.7rem;
                margin-top: 1.15rem;
            }

            .hero-chip {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.5rem 0.85rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(143, 76, 43, 0.12);
                color: #5d5148;
                font-size: 0.9rem;
                font-weight: 700;
            }

            .hero-stat-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
                margin-top: 1.4rem;
            }

            .hero-stat {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 22px;
                padding: 0.95rem 1rem;
                border: 1px solid rgba(143, 76, 43, 0.12);
            }

            .hero-stat-label {
                color: var(--muted);
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            .hero-stat-value {
                margin-top: 0.35rem;
                font-size: 1.25rem;
                font-weight: 800;
                color: #221814;
            }

            .hero-stat-copy {
                margin-top: 0.2rem;
                color: #635952;
                font-size: 0.88rem;
                line-height: 1.5;
            }

            .section-kicker {
                color: var(--brand);
                font-size: 0.82rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.35rem;
            }

            .panel-note {
                display: grid;
                gap: 0.28rem;
                margin: 0.75rem 0 0.25rem 0;
                padding: 0.95rem 1rem;
                border-radius: 18px;
                background: linear-gradient(135deg, rgba(247, 231, 221, 0.75), rgba(255, 255, 255, 0.7));
                border: 1px solid rgba(143, 76, 43, 0.12);
            }

            .panel-note strong {
                color: #2b211a;
                font-size: 0.95rem;
            }

            .panel-note span,
            .muted-note,
            .gallery-heading {
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

            .result-bullets {
                display: grid;
                gap: 0.45rem;
                color: #524942;
                font-size: 0.9rem;
                line-height: 1.6;
            }

            .result-label {
                margin-top: 0.75rem;
                color: #3a2d24;
                font-weight: 800;
            }

            @media (max-width: 900px) {
                .hero-shell {
                    padding: 1.45rem;
                    border-radius: 28px;
                }

                .hero-stat-grid {
                    grid-template-columns: 1fr;
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
            <div class="hero-eyebrow">ISHITOMO HOME | AI VISUAL STUDIO</div>
            <h1 class="hero-title">建築パースを、<br>公開したくなる完成度へ。</h1>
            <p class="hero-copy">
                手描きスケッチや簡易モデルの輪郭を保ちながら、素材感・光・空気感だけを引き上げるための生成ワークスペースです。
                Xで見せやすい比較体験と、短時間で意思決定できる画面構成に整えています。
            </p>
            <div class="hero-meta">
                <div class="hero-chip">Nano Banana 2 / GPT Image 1.5</div>
                <div class="hero-chip">画像生成 + 動画生成</div>
                <div class="hero-chip">コミュニティギャラリー連携</div>
            </div>
            <div class="hero-stat-grid">
                <div class="hero-stat">
                    <div class="hero-stat-label">Rendering</div>
                    <div class="hero-stat-value">2 Engines</div>
                    <div class="hero-stat-copy">同条件で並列生成し、質感差をその場で比較できます。</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Workflow</div>
                    <div class="hero-stat-value">Image to Share</div>
                    <div class="hero-stat-copy">入力から結果確認までを1画面で完結させる設計です。</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">For Social</div>
                    <div class="hero-stat-value">Clean First View</div>
                    <div class="hero-stat-copy">ファーストビューでアプリの価値が伝わるよう密度を整理しています。</div>
                </div>
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
                <div class="result-placeholder-title">生成結果はここに表示されます</div>
                <p class="result-placeholder-copy">
                    画像をアップロードして生成を開始すると、進行状況と各エンジンの出力がこのエリアに並びます。
                    比較しながら、そのまま公開用の1枚を選べます。
                </p>
                <div class="result-bullets">
                    <div>・同じ元画像で Nano Banana 2 と GPT Image 1.5 を比較</div>
                    <div>・生成中の進捗と完了順をリアルタイム表示</div>
                    <div>・保存済みの結果は下部ギャラリーにも反映</div>
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
