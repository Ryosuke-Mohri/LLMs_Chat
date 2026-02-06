"""
LLM Select Chat App - Streamlit Frontend（ルート配置版）
Azure OpenAI / Anthropic モデル選択チャットアプリ。
設定は .env と src.llm_select_chat.config から読む。
"""
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

# ========================================
# 詳細ログ（ファイル + コンソール）。set_page_config より前に初期化
# ========================================
def _setup_app_logging():
    root = Path(__file__).resolve().parent.parent.parent
    log_dir = root / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app_debug.log"
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG,
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
        force=True,
    )
    return logging.getLogger("llm_select_chat")

_app_log = _setup_app_logging()
_app_log.debug("script start (app_main loaded)")

import streamlit as st
import streamlit.components.v1 as components

from src.llm_select_chat.services import catalog, log_store, pricing, llm as llm_service
from src.llm_select_chat.utils import format as fmt_util, model_type as model_type_util

# フォントサイズを今の80%に固定（zoom プロパティを使用）
FONT_ZOOM = 0.8

# デバッグ: True のとき最初の CSS をスキップし st.write("test") のみ表示（切り分け用）
DEBUG_MINIMAL_RENDER = False

# 定数・パス（services に委譲。フッター表示用のみ）
LOG_FILE_PATH = log_store.get_log_file_path()


def _ensure_session_list_keys(session_data: dict) -> None:
    """古いログ形式でも KeyError しないよう、name_changes / errors を保証する。"""
    if "name_changes" not in session_data:
        session_data["name_changes"] = []
    if "errors" not in session_data:
        session_data["errors"] = []


def run_app():
    """毎 run で実行されるアプリ本体（Streamlit の rerun のたびに呼ばれる）。"""
    # ページ設定は streamlit_app.py でメインスクリプトの最初の st として実行済み
    _app_log.debug("run_app() entered")

    # ========================================
    # カスタムCSS（1本目: フォントzoomのみ。2本目以降は分割して白画面の原因を切り分け）
    # ========================================
    _app_log.debug("before first st.markdown (font zoom)")
    st.markdown(f"""
<style>
/* ===== フォントサイズ（80%固定）===== */
.main .block-container {{
    zoom: {FONT_ZOOM};
}}
@media (max-width: 992px) {{
    .main .block-container {{
        zoom: {FONT_ZOOM * 0.95};
    }}
}}
@media (max-width: 768px) {{
    .main .block-container {{
        zoom: {FONT_ZOOM * 0.9};
    }}
}}
</style>
""", unsafe_allow_html=True)
    _app_log.debug("after first st.markdown (font zoom)")

    # CSS チャンク1: 共通・セッションヘッダー・メッセージ・メトリクス・入力
    st.markdown("""
<style>
    * { transition: all 0.2s ease; }
    .session-header {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .model-badge {
        background: #f5f5f5;
        color: #424242;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 0.95em;
        display: inline-block;
        margin: 5px 0;
    }
    .user-message {
        background: linear-gradient(135deg, #f0f8ff 0%, #e8f4fc 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    .ai-message {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    .copy-btn {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: #e0e0e0;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.8em;
        color: #424242;
    }
    .copy-btn:hover { background: #bdbdbd; }
    .copy-btn.copied { background: #c8e6c9; color: #2e7d32; }
    .metric-box {
        background: linear-gradient(135deg, #fff8e1 0%, #fff3e0 100%);
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    .stTextInput > div > div > input { font-size: 16px; }
</style>
""", unsafe_allow_html=True)
    _app_log.debug("after CSS chunk 1")

    # CSS チャンク2: サイドバー背景・タイトル・ボタン高さ・popover
    st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #e8e8e8 !important; }
    [data-testid="stSidebar"] > div:first-child { background-color: #e8e8e8 !important; }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] { background-color: #e8e8e8 !important; }
    .sidebar-title {
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        color: #1565c0;
        padding: 5px 0 10px 0;
        margin-top: 0;
    }
    [data-testid="stSidebar"] button[kind="primary"] { min-height: 60px !important; }
    .main .block-container { background-color: white; }
    [data-testid="stSidebar"] button[data-testid="stPopoverButton"] {
        padding: 4px 8px !important;
        min-width: 32px !important;
        min-height: auto !important;
        height: auto !important;
        background-color: #f5f5f5 !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
        align-self: stretch !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stSidebar"] button[data-testid="stPopoverButton"]:hover { background-color: #e0e0e0 !important; }
    .active-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"] { background-color: #e3f2fd !important; }
    .active-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"]:hover { background-color: #bbdefb !important; }
    .completed-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"] { background-color: #e8f5e9 !important; }
    .completed-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"]:hover { background-color: #c8e6c9 !important; }
</style>
""", unsafe_allow_html=True)
    _app_log.debug("after CSS chunk 2")

    # CSS チャンク3: セッションボタン・アクティブ/終了済み・ゴミ箱・Expander・メインpopover・メトリクス・コード
    st.markdown("""
<style>
    [data-testid="stSidebar"] button[kind="secondary"] {
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: pre-line !important;
        line-height: 1.3 !important;
        padding: 6px 10px !important;
        min-height: auto !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        margin-bottom: 2px !important;
    }
    [data-testid="stSidebar"] [data-testid="column"] { padding: 0 2px !important; }
    [data-testid="stSidebar"] .stHorizontalBlock { gap: 4px !important; margin-bottom: 4px !important; align-items: stretch !important; }
    [data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #fff8e1 0%, #fffde7 100%) !important;
        color: #5d4037 !important;
    }
    .active-session-marker + div button[kind="secondary"] {
        background-color: #e3f2fd !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
    }
    .active-session-marker + div button[kind="secondary"]:hover { background-color: #bbdefb !important; }
    .completed-session-marker + div button[kind="secondary"] {
        background-color: #e8f5e9 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
    }
    .completed-session-marker + div button[kind="secondary"]:hover { background-color: #c8e6c9 !important; }
    .trash-button-marker + div button {
        background-color: #616161 !important;
        color: white !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    .trash-button-marker + div button:hover { background-color: #424242 !important; }
    .trash-button-marker + div button p { color: white !important; }
    [data-testid="stSidebar"] .stExpander { background-color: transparent !important; border: none !important; }
    [data-testid="stSidebar"] details summary {
        background-color: white !important;
        border-radius: 8px;
        padding: 10px 12px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
        margin-bottom: 4px;
    }
    [data-testid="stSidebar"] details[open] > div {
        background-color: white !important;
        border-radius: 8px;
        padding: 8px !important;
        margin-top: 4px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    }
    .main button[data-testid="stPopoverButton"] {
        background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    .main button[data-testid="stPopoverButton"]:hover {
        background: linear-gradient(135deg, #e0e0e0 0%, #d5d5d5 100%) !important;
    }
    .main [data-testid="stMetricValue"] { font-size: 1rem !important; }
    .main pre, .main code, .main [data-testid="stMarkdown"] pre, .main [data-testid="stMarkdown"] code {
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
    }
    .main pre { padding: 12px 16px !important; border-radius: 8px !important; overflow-x: auto !important; }
    .main code { padding: 2px 6px !important; border-radius: 4px !important; }
</style>
""", unsafe_allow_html=True)
    _app_log.debug("after CSS chunk 3")

    # ========================================
    # セッション状態の初期化
    # ========================================
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "is_new_session" not in st.session_state:
        st.session_state.is_new_session = True
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "chat"  # "chat" or "trash"
    if "delete_confirm_session" not in st.session_state:
        st.session_state.delete_confirm_session = None  # 削除確認中のセッションID
    if "generating_name" not in st.session_state:
        st.session_state.generating_name = False
    if "sidebar_rename_session_id" not in st.session_state:
        st.session_state.sidebar_rename_session_id = None  # 左ペインで名前変更フォーム表示中のセッションID

    # ========================================
    # メイン処理（例外時は白画面にせずエラー表示）
    # ========================================
    _app_log.debug("before get_all_models")
    try:
        all_models = catalog.get_all_models()
        _app_log.debug("get_all_models ok, count=%s", len(all_models))
    except Exception as e:
        _app_log.exception("get_all_models failed")
        st.error(f"モデル一覧の取得に失敗しました: {e}")
        st.exception(e)
        st.stop()

    # ========================================
    # サイドバー
    # ========================================
    st.sidebar.markdown('<div class="sidebar-title">🐱 LLM Select Chat</div>', unsafe_allow_html=True)

    # ログデータ読み込み
    _app_log.debug("before load_log_data")
    try:
        log_data = log_store.load_log_data()
        _app_log.debug("load_log_data ok, sessions count=%s", len(log_data.get("sessions", {})))
    except Exception as e:
        _app_log.exception("load_log_data failed")
        st.sidebar.error("ログの読み込みに失敗しました")
        st.error(f"ログの読み込みに失敗しました: {e}")
        st.exception(e)
        st.stop()
    sessions = log_data.get("sessions", {})

    # 新規セッション作成ボタン（PoC と同様に st.rerun() で再描画）
    _app_log.debug("before new session button")
    new_session_clicked = st.sidebar.button("➕ 新規セッション", use_container_width=True)
    if new_session_clicked:
        _app_log.debug("NEW SESSION BUTTON CLICKED: clearing state and rerun")
        st.session_state.current_session_id = None
        st.session_state.conversation_history = []
        st.session_state.selected_model = None
        st.session_state.is_new_session = True
        st.session_state.view_mode = "chat"
        st.session_state.delete_confirm_session = None
        st.session_state.sidebar_rename_session_id = None
        st.rerun()
    _app_log.debug("after new session block")

    st.sidebar.markdown("---")

    # セッション分類
    active_sessions = sorted(
        [(k, v) for k, v in sessions.items() if not v.get("deleted", False) and v.get("status", "active") == "active"],
        key=lambda x: x[1].get("updated_at", ""),
        reverse=True
    )
    completed_sessions = sorted(
        [(k, v) for k, v in sessions.items() if not v.get("deleted", False) and v.get("status") == "completed"],
        key=lambda x: x[1].get("updated_at", ""),
        reverse=True
    )
    deleted_sessions = sorted(
        [(k, v) for k, v in sessions.items() if v.get("deleted", False) and not v.get("purged_from_trash", False)],
        key=lambda x: x[1].get("deleted_at", ""),
        reverse=True
    )

    # --- ヘルパー関数: セッションアイテム表示 ---
    def render_session_item(session_id, session_info, container=None, show_resume=False, session_type="active"):
        """サイドバーのセッションアイテムをレンダリング

        Args:
            session_id: セッションID
            session_info: セッション情報
            container: 描画先コンテナ（Noneの場合はst.sidebar）
            show_resume: 再開ボタン表示フラグ
            session_type: セッションタイプ（"active" or "completed"）
        """
        if container is None:
            container = st.sidebar

        session_name = session_info.get("session_name", session_id)
        model_info = session_info.get("model", {})
        deployment_name = model_info.get("deployment_name", "不明")
        region_raw = model_info.get("region", "")
        region_display = fmt_util.format_region_display(region_raw)
        model_type = model_info.get("model_type", "openai")
        status = session_info.get("status", "active")
        constructor = model_info.get("constructor") or catalog.get_constructor_for_deployment(deployment_name)
        type_icon = model_info.get("constructor_icon") or model_type_util.get_constructor_icon(constructor)

        # CSSマーカーを挿入（セッションタイプ別のスタイル適用用）
        marker_class = "active-session-marker" if session_type == "active" else "completed-session-marker"
        container.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)

        # セッション選択行（カード形式）
        col1, col2 = container.columns([6, 1])
        with col1:
            # セッション名を表示（長すぎる場合は省略）
            display_name = session_name[:25] + "..." if len(session_name) > 25 else session_name
            # モデル情報を全体表示（省略なし）
            model_display = f"{type_icon} {deployment_name} | 📍{region_display}"

            # セッションカード風のボタン（2行表示）
            button_label = f"{display_name}\n{model_display}"
            if st.button(button_label, key=f"btn_{session_id}", use_container_width=True):
                st.session_state.current_session_id = session_id
                st.session_state.conversation_history = session_info.get("conversation_history", [])
                model_info_copy = model_info.copy()
                if not model_info_copy.get("api_key"):
                    model_info_copy["api_key"] = catalog.get_api_key_for_region(region_raw)
                st.session_state.selected_model = model_info_copy
                st.session_state.is_new_session = False
                st.session_state.view_mode = "chat"
                st.session_state.delete_confirm_session = None
                st.rerun()

        with col2:
            # メニューボタン（▾）
            with st.popover("▾"):
                # セッション名変更：ポップアップ内で入力・保存
                if st.session_state.get("sidebar_rename_session_id") == session_id:
                    new_name = st.text_input("新しいセッション名", value=session_name, key=f"sidebar_rename_input_{session_id}")
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("変更保存", key=f"sidebar_rename_save_{session_id}", use_container_width=True):
                            if new_name and new_name.strip():
                                log_data = log_store.load_log_data()
                                if session_id in log_data.get("sessions", {}):
                                    _ensure_session_list_keys(log_data["sessions"][session_id])
                                    old_name = log_data["sessions"][session_id]["session_name"]
                                    log_data["sessions"][session_id]["session_name"] = new_name.strip()
                                    log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                                    log_data["sessions"][session_id]["name_changes"].append({
                                        "timestamp": datetime.now().isoformat(),
                                        "old_name": old_name,
                                        "new_name": new_name.strip()
                                    })
                                    log_store.save_log_data(log_data)
                                st.session_state.sidebar_rename_session_id = None
                                st.rerun()
                    with col_cancel:
                        if st.button("キャンセル", key=f"sidebar_rename_cancel_{session_id}", use_container_width=True):
                            st.session_state.sidebar_rename_session_id = None
                            st.rerun()
                else:
                    if st.button("📝 名前変更", key=f"menu_rename_{session_id}", use_container_width=True):
                        st.session_state.sidebar_rename_session_id = session_id
                        st.rerun()

                # セッション名生成
                if st.button("✨ 名前生成", key=f"menu_gen_{session_id}", use_container_width=True):
                    with st.spinner("生成中..."):
                        try:
                            mi = model_info
                            if mi.get("model_type") == "anthropic":
                                mi = {**mi, "endpoint": catalog.get_anthropic_endpoint_for_region(mi.get("region", "")) or mi.get("endpoint", "")}
                            generated = llm_service.generate_session_name(
                                mi, session_info.get("conversation_history", [])
                            )
                        except Exception as e:
                            st.error(f"セッション名生成エラー: {e}")
                            generated = None
                        if generated:
                            log_data = log_store.load_log_data()
                            _ensure_session_list_keys(log_data["sessions"][session_id])
                            old_name = log_data["sessions"][session_id]["session_name"]
                            log_data["sessions"][session_id]["session_name"] = generated
                            log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                            log_data["sessions"][session_id]["name_changes"].append({
                                "timestamp": datetime.now().isoformat(),
                                "old_name": old_name,
                                "new_name": generated,
                                "generated_by_llm": True
                            })
                            log_store.save_log_data(log_data)
                            st.rerun()

                # セッション終了/再開
                if status == "active":
                    if st.button("🏁 終了", key=f"menu_end_{session_id}", use_container_width=True):
                        log_data = log_store.load_log_data()
                        session_data = log_data["sessions"][session_id]
                        _ensure_session_list_keys(session_data)
                        messages = session_data.get("messages", [])

                        total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
                        total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
                        total_turns = len(messages)
                        response_times = [m.get("response", {}).get("response_time_seconds", 0) for m in messages]
                        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

                        session_end = datetime.now()
                        session_start = datetime.fromisoformat(session_data.get("created_at", session_end.isoformat()))
                        session_duration = (session_end - session_start).total_seconds()

                        session_data["status"] = "completed"
                        session_data["ended_at"] = session_end.isoformat()
                        session_data["updated_at"] = session_end.isoformat()
                        session_data["stats"] = {
                            "total_turns": total_turns,
                            "total_tokens": total_tokens,
                            "total_cost_usd": round(total_cost, 6),
                            "total_cost_jpy": round(total_cost * pricing.get_usd_to_jpy(), 2),
                            "avg_response_time_seconds": round(avg_response_time, 3),
                            "min_response_time_seconds": round(min(response_times), 3) if response_times else 0,
                            "max_response_time_seconds": round(max(response_times), 3) if response_times else 0,
                            "session_duration_seconds": round(session_duration, 3),
                            "conversation_length": len(session_data.get("conversation_history", []))
                        }
                        log_store.save_log_data(log_data)
                        st.rerun()
                else:
                    if st.button("🔄 再開", key=f"menu_resume_{session_id}", use_container_width=True):
                        log_data = log_store.load_log_data()
                        log_data["sessions"][session_id]["status"] = "active"
                        log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                        log_store.save_log_data(log_data)
                        st.session_state.current_session_id = session_id
                        st.session_state.conversation_history = session_info.get("conversation_history", [])
                        model_info_copy = model_info.copy()
                        if not model_info_copy.get("api_key"):
                            model_info_copy["api_key"] = catalog.get_api_key_for_region(region_raw)
                        st.session_state.selected_model = model_info_copy
                        st.session_state.is_new_session = False
                        st.session_state.view_mode = "chat"
                        st.rerun()

                # 削除（2段階確認）
                if st.session_state.delete_confirm_session == session_id:
                    st.warning("本当に削除しますか？\n⚠️ 削除後は復元できません")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✓ 削除", key=f"confirm_del_{session_id}", type="primary"):
                            log_data = log_store.load_log_data()
                            log_data["sessions"][session_id]["deleted"] = True
                            log_data["sessions"][session_id]["deleted_at"] = datetime.now().isoformat()
                            log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                            log_store.save_log_data(log_data)
                            if st.session_state.current_session_id == session_id:
                                st.session_state.current_session_id = None
                                st.session_state.conversation_history = []
                                st.session_state.selected_model = None
                                st.session_state.is_new_session = True
                            st.session_state.delete_confirm_session = None
                            st.rerun()
                    with col_b:
                        if st.button("✗ キャンセル", key=f"cancel_del_{session_id}"):
                            st.session_state.delete_confirm_session = None
                            st.rerun()
                else:
                    if st.button("🗑️ 削除", key=f"menu_del_{session_id}", use_container_width=True):
                        st.session_state.delete_confirm_session = session_id
                        st.rerun()

    # --- アクティブセッション ---
    with st.sidebar.expander(f"▶️ アクティブ ({len(active_sessions)})", expanded=True):
        if active_sessions:
            for session_id, session_info in active_sessions:
                render_session_item(session_id, session_info, container=st, session_type="active")
        else:
            st.caption("アクティブなセッションはありません")

    # --- 終了済みセッション ---
    with st.sidebar.expander(f"✅ 終了済み ({len(completed_sessions)})", expanded=False) as completed_expander:
        if completed_sessions:
            for session_id, session_info in completed_sessions:
                render_session_item(session_id, session_info, container=st, show_resume=True, session_type="completed")
        else:
            st.caption("終了済みのセッションはありません")

    st.sidebar.markdown("---")

    # --- ゴミ箱 ---
    st.sidebar.markdown('<div class="trash-button-marker"></div>', unsafe_allow_html=True)
    if st.sidebar.button(f"🗑️ ゴミ箱 ({len(deleted_sessions)})", use_container_width=True):
        st.session_state.view_mode = "trash"
        st.session_state.current_session_id = None
        st.session_state.is_new_session = False
        st.session_state.sidebar_rename_session_id = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"アクティブ: {len(active_sessions)} | 終了: {len(completed_sessions)} | 削除: {len(deleted_sessions)}")

    # ========================================
    # メインコンテンツ
    # ========================================

    # ゴミ箱表示モード
    _app_log.debug(
        "main branch: view_mode=%s is_new_session=%s current_session_id=%s",
        st.session_state.view_mode,
        st.session_state.is_new_session,
        st.session_state.current_session_id,
    )
    if st.session_state.view_mode == "trash":
        st.title("ゴミ箱")
        st.markdown("---")

        log_data = log_store.load_log_data()
        deleted_sessions = sorted(
            [(k, v) for k, v in log_data.get("sessions", {}).items() if v.get("deleted", False) and not v.get("purged_from_trash", False)],
            key=lambda x: x[1].get("deleted_at", ""),
            reverse=True
        )

        if deleted_sessions:
            # ゴミ箱を空にするボタン（上部）
            if st.button("🗑️ ゴミ箱を空にする", type="primary", use_container_width=False):
                log_data = log_store.load_log_data()
                for sid, sinfo in list(log_data.get("sessions", {}).items()):
                    if sinfo.get("deleted", False) and not sinfo.get("purged_from_trash", False):
                        log_data["sessions"][sid]["purged_from_trash"] = True
                        log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
                log_store.save_log_data(log_data)
                st.rerun()
            st.markdown("")

            st.warning("⚠️ 削除されたセッションは復元できません（履歴として表示のみ）")
            st.markdown("")

            for session_id, session_info in deleted_sessions:
                session_name = session_info.get("session_name", session_id)
                model_info = session_info.get("model", {})
                constructor = model_info.get("constructor") or catalog.get_constructor_for_deployment(model_info.get("deployment_name", ""))
                type_icon = model_info.get("constructor_icon") or model_type_util.get_constructor_icon(constructor)

                messages = session_info.get("messages", [])
                total_turns = len(messages)
                total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
                total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)

                with st.container():
                    col_cb, col1, col2, col3, col4, col5 = st.columns([0.4, 2.6, 2, 1, 1, 2])
                    with col_cb:
                        st.checkbox("", key=f"trash_cb_{session_id}", label_visibility="collapsed")
                    with col1:
                        st.markdown(f"**{session_name}**")
                        st.caption(f"{type_icon} {model_info.get('deployment_name', '不明')} | 📍 {fmt_util.format_region_display(model_info.get('region', ''))}")
                    with col2:
                        st.caption(f"🕐 作成: {fmt_util.format_timestamp(session_info.get('created_at', ''))}")
                        st.caption(f"🗑️ 削除: {fmt_util.format_timestamp(session_info.get('deleted_at', ''))}")
                    with col3:
                        st.metric("ターン", total_turns)
                    with col4:
                        st.metric("トークン", f"{total_tokens:,}")
                    with col5:
                        st.metric("コスト", f"${total_cost:.4f}")
                    st.markdown("---")

            # チェック済みセッションを取得
            trash_checked_ids = {sid for sid, _ in deleted_sessions if st.session_state.get(f"trash_cb_{sid}", False)}
            has_checked = len(trash_checked_ids) > 0

            # 選択したセッションを削除するボタン（1つ以上チェック時のみ有効）
            if has_checked:
                if st.button("選択したセッションを削除", type="primary", use_container_width=False):
                    log_data = log_store.load_log_data()
                    for sid in trash_checked_ids:
                        if sid in log_data.get("sessions", {}):
                            log_data["sessions"][sid]["purged_from_trash"] = True
                            log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
                    log_store.save_log_data(log_data)
                    st.rerun()
            else:
                st.button("選択したセッションを削除", type="primary", disabled=True, use_container_width=False, help="削除するセッションを1つ以上チェックしてください")
        else:
            st.info("🗑️ ゴミ箱は空です")

        # 戻るボタン
        if st.button("↩️ 戻る", use_container_width=True):
            st.session_state.view_mode = "chat"
            st.session_state.is_new_session = True
            st.rerun()

    else:
        # 現在のセッション情報取得
        current_session = None
        if st.session_state.current_session_id:
            log_data = log_store.load_log_data()
            current_session = log_data.get("sessions", {}).get(st.session_state.current_session_id)
            if current_session:
                _ensure_session_list_keys(current_session)

        # ========================================
        # ヘッダー部分
        # ========================================
        if st.session_state.is_new_session or current_session is None:
            _app_log.debug("rendering new session (model selection) screen")
            # 新規セッション - モデル選択
            st.title("新規チャットセッション")
            st.markdown("---")

            st.subheader("🤖 使用するモデルを選択")

            if all_models:
                model_options = [m["display_name"] for m in all_models]
                selected_display_name = st.selectbox(
                    "モデル選択",
                    model_options,
                    index=0
                )

                # 選択されたモデル情報を取得
                selected_model_info = next(
                    (m for m in all_models if m["display_name"] == selected_display_name),
                    None
                )

                if selected_model_info:
                    st.info(f"""
                **選択されたモデル:**
                - デプロイメント: `{selected_model_info['deployment_name']}`
                - リージョン: `{fmt_util.format_region_display(selected_model_info.get('region', ''))}`
                - コンストラクター: {selected_model_info.get('constructor_icon', '🔵')} `{selected_model_info.get('constructor', 'その他')}`
                - エンドポイント: `{selected_model_info['endpoint']}`
                """)

                    # セッション開始ボタン
                    if st.button("🚀 チャットを開始", type="primary", use_container_width=True):
                        # 新規セッション作成
                        session_start = datetime.now()
                        new_session_id = session_start.strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
                        auto_session_name = f"Session_{session_start.strftime('%Y%m%d_%H%M%S')}"

                        config = selected_model_info["config"]

                        new_session = {
                            "session_id": new_session_id,
                            "session_name": auto_session_name,
                            "created_at": session_start.isoformat(),
                            "updated_at": session_start.isoformat(),
                            "status": "active",
                            "model": {
                                "deployment_name": selected_model_info["deployment_name"],
                                "region": selected_model_info["region"],
                                "model_type": selected_model_info["model_type"],
                                "constructor": selected_model_info.get("constructor", catalog.get_constructor_for_deployment(selected_model_info["deployment_name"])),
                                "constructor_icon": selected_model_info.get("constructor_icon", model_type_util.get_constructor_icon(selected_model_info.get("constructor", "その他"))),
                                "endpoint": selected_model_info["endpoint"],
                                "api_version": config.get("Azure API Version", "2024-12-01-preview"),
                                "api_key": config.get("Azure API Key", "")
                            },
                            "config": {
                                "pricing": pricing.PRICING_DEFAULT,
                                "usd_to_jpy": pricing.get_usd_to_jpy()
                            },
                            "conversation_history": [
                                {"role": "system", "content": "あなたは親切で知識豊富なアシスタントです。日本語で回答してください。会話の文脈を踏まえて応答してください。"}
                            ],
                            "messages": [],
                            "errors": [],
                            "stats": None,
                            "name_changes": []
                        }

                        log_data = log_store.load_log_data()
                        log_data["sessions"][new_session_id] = new_session
                        log_store.save_log_data(log_data)

                        st.session_state.current_session_id = new_session_id
                        st.session_state.conversation_history = new_session["conversation_history"]
                        st.session_state.selected_model = new_session["model"]
                        st.session_state.is_new_session = False
                        st.rerun()
            else:
                st.error("利用可能なモデルがありません。設定ファイルを確認してください。")

        else:
            # 既存セッション - チャット画面
            session_name = current_session.get("session_name", st.session_state.current_session_id)
            model_info = current_session.get("model", {})
            session_status = current_session.get("status", "active")
            is_completed = session_status == "completed"

            # ========================================
            # セッションヘッダー
            # ========================================
            st.title(session_name)
            created_at = current_session.get("created_at", "")
            if created_at:
                st.caption(f"📅 作成: {fmt_util.format_timestamp(created_at)}")
        
            col_left, col_right = st.columns([3, 1])
            with col_right:
                with st.popover("操作"):
                    # セッション名変更
                    new_name = st.text_input("📝 新しいセッション名", value=session_name, key=f"rename_input_{st.session_state.current_session_id}")
                    if st.button("入力した名前に変更", key="rename_btn", use_container_width=True):
                        if new_name and new_name != session_name:
                            log_data = log_store.load_log_data()
                            sid = st.session_state.current_session_id
                            _ensure_session_list_keys(log_data["sessions"][sid])
                            old_name = log_data["sessions"][sid]["session_name"]
                            log_data["sessions"][sid]["session_name"] = new_name
                            log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
                            log_data["sessions"][sid]["name_changes"].append({
                                "timestamp": datetime.now().isoformat(),
                                "old_name": old_name,
                                "new_name": new_name
                            })
                            log_store.save_log_data(log_data)
                            st.success("セッション名を変更しました")
                            st.rerun()
                
                    # セッション名生成
                    if st.button("✨ LLMで名前を生成", key="gen_name_btn", use_container_width=True):
                        with st.spinner("生成中..."):
                            try:
                                mi = model_info
                                if mi.get("model_type") == "anthropic":
                                    mi = {**mi, "endpoint": catalog.get_anthropic_endpoint_for_region(mi.get("region", "")) or mi.get("endpoint", "")}
                                generated = llm_service.generate_session_name(
                                    mi,
                                    st.session_state.conversation_history,
                                )
                            except Exception as e:
                                st.error(f"セッション名生成エラー: {e}")
                                generated = None
                            if generated:
                                log_data = log_store.load_log_data()
                                sid = st.session_state.current_session_id
                                _ensure_session_list_keys(log_data["sessions"][sid])
                                old_name = log_data["sessions"][sid]["session_name"]
                                log_data["sessions"][sid]["session_name"] = generated
                                log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
                                log_data["sessions"][sid]["name_changes"].append({
                                    "timestamp": datetime.now().isoformat(),
                                    "old_name": old_name,
                                    "new_name": generated,
                                    "generated_by_llm": True
                                })
                                log_store.save_log_data(log_data)
                                st.success(f"生成完了: {generated}")
                                st.rerun()
                
                    # セッション終了/再開
                    if session_status == "active":
                        if st.button("🏁 このセッションを終了", key="end_session_btn", use_container_width=True):
                            log_data = log_store.load_log_data()
                            session_data = log_data["sessions"][st.session_state.current_session_id]
                            _ensure_session_list_keys(session_data)
                            messages = session_data.get("messages", [])
                        
                            total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
                            total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
                            total_turns = len(messages)
                            response_times = [m.get("response", {}).get("response_time_seconds", 0) for m in messages]
                            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                        
                            session_end = datetime.now()
                            session_start = datetime.fromisoformat(session_data.get("created_at", session_end.isoformat()))
                            session_duration = (session_end - session_start).total_seconds()
                        
                            session_data["status"] = "completed"
                            session_data["ended_at"] = session_end.isoformat()
                            session_data["updated_at"] = session_end.isoformat()
                            session_data["stats"] = {
                                "total_turns": total_turns,
                                "total_tokens": total_tokens,
                                "total_cost_usd": round(total_cost, 6),
                                "total_cost_jpy": round(total_cost * pricing.get_usd_to_jpy(), 2),
                                "avg_response_time_seconds": round(avg_response_time, 3),
                                "min_response_time_seconds": round(min(response_times), 3) if response_times else 0,
                                "max_response_time_seconds": round(max(response_times), 3) if response_times else 0,
                                "session_duration_seconds": round(session_duration, 3),
                                "conversation_length": len(session_data.get("conversation_history", []))
                            }
                            log_store.save_log_data(log_data)
                            st.success("セッションを終了しました")
                            st.rerun()
                    else:
                        if st.button("🔄 セッションを再開", key="resume_session_btn", use_container_width=True):
                            log_data = log_store.load_log_data()
                            log_data["sessions"][st.session_state.current_session_id]["status"] = "active"
                            log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                            log_store.save_log_data(log_data)
                            st.success("セッションを再開しました")
                            st.rerun()
                
                    # 削除（2段階確認）
                    if st.session_state.delete_confirm_session == st.session_state.current_session_id:
                        st.warning("本当に削除しますか？\n⚠️ 削除後は復元できません")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ 削除", key="confirm_del_main", type="primary"):
                                log_data = log_store.load_log_data()
                                log_data["sessions"][st.session_state.current_session_id]["deleted"] = True
                                log_data["sessions"][st.session_state.current_session_id]["deleted_at"] = datetime.now().isoformat()
                                log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                                log_store.save_log_data(log_data)
                                st.session_state.current_session_id = None
                                st.session_state.conversation_history = []
                                st.session_state.selected_model = None
                                st.session_state.is_new_session = True
                                st.session_state.delete_confirm_session = None
                                st.rerun()
                        with col_b:
                            if st.button("✗ キャンセル", key="cancel_del_main"):
                                st.session_state.delete_confirm_session = None
                                st.rerun()
                    else:
                        if st.button("🗑️ このセッションを削除", key="delete_session_btn", use_container_width=True):
                            st.session_state.delete_confirm_session = st.session_state.current_session_id
                            st.rerun()
        
            # モデル情報表示（変更不可）※コンストラクターで表示
            constructor = model_info.get("constructor") or catalog.get_constructor_for_deployment(model_info.get("deployment_name", ""))
            constructor_icon = model_info.get("constructor_icon") or model_type_util.get_constructor_icon(constructor)
            st.markdown(f"""
            <div class="model-badge">
                {constructor_icon} {model_info.get('deployment_name', '不明')} | 📍 {fmt_util.format_region_display(model_info.get('region', ''))} | {constructor}
            </div>
            """, unsafe_allow_html=True)
        
            st.caption("※ セッション途中でモデルを変更することはできません")
        
            st.markdown("---")
        
            # ========================================
            # メトリクス表示
            # ========================================
            # ページ上部アンカー
            st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)
        
            stats = current_session.get("stats")
            messages = current_session.get("messages", [])
        
            # リアルタイム統計計算
            total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
            total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
            total_turns = len(messages)
            avg_response_time = (
                sum(m.get("response", {}).get("response_time_seconds", 0) for m in messages) / len(messages)
                if messages else 0
            )
        
            # メトリクス行
            metric_cols = st.columns([1, 1, 1, 1, 1])
            with metric_cols[0]:
                st.metric("ターン数", total_turns)
            with metric_cols[1]:
                st.metric("総トークン", f"{total_tokens:,}")
            with metric_cols[2]:
                st.metric("コスト (USD)", f"${total_cost:.4f}")
            with metric_cols[3]:
                st.metric("コスト (JPY)", f"¥{(total_cost * pricing.get_usd_to_jpy()):.2f}")
            with metric_cols[4]:
                st.metric("平均応答時間", f"{avg_response_time:.2f}秒")
        
            st.markdown("---")
        
            # ========================================
            # 会話履歴表示（最下部へを同段右側に配置）
            # ========================================
            col_hist, col_bottom = st.columns([4, 1])
            with col_hist:
                st.subheader("📝 会話履歴")
            with col_bottom:
                st.markdown("""
                <a href="#page-bottom" style="text-decoration:none;">
                    <div style="text-align:center; padding:8px; background:#e3f2fd; border-radius:8px; cursor:pointer;">
                        ⬇️ 最下部へ
                    </div>
                </a>
                """, unsafe_allow_html=True)
        
            conversation = st.session_state.conversation_history
        
            # 会話インデックスからメッセージログへのマッピング
            user_msg_idx = 0
            for i, msg in enumerate(conversation):
                if msg["role"] == "system":
                    continue  # システムメッセージは非表示
            
                if msg["role"] == "user":
                    # 対応するメッセージログからタイムスタンプを取得
                    msg_log = messages[user_msg_idx] if user_msg_idx < len(messages) else None
                    timestamp_str = ""
                    if msg_log:
                        request_ts = msg_log.get("request", {}).get("timestamp", "")
                        if request_ts:
                            timestamp_str = f'<span style="color:#888; font-size:0.8em; float:right;">📤 {fmt_util.format_timestamp(request_ts)}</span>'
                
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>🧑 ユーザー</strong>{timestamp_str}
                        <p style="margin-top:10px;">{msg['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
                elif msg["role"] == "assistant":
                    # 対応するメッセージログを検索
                    msg_log = messages[user_msg_idx] if user_msg_idx < len(messages) else None
                    user_msg_idx += 1  # 次のユーザーメッセージへ
                
                    if msg_log:
                        response_time = msg_log.get("response", {}).get("response_time_seconds", 0)
                        tokens = msg_log.get("metrics", {}).get("total_tokens", 0)
                        cost_jpy = msg_log.get("cost", {}).get("total_cost_jpy", 0)
                        metrics_str = f"⏱️ {response_time:.2f}秒 | 🔢 {tokens:,}トークン | 💰 ¥{cost_jpy:.2f}"
                    else:
                        metrics_str = ""
                
                    # ユニークなメッセージIDを生成
                    msg_id = f"ai_msg_{i}"
                    # コンテンツをエスケープ（JavaScriptで使用）
                    escaped_content = msg['content'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('`', '\\`')
                
                    # AI回答表示（コピーボタンなしのマークダウン部分）
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>🤖 AI</strong> <span style="color:#666; font-size:0.9em;">{metrics_str}</span>
                        <div style="margin-top:10px;">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                    # コピーボタン（components.htmlで動作するJavaScript）
                    copy_html = f"""
                    <div style="text-align: right; margin-top: -10px; margin-bottom: 10px;">
                        <button id="copy_btn_{msg_id}" onclick="copyText_{msg_id}()" style="
                            background: #e0e0e0;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 0.85em;
                            color: #424242;
                        ">📋 Copy</button>
                    </div>
                    <script>
                    function copyText_{msg_id}() {{
                        const text = `{escaped_content}`;
                        navigator.clipboard.writeText(text).then(function() {{
                            var btn = document.getElementById('copy_btn_{msg_id}');
                            btn.innerHTML = '✓ Copied!';
                            btn.style.background = '#c8e6c9';
                            btn.style.color = '#2e7d32';
                            setTimeout(function() {{
                                btn.innerHTML = '📋 Copy';
                                btn.style.background = '#e0e0e0';
                                btn.style.color = '#424242';
                            }}, 2000);
                        }}).catch(function(err) {{
                            alert('コピーに失敗しました');
                        }});
                    }}
                    </script>
                    """
                    components.html(copy_html, height=40)
        
            # 最上部へのナビゲーション
            st.markdown("""
            <div style="display:flex; justify-content:center; margin:10px 0;">
                <a href="#page-top" style="text-decoration:none;">
                    <div style="text-align:center; padding:8px 16px; background:#e8f5e9; border-radius:8px; cursor:pointer;">
                        ⬆️ 最上部へ
                    </div>
                </a>
            </div>
            <div id="page-bottom"></div>
            """, unsafe_allow_html=True)
        
            st.markdown("---")
    
            # ========================================
            # プロンプト入力フォーム
            # ========================================
        
            # 終了済みセッションの場合は入力を無効化
            if is_completed:
                st.info("✅ このセッションは終了済みです。メッセージを送信するには、セッションを再開してください。")
            
                if st.button("🔄 セッションを再開してチャットを続ける", type="primary", use_container_width=True):
                    log_data = log_store.load_log_data()
                    log_data["sessions"][st.session_state.current_session_id]["status"] = "active"
                    log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                    log_store.save_log_data(log_data)
                    st.success("セッションを再開しました")
                    st.rerun()
            else:
                st.subheader("💬 メッセージ送信")
            
                with st.form(key="chat_form", clear_on_submit=True):
                    user_input = st.text_area(
                        "プロンプトを入力",
                        height=100,
                        placeholder="メッセージを入力してください...",
                        key="user_input"
                    )
                
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        submit_button = st.form_submit_button("📤 送信", type="primary", use_container_width=True)
        
            if not is_completed and submit_button and user_input.strip():
                # API呼び出し
                model_type = model_info.get("model_type", "openai")
                type_display = model_type_util.get_model_type_display(model_type)
                deployment_name = model_info.get("deployment_name", "")
            
                # API Key を取得（保存されていなければリージョンから取得）
                api_key = model_info.get("api_key", "")
                if not api_key:
                    api_key = catalog.get_api_key_for_region(model_info.get("region", ""))
                    # セッションに API Key を保存
                    if api_key:
                        log_data = log_store.load_log_data()
                        log_data["sessions"][st.session_state.current_session_id]["model"]["api_key"] = api_key
                        log_store.save_log_data(log_data)
            
                # モデル別料金を取得
                model_pricing = pricing.get_pricing_for_model(deployment_name, model_type)
            
                with st.spinner(f"🔄 {type_display['icon']} AIが応答を生成中..."):
                    try:
                        st.session_state.conversation_history.append({
                            "role": "user",
                            "content": user_input,
                        })
                        request_time = datetime.now()
                        system_message = ""
                        for msg in st.session_state.conversation_history:
                            if msg.get("role") == "system":
                                system_message = msg.get("content", "")
                                break
                        # Anthropic の場合は .env の ANTHROPIC_ENDPOINT を常に使用（セッションキャッシュに依存しない）
                        if model_type == "anthropic":
                            endpoint = catalog.get_anthropic_endpoint_for_region(model_info.get("region", "")) or model_info.get("endpoint", "")
                        else:
                            endpoint = model_info.get("endpoint", "")
                        result = llm_service.call_llm_chat(
                            model_type=model_type,
                            deployment_name=deployment_name,
                            api_key=api_key,
                            endpoint=endpoint,
                            api_version=model_info.get("api_version", "2024-12-01-preview"),
                            messages=st.session_state.conversation_history,
                            system_message=system_message or None,
                            max_tokens=4000,
                        )
                        response_time_dt = datetime.now()
                        ai_response = result["ai_response"]
                        prompt_tokens = result["prompt_tokens"]
                        completion_tokens = result["completion_tokens"]
                        total_tokens_turn = result["total_tokens"]
                        elapsed = result["response_time_seconds"]
                        cost_info = pricing.calculate_cost(
                            prompt_tokens, completion_tokens, model_pricing
                        )
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": ai_response,
                        })
                        message_log = {
                            "turn": len(messages) + 1,
                            "request": {
                                "timestamp": request_time.isoformat(),
                                "user_input": user_input,
                                "user_input_chars": len(user_input),
                            },
                            "response": {
                                "timestamp": response_time_dt.isoformat(),
                                "response_time_seconds": result["response_time_seconds"],
                                "model": result["response_model"],
                                "model_type": model_type,
                                "region": model_info.get("region", ""),
                                "response_id": result["response_id"],
                                "finish_reason": result["finish_reason"],
                                "ai_response": ai_response,
                                "ai_response_chars": len(ai_response),
                            },
                            "metrics": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": total_tokens_turn,
                                "tokens_per_second": round(completion_tokens / elapsed, 2) if elapsed > 0 else 0,
                            },
                            "cost": cost_info,
                        }
                        log_data = log_store.load_log_data()
                        sid = st.session_state.current_session_id
                        log_data["sessions"][sid]["messages"].append(message_log)
                        log_data["sessions"][sid]["conversation_history"] = st.session_state.conversation_history
                        log_data["sessions"][sid]["updated_at"] = response_time_dt.isoformat()
                        log_store.save_log_data(log_data)
                        st.rerun()
                    except Exception as e:
                        # エラー処理
                        error_time = datetime.now()
                        st.session_state.conversation_history.pop()  # 失敗したユーザー入力を削除
                    
                        error_log = {
                            "turn": len(messages) + 1,
                            "timestamp": error_time.isoformat(),
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "user_input": user_input
                        }
                    
                        log_data = log_store.load_log_data()
                        sid = st.session_state.current_session_id
                        _ensure_session_list_keys(log_data["sessions"][sid])
                        log_data["sessions"][sid]["errors"].append(error_log)
                        log_data["sessions"][sid]["updated_at"] = error_time.isoformat()
                        log_store.save_log_data(log_data)
                    
                        st.error(f"❌ エラーが発生しました: {type(e).__name__}: {e}")
        
            # ========================================
            # エラー表示
            # ========================================
            errors = current_session.get("errors", [])
            if errors:
                with st.expander(f"❌ エラー履歴 ({len(errors)}件)", expanded=False):
                    for error in errors:
                        st.error(f"""
                        **{error.get('error_type', 'Error')}** ({fmt_util.format_timestamp(error.get('timestamp', ''))})
                    
                        {error.get('error_message', '')[:200]}...
                        """)

    # ========================================
    # フッター
    # ========================================
    st.markdown("---")
    st.caption(f"📁 ログファイル: {LOG_FILE_PATH} | デバッグログ: data/app_debug.log")


if __name__ == "__main__":
    run_app()
