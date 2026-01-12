import streamlit as st

def render():
    """Render Tab 3: Floor Plan (Blueprint Integration)"""
    st.subheader("📐 間取り作成")
    st.markdown(\"\"\"
    ブラウザで動作する間取り作成ツールです。
    簡単な操作で平面図を作成し、AIパース生成や3D化に使用できます。
    \"\"\")
    
    st.markdown("### ✨ 機能")
    st.markdown(\"\"\"
    - **ドラッグ&ドロップ**で部屋を配置
    - **ワンクリック**で窓やドアを追加
    - 作成した間取りを**画像としてダウンロード**して、このAIアプリでパース化可能
    \"\"\")
    
    # Link to the deployed or local blueprint app
    # In a real scenario, this URL might be dynamic or env-dependent
    st.link_button("間取り作成アプリを開く (Sales App)", "https://blueprint-js-app.vercel.app/sales-mode.html", type="primary")
    
    st.info("💡 ヒント: 作成画面で「AIアプリへ送る」ボタンを押すと、画像がダウンロードされ、スムーズにこのアプリに取り込めます。")
