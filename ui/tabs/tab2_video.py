import json
import time

import streamlit as st
from PIL import Image

from services import kie_api

POLL_INTERVAL_SECONDS = 4
POLL_TIMEOUT_SECONDS = 15 * 60
DEFAULT_FORM_INPUT = {
    "duration": "10",
    "mode": "std",
    "aspect_ratio": "16:9",
    "sound": True,
    "multi_shots": False,
    "prompt": "朝焼けの時間帯に、モダンな住宅をドローンでシネマティックに撮影した映像。",
}


def _inject_styles():
    st.markdown(
        """
        <style>
            .kling-header {
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
                padding: 18px 20px;
                margin-bottom: 16px;
            }
            .kling-chip {
                display: inline-block;
                font-size: 0.82rem;
                background: #eff6ff;
                color: #1d4ed8;
                border: 1px solid #bfdbfe;
                border-radius: 999px;
                padding: 0.25rem 0.7rem;
                margin-top: 6px;
            }
            .kling-card {
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                background: #ffffff;
                padding: 16px;
            }
            .kling-card-title {
                font-size: 1.05rem;
                font-weight: 700;
                margin-bottom: 12px;
            }
            .kling-caption {
                color: #6b7280;
                font-size: 0.85rem;
                margin-bottom: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _upload_input_image(api_key, uploaded_file):
    image = Image.open(uploaded_file)
    image.thumbnail((1536, 1536))
    encoded = kie_api.image_to_base64(image)
    return kie_api.upload_image_to_kieai(api_key, encoded)


def _render_multi_prompt_inputs():
    shot_count = st.slider("ショット数", min_value=2, max_value=6, value=2)
    prompts = []
    for idx in range(shot_count):
        col_prompt, col_duration = st.columns([4, 1])
        with col_prompt:
            shot_prompt = st.text_area(
                f"ショット{idx + 1}のプロンプト",
                height=80,
                max_chars=2500,
                placeholder=f"ショット {idx + 1} の指示を入力",
                key=f"kling_shot_prompt_{idx + 1}",
            ).strip()
        with col_duration:
            shot_duration = st.number_input(
                f"ショット{idx + 1}の秒数",
                min_value=1,
                max_value=15,
                value=3,
                key=f"kling_shot_duration_{idx + 1}",
            )
        if shot_prompt:
            prompts.append({"prompt": shot_prompt, "duration": str(int(shot_duration))})
    return prompts


def _render_form_fields():
    st.markdown("##### 入力画像")
    col_start, col_end = st.columns(2)
    with col_start:
        start_frame = st.file_uploader(
            "開始フレーム",
            type=["jpg", "jpeg", "png", "webp"],
            key="kling_start_frame",
        )
    with col_end:
        end_frame = st.file_uploader(
            "終了フレーム",
            type=["jpg", "jpeg", "png", "webp"],
            key="kling_end_frame",
            disabled=True,
            help="Kling 3.0では現在、終了フレーム入力は無効です。",
        )

    multi_shots = st.toggle("複数ショット", value=False)
    sound = st.toggle("音声を含める", value=True)

    multi_prompt = []
    prompt = ""
    if multi_shots:
        st.markdown("##### ショットごとの設定")
        multi_prompt = _render_multi_prompt_inputs()
    else:
        prompt = st.text_area(
            "プロンプト *",
            height=120,
            max_chars=2500,
            placeholder="プロンプトを入力してください（最大2500文字）",
            key="kling_single_prompt",
        ).strip()

    duration = st.slider("動画の長さ（秒）*", min_value=3, max_value=15, value=10)
    mode = st.radio("生成モード *", ["std", "pro"], horizontal=True)
    aspect_ratio = st.radio("アスペクト比 *", ["1:1", "9:16", "16:9"], horizontal=True, index=2)

    kling_elements_raw = st.text_area(
        "追加オプション（JSON・任意）",
        height=100,
        placeholder='{"style":"cinematic","camera":"dolly-in"}',
        key="kling_elements_raw",
    ).strip()

    return {
        "start_frame": start_frame,
        "end_frame": end_frame,
        "multi_shots": multi_shots,
        "sound": sound,
        "prompt": prompt,
        "multi_prompt": multi_prompt,
        "duration": duration,
        "mode": mode,
        "aspect_ratio": aspect_ratio,
        "kling_elements_raw": kling_elements_raw,
    }


def _build_form_payload(api_key, form_state):
    input_payload = {
        "duration": str(int(form_state["duration"])),
        "mode": form_state["mode"],
        "aspect_ratio": form_state["aspect_ratio"],
        "sound": form_state["sound"],
        "multi_shots": form_state["multi_shots"],
    }

    if form_state["multi_shots"]:
        if not form_state["multi_prompt"]:
            raise ValueError("複数ショットが有効ですが、ショットごとのプロンプトが未入力です。")
        input_payload["multi_prompt"] = form_state["multi_prompt"]
    else:
        if not form_state["prompt"]:
            raise ValueError("プロンプトは必須です。")
        input_payload["prompt"] = form_state["prompt"]

    image_urls = []
    if form_state["start_frame"] is not None:
        url = _upload_input_image(api_key, form_state["start_frame"])
        if not url:
            raise ValueError("開始フレームのアップロードに失敗しました。")
        image_urls.append(url)
    if form_state["end_frame"] is not None:
        url = _upload_input_image(api_key, form_state["end_frame"])
        if not url:
            raise ValueError("終了フレームのアップロードに失敗しました。")
        image_urls.append(url)
    if image_urls:
        input_payload["image_urls"] = image_urls

    kling_elements_raw = form_state["kling_elements_raw"]
    if kling_elements_raw:
        try:
            input_payload["kling_elements"] = json.loads(kling_elements_raw)
        except Exception as e:
            raise ValueError(f"追加オプションのJSONが不正です: {e}") from e

    return input_payload


def _render_json_editor():
    default_text = json.dumps(DEFAULT_FORM_INPUT, indent=2)
    return st.text_area(
        "入力JSON",
        height=360,
        value=default_text,
        key="kling_json_input",
    )


def _parse_json_payload(raw_json):
    parsed = json.loads(raw_json)
    if not isinstance(parsed, dict):
        raise ValueError("JSON入力はオブジェクト形式で指定してください。")

    if "input" in parsed and isinstance(parsed["input"], dict):
        model = parsed.get("model")
        if model and model != "kling-3.0/video":
            raise ValueError("このタブで指定できるmodelは kling-3.0/video のみです。")
        return parsed["input"]

    return parsed


def _state_progress(state, elapsed):
    table = {
        "waiting": 0.15,
        "queuing": 0.25,
        "generating": 0.75,
        "success": 1.0,
        "fail": 1.0,
    }
    return max(table.get(state, 0.1), min(elapsed / 480.0, 0.95))


def _state_label(state):
    labels = {
        "waiting": "待機中",
        "queuing": "キュー待ち",
        "generating": "生成中",
        "success": "完了",
        "fail": "失敗",
    }
    return labels.get(state, state)


def render(api_key):
    """Render Tab 2: Kling 3.0 video generation."""
    _inject_styles()

    st.markdown(
        """
        <div class="kling-header">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
            <div>
              <div style="font-size:1.4rem;font-weight:800;">Kling 3.0 Video API</div>
              <div class="kling-chip">商用利用可</div>
            </div>
            <div style="font-size:0.9rem;color:#2563eb;font-weight:700;">API実行</div>
          </div>
          <p style="margin-top:10px;color:#4b5563;">
            テキストや画像フレームから、複数ショット構成と音声付きの動画を生成できます。
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "kling_recent_history" not in st.session_state:
        st.session_state.kling_recent_history = []

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown('<div class="kling-card">', unsafe_allow_html=True)
        st.markdown('<div class="kling-card-title">入力</div>', unsafe_allow_html=True)
        input_mode = st.radio(
            "input_mode",
            ["フォーム", "JSON"],
            horizontal=True,
            label_visibility="collapsed",
            key="kling_input_mode",
        )
        st.markdown(
            '<div class="kling-caption">フォーム入力とJSON入力は同じスキーマです。</div>',
            unsafe_allow_html=True,
        )

        form_state = None
        raw_json_input = None
        if input_mode == "フォーム":
            form_state = _render_form_fields()
        else:
            raw_json_input = _render_json_editor()

        run_btn = st.button("APIで生成する", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="kling-card">', unsafe_allow_html=True)
        st.markdown('<div class="kling-card-title">出力</div>', unsafe_allow_html=True)
        status_box = st.empty()
        progress_bar = st.progress(0)
        result_box = st.container()
        st.markdown("</div>", unsafe_allow_html=True)

    if run_btn:
        if not api_key:
            status_box.error("KIEAI API Keyが必要です。")
            return

        try:
            if input_mode == "フォーム":
                with st.spinner("フレームをアップロードして入力を準備中..."):
                    input_payload = _build_form_payload(api_key, form_state)
            else:
                input_payload = _parse_json_payload(raw_json_input)
        except Exception as e:
            status_box.error(str(e))
            return

        status_box.info("Kling 3.0 タスクを送信中...")
        task_id, create_err = kie_api.create_kling3_video_task(api_key, input_payload)
        if create_err:
            status_box.error(f"タスク作成に失敗しました: {create_err}")
            return

        status_box.success(f"タスクを受け付けました: {task_id}")
        with result_box:
            st.code(
                json.dumps(
                    {"model": "kling-3.0/video", "taskId": task_id, "input": input_payload},
                    ensure_ascii=False,
                    indent=2,
                ),
                language="json",
            )

        start_ts = time.time()
        final_state = "waiting"
        latest_data = {}

        while True:
            elapsed = time.time() - start_ts
            if elapsed > POLL_TIMEOUT_SECONDS:
                status_box.error("ポーリングがタイムアウトしました。同じタスクIDで後から状態を確認してください。")
                break

            poll_data, poll_err = kie_api.poll_job_record(api_key, task_id)
            if poll_err:
                status_box.warning(f"ポーリング警告: {poll_err}")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            latest_data = poll_data or {}
            final_state = str(latest_data.get("state", "waiting")).lower()
            progress_bar.progress(_state_progress(final_state, elapsed))
            status_box.info(f"状態: {_state_label(final_state)} | 経過: {int(elapsed)}秒")

            if final_state == "success":
                urls = kie_api.extract_result_urls(latest_data)
                progress_bar.progress(1.0)
                status_box.success("生成が完了しました。")
                with result_box:
                    if not urls:
                        st.warning("タスクは成功しましたが、結果URLが見つかりませんでした。")
                    for idx, url in enumerate(urls, start=1):
                        st.markdown(f"結果 {idx}")
                        st.video(url)
                        st.markdown(f"[動画 {idx} を開く]({url})")
                break

            if final_state == "fail":
                progress_bar.progress(1.0)
                fail_reason = latest_data.get("failMsg") or latest_data.get("error") or "不明なエラー"
                status_box.error(f"生成に失敗しました: {fail_reason}")
                break

            time.sleep(POLL_INTERVAL_SECONDS)

        st.session_state.kling_recent_history.insert(
            0,
            {
                "taskId": task_id,
                "status": final_state,
                "mode": input_payload.get("mode"),
                "duration": input_payload.get("duration"),
                "updatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        st.session_state.kling_recent_history = st.session_state.kling_recent_history[:20]

    st.markdown("### 最近の履歴")
    if st.session_state.kling_recent_history:
        display_history = [
            {
                "タスクID": item.get("taskId"),
                "状態": _state_label(item.get("status")),
                "モード": item.get("mode"),
                "長さ（秒）": item.get("duration"),
                "更新時刻": item.get("updatedAt"),
            }
            for item in st.session_state.kling_recent_history
        ]
        st.dataframe(display_history, use_container_width=True, hide_index=True)
    else:
        st.caption("まだKling 3.0のタスクはありません。")
