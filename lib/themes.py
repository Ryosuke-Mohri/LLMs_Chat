"""
テーマ定義モジュール
ライト/ダーク配色の辞書 + CSS テンプレート生成
"""

# ========================================
# 配色辞書
# ========================================
THEMES = {
    "light": {
        # --- 全体背景 ---
        "sidebar_bg": "#e8e8e8",
        "main_bg": "#ffffff",
        "app_bg": "#ffffff",

        # --- テキスト ---
        "text_primary": "#333333",
        "text_secondary": "#555555",
        "text_muted": "#888888",
        "timestamp_color": "#888888",
        "ai_metrics_color": "#666666",

        # --- セッションヘッダー ---
        "session_header_start": "#2e7d32",
        "session_header_end": "#43a047",
        "session_header_text": "#ffffff",

        # --- モデルバッジ ---
        "model_badge_bg": "#f5f5f5",
        "model_badge_text": "#424242",

        # --- ユーザーメッセージ ---
        "user_msg_bg_start": "#f0f8ff",
        "user_msg_bg_end": "#e8f4fc",
        "user_msg_border": "#2196f3",

        # --- AI メッセージ ---
        "ai_msg_bg_start": "#fafafa",
        "ai_msg_bg_end": "#f5f5f5",
        "ai_msg_border": "#4caf50",

        # --- コピーボタン ---
        "copy_btn_bg": "#e0e0e0",
        "copy_btn_text": "#424242",
        "copy_btn_hover_bg": "#bdbdbd",
        "copy_btn_copied_bg": "#c8e6c9",
        "copy_btn_copied_text": "#2e7d32",

        # --- メトリクスボックス ---
        "metric_box_bg_start": "#fff8e1",
        "metric_box_bg_end": "#fff3e0",

        # --- サイドバー ---
        "sidebar_title_color": "#1565c0",
        "popover_bg": "#f5f5f5",
        "popover_border": "#d0d0d0",
        "popover_hover_bg": "#e0e0e0",

        # --- セッションボタン ---
        "btn_secondary_border": "#d0d0d0",
        "active_session_bg": "#e3f2fd",
        "active_session_hover": "#bbdefb",
        "completed_session_bg": "#e8f5e9",
        "completed_session_hover": "#c8e6c9",

        # --- 新規セッションボタン ---
        "new_session_btn_start": "#1565c0",
        "new_session_btn_end": "#1976d2",
        "new_session_btn_hover_start": "#fff8e1",
        "new_session_btn_hover_end": "#fffde7",
        "new_session_btn_hover_text": "#5d4037",

        # --- ゴミ箱ボタン ---
        "trash_btn_bg": "#616161",
        "trash_btn_hover_bg": "#424242",
        "trash_btn_text": "#ffffff",

        # --- Expander ---
        "expander_header_bg": "#ffffff",
        "expander_content_bg": "#ffffff",

        # --- メインエリア popover ---
        "main_popover_bg_start": "#f5f5f5",
        "main_popover_bg_end": "#eeeeee",
        "main_popover_hover_start": "#e0e0e0",
        "main_popover_hover_end": "#d5d5d5",

        # --- コードブロック ---
        "code_bg": "#1e1e1e",
        "code_text": "#d4d4d4",

        # --- メインプライマリボタン ---
        "main_primary_btn_start": "#c8e6c9",
        "main_primary_btn_end": "#a5d6a7",
        "main_primary_btn_text": "#2e7d32",
        "main_primary_btn_hover_start": "#a5d6a7",
        "main_primary_btn_hover_end": "#81c784",
        "main_primary_btn_hover_text": "#1b5e20",

        # --- オーバーレイ ---
        "overlay_bg": "rgba(255, 255, 255, 0.6)",
        "overlay_text": "#333333",
        "spinner_border": "#e0e0e0",
        "spinner_top": "#2e7d32",

        # --- シャドウ ---
        "shadow_xs": "rgba(0, 0, 0, 0.05)",
        "shadow_sm": "rgba(0, 0, 0, 0.08)",
        "shadow_md": "rgba(0, 0, 0, 0.15)",
        "shadow_lg": "rgba(0, 0, 0, 0.2)",

        # --- ナビゲーションリンク ---
        "nav_bottom_bg": "#e3f2fd",
        "nav_top_bg": "#e8f5e9",
        "nav_text": "#333333",

        # --- Streamlit ネイティブ override ---
        "st_app_bg": "#ffffff",
        "st_widget_bg": "#ffffff",
        "st_widget_border": "#d0d0d0",
        "st_input_bg": "#ffffff",
        "st_input_text": "#333333",
        "st_label_text": "#333333",
        "st_caption_text": "#888888",
        "st_metric_label": "#555555",
        "st_metric_value": "#333333",
        "st_header_text": "#333333",
        "st_markdown_text": "#333333",

        # --- アラートボックス ---
        "alert_info_bg": "#e3f2fd",
        "alert_info_text": "#1565c0",
        "alert_info_border": "#90caf9",
        "alert_success_bg": "#e8f5e9",
        "alert_success_text": "#2e7d32",
        "alert_success_border": "#a5d6a7",
        "alert_warning_bg": "#fff8e1",
        "alert_warning_text": "#f57f17",
        "alert_warning_border": "#fff176",
        "alert_error_bg": "#ffebee",
        "alert_error_text": "#c62828",
        "alert_error_border": "#ef9a9a",
    },
    "dark": {
        # --- 全体背景 ---
        "sidebar_bg": "#1a1a2e",
        "main_bg": "#0f0f1a",
        "app_bg": "#0a0a14",

        # --- テキスト ---
        "text_primary": "#e0e0e0",
        "text_secondary": "#b0b0b0",
        "text_muted": "#909090",
        "timestamp_color": "#999999",
        "ai_metrics_color": "#aaaaaa",

        # --- セッションヘッダー ---
        "session_header_start": "#1b5e20",
        "session_header_end": "#2e7d32",
        "session_header_text": "#e0e0e0",

        # --- モデルバッジ ---
        "model_badge_bg": "#252540",
        "model_badge_text": "#c8c8d0",

        # --- ユーザーメッセージ ---
        "user_msg_bg_start": "#141e30",
        "user_msg_bg_end": "#1a2840",
        "user_msg_border": "#42a5f5",

        # --- AI メッセージ ---
        "ai_msg_bg_start": "#141a14",
        "ai_msg_bg_end": "#1a221a",
        "ai_msg_border": "#66bb6a",

        # --- コピーボタン ---
        "copy_btn_bg": "#333350",
        "copy_btn_text": "#c0c0c8",
        "copy_btn_hover_bg": "#44446a",
        "copy_btn_copied_bg": "#1b5e20",
        "copy_btn_copied_text": "#a5d6a7",

        # --- メトリクスボックス ---
        "metric_box_bg_start": "#1e1c14",
        "metric_box_bg_end": "#24221a",

        # --- サイドバー ---
        "sidebar_title_color": "#64b5f6",
        "popover_bg": "#252540",
        "popover_border": "#3a3a58",
        "popover_hover_bg": "#333350",

        # --- セッションボタン ---
        "btn_secondary_border": "#3a3a58",
        "active_session_bg": "#141e30",
        "active_session_hover": "#1e3050",
        "completed_session_bg": "#141e14",
        "completed_session_hover": "#1e3020",

        # --- 新規セッションボタン ---
        "new_session_btn_start": "#1565c0",
        "new_session_btn_end": "#1976d2",
        "new_session_btn_hover_start": "#1e1c14",
        "new_session_btn_hover_end": "#24221a",
        "new_session_btn_hover_text": "#e0d0b0",

        # --- ゴミ箱ボタン ---
        "trash_btn_bg": "#3a3a50",
        "trash_btn_hover_bg": "#2a2a40",
        "trash_btn_text": "#d0d0d8",

        # --- Expander ---
        "expander_header_bg": "#1e1e30",
        "expander_content_bg": "#1e1e30",

        # --- メインエリア popover ---
        "main_popover_bg_start": "#252540",
        "main_popover_bg_end": "#202035",
        "main_popover_hover_start": "#333350",
        "main_popover_hover_end": "#2e2e48",

        # --- コードブロック ---
        "code_bg": "#0a0a14",
        "code_text": "#d4d4d4",

        # --- メインプライマリボタン ---
        "main_primary_btn_start": "#1b5e20",
        "main_primary_btn_end": "#2e7d32",
        "main_primary_btn_text": "#a5d6a7",
        "main_primary_btn_hover_start": "#2e7d32",
        "main_primary_btn_hover_end": "#388e3c",
        "main_primary_btn_hover_text": "#c8e6c9",

        # --- オーバーレイ ---
        "overlay_bg": "rgba(0, 0, 0, 0.65)",
        "overlay_text": "#e0e0e0",
        "spinner_border": "#333350",
        "spinner_top": "#4caf50",

        # --- シャドウ ---
        "shadow_xs": "rgba(0, 0, 0, 0.25)",
        "shadow_sm": "rgba(0, 0, 0, 0.35)",
        "shadow_md": "rgba(0, 0, 0, 0.45)",
        "shadow_lg": "rgba(0, 0, 0, 0.55)",

        # --- ナビゲーションリンク ---
        "nav_bottom_bg": "#141e30",
        "nav_top_bg": "#141e14",
        "nav_text": "#c0c0c8",

        # --- Streamlit ネイティブ override ---
        "st_app_bg": "#0a0a14",
        "st_widget_bg": "#1e1e30",
        "st_widget_border": "#3a3a58",
        "st_input_bg": "#1e1e30",
        "st_input_text": "#e0e0e0",
        "st_label_text": "#c0c0c8",
        "st_caption_text": "#909090",
        "st_metric_label": "#b0b0b0",
        "st_metric_value": "#e0e0e0",
        "st_header_text": "#e0e0e0",
        "st_markdown_text": "#e0e0e0",

        # --- アラートボックス ---
        "alert_info_bg": "#0d1b2a",
        "alert_info_text": "#64b5f6",
        "alert_info_border": "#1565c0",
        "alert_success_bg": "#0d1a0d",
        "alert_success_text": "#66bb6a",
        "alert_success_border": "#2e7d32",
        "alert_warning_bg": "#1a1600",
        "alert_warning_text": "#ffca28",
        "alert_warning_border": "#f57f17",
        "alert_error_bg": "#1a0d0d",
        "alert_error_text": "#ef5350",
        "alert_error_border": "#c62828",
    },
}


def generate_theme_css(theme_name: str, font_zoom: float = 0.8) -> str:
    """テーマ名に応じた完全な CSS 文字列を生成する"""
    t = THEMES[theme_name]

    css = f"""
<style>
    /* ===== フォントサイズ（zoom）===== */
    .main .block-container {{
        zoom: {font_zoom};
    }}
    @media (max-width: 992px) {{
        .main .block-container {{
            zoom: {font_zoom * 0.95};
        }}
    }}
    @media (max-width: 768px) {{
        .main .block-container {{
            zoom: {font_zoom * 0.9};
        }}
    }}

    /* ===== 共通スタイル ===== */
    * {{
        transition: all 0.2s ease;
    }}

    /* ===== セッションヘッダー ===== */
    .session-header {{
        background: linear-gradient(135deg, {t['session_header_start']} 0%, {t['session_header_end']} 100%);
        color: {t['session_header_text']};
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px {t['shadow_md']};
    }}

    /* ===== モデルバッジ ===== */
    .model-badge {{
        background: {t['model_badge_bg']};
        color: {t['model_badge_text']};
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 0.95em;
        display: inline-block;
        margin: 5px 0;
    }}

    /* ===== ユーザーメッセージ ===== */
    .user-message {{
        background: linear-gradient(135deg, {t['user_msg_bg_start']} 0%, {t['user_msg_bg_end']} 100%);
        color: {t['text_primary']};
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid {t['user_msg_border']};
        box-shadow: 0 2px 8px {t['shadow_sm']};
    }}

    /* ===== AIメッセージ ===== */
    .ai-message {{
        background: linear-gradient(135deg, {t['ai_msg_bg_start']} 0%, {t['ai_msg_bg_end']} 100%);
        color: {t['text_primary']};
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid {t['ai_msg_border']};
        box-shadow: 0 2px 8px {t['shadow_sm']};
        position: relative;
    }}

    /* ===== コピーボタン ===== */
    .copy-btn {{
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: {t['copy_btn_bg']};
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.8em;
        color: {t['copy_btn_text']};
        display: flex;
        align-items: center;
        gap: 4px;
        transition: all 0.2s ease;
    }}
    .copy-btn:hover {{
        background: {t['copy_btn_hover_bg']};
    }}
    .copy-btn.copied {{
        background: {t['copy_btn_copied_bg']};
        color: {t['copy_btn_copied_text']};
    }}

    /* ===== メトリクスボックス ===== */
    .metric-box {{
        background: linear-gradient(135deg, {t['metric_box_bg_start']} 0%, {t['metric_box_bg_end']} 100%);
        color: {t['text_primary']};
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        box-shadow: 0 2px 6px {t['shadow_sm']};
    }}

    .stTextInput > div > div > input {{
        font-size: 16px;
    }}

    /* ===== サイドバー背景 ===== */
    [data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']} !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {t['sidebar_bg']} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        background-color: {t['sidebar_bg']} !important;
    }}

    /* ===== サイドバータイトル ===== */
    .sidebar-title {{
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        color: {t['sidebar_title_color']};
        padding: 5px 0 10px 0;
        margin-top: 0;
    }}

    /* ===== 新規セッションボタン（高さ2倍）===== */
    [data-testid="stSidebar"] button[kind="primary"] {{
        min-height: 60px !important;
    }}

    /* ===== メインコンテンツ背景 ===== */
    .main .block-container {{
        background-color: {t['main_bg']};
    }}

    /* ===== サイドバーのpopoverボタン ===== */
    [data-testid="stSidebar"] button[data-testid="stPopoverButton"] {{
        padding: 4px 8px !important;
        min-width: 32px !important;
        min-height: auto !important;
        height: auto !important;
        background-color: {t['popover_bg']} !important;
        border: 1px solid {t['popover_border']} !important;
        border-radius: 6px !important;
        align-self: stretch !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSidebar"] button[data-testid="stPopoverButton"]:hover {{
        background-color: {t['popover_hover_bg']} !important;
    }}
    .active-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"] {{
        background-color: {t['active_session_bg']} !important;
    }}
    .active-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"]:hover {{
        background-color: {t['active_session_hover']} !important;
    }}
    .completed-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"] {{
        background-color: {t['completed_session_bg']} !important;
    }}
    .completed-session-marker + div [data-testid="column"]:last-child button[data-testid="stPopoverButton"]:hover {{
        background-color: {t['completed_session_hover']} !important;
    }}

    /* ===== セッションボタンの基本スタイル ===== */
    [data-testid="stSidebar"] button[kind="secondary"] {{
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: pre-line !important;
        line-height: 1.3 !important;
        padding: 6px 10px !important;
        text-indent: 0 !important;
        min-height: auto !important;
        border: 1px solid {t['btn_secondary_border']} !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 4px {t['shadow_sm']};
        margin-bottom: 2px !important;
    }}
    [data-testid="stSidebar"] button[kind="secondary"] p {{
        text-align: left !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* ===== セッション行の間隔調整 ===== */
    [data-testid="stSidebar"] [data-testid="column"] {{
        padding: 0 2px !important;
    }}
    [data-testid="stSidebar"] .stHorizontalBlock {{
        gap: 4px !important;
        margin-bottom: 4px !important;
        align-items: stretch !important;
    }}

    /* ===== 新規セッションボタン ===== */
    [data-testid="stSidebar"] button[kind="primary"] {{
        background: linear-gradient(135deg, {t['new_session_btn_start']} 0%, {t['new_session_btn_end']} 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px {t['shadow_md']};
    }}
    [data-testid="stSidebar"] button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {t['new_session_btn_hover_start']} 0%, {t['new_session_btn_hover_end']} 100%) !important;
        color: {t['new_session_btn_hover_text']} !important;
    }}

    /* ===== アクティブセッション ===== */
    .active-session-marker + div button[kind="secondary"] {{
        background-color: {t['active_session_bg']} !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
    }}
    .active-session-marker + div button[kind="secondary"]:hover {{
        background-color: {t['active_session_hover']} !important;
    }}

    /* ===== 終了済みセッション ===== */
    .completed-session-marker + div button[kind="secondary"] {{
        background-color: {t['completed_session_bg']} !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 2 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: normal !important;
    }}
    .completed-session-marker + div button[kind="secondary"]:hover {{
        background-color: {t['completed_session_hover']} !important;
    }}

    /* ===== ゴミ箱ボタン ===== */
    .trash-button-marker + div button {{
        background-color: {t['trash_btn_bg']} !important;
        color: {t['trash_btn_text']} !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px {t['shadow_lg']};
    }}
    .trash-button-marker + div button:hover {{
        background-color: {t['trash_btn_hover_bg']} !important;
    }}
    .trash-button-marker + div button p {{
        color: {t['trash_btn_text']} !important;
    }}

    /* ===== Expander ===== */
    [data-testid="stSidebar"] .stExpander {{
        background-color: transparent !important;
        border: none !important;
    }}
    [data-testid="stSidebar"] details summary {{
        background-color: {t['expander_header_bg']} !important;
        color: {t['text_primary']} !important;
        border-radius: 8px;
        padding: 10px 12px !important;
        box-shadow: 0 1px 4px {t['shadow_sm']};
        margin-bottom: 4px;
    }}
    [data-testid="stSidebar"] details[open] > div {{
        background-color: {t['expander_content_bg']} !important;
        border-radius: 8px;
        padding: 8px !important;
        margin-top: 4px;
        box-shadow: 0 1px 4px {t['shadow_xs']};
    }}

    /* ===== メインエリアのpopover ===== */
    .main button[data-testid="stPopoverButton"] {{
        background: linear-gradient(135deg, {t['main_popover_bg_start']} 0%, {t['main_popover_bg_end']} 100%) !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px {t['shadow_sm']};
    }}
    .main button[data-testid="stPopoverButton"]:hover {{
        background: linear-gradient(135deg, {t['main_popover_hover_start']} 0%, {t['main_popover_hover_end']} 100%) !important;
    }}

    /* ===== メトリクス数値のフォントサイズ ===== */
    .main [data-testid="stMetricValue"] {{
        font-size: 1rem !important;
    }}

    /* ===== コード表示領域 ===== */
    .main pre,
    .main code,
    .main [data-testid="stMarkdown"] pre,
    .main [data-testid="stMarkdown"] code {{
        background-color: {t['code_bg']} !important;
        color: {t['code_text']} !important;
    }}
    .main pre {{
        padding: 12px 16px !important;
        border-radius: 8px !important;
        overflow-x: auto !important;
    }}
    .main code {{
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }}

    /* ===== メインエリアのプライマリボタン ===== */
    .main button[kind="primary"],
    .main [data-testid="stBaseButton-primary"],
    .main [data-testid="stFormSubmitButton"] button[kind="primary"],
    .main [data-testid="stFormSubmitButton"] button {{
        background: linear-gradient(135deg, {t['main_primary_btn_start']} 0%, {t['main_primary_btn_end']} 100%) !important;
        color: {t['main_primary_btn_text']} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .main button[kind="primary"]:hover,
    .main [data-testid="stBaseButton-primary"]:hover,
    .main [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
    .main [data-testid="stFormSubmitButton"] button:hover {{
        background: linear-gradient(135deg, {t['main_primary_btn_hover_start']} 0%, {t['main_primary_btn_hover_end']} 100%) !important;
        color: {t['main_primary_btn_hover_text']} !important;
    }}

    /* ===== LLM処理中オーバーレイ ===== */
    .loading-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: {t['overlay_bg']};
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: all;
    }}
    .loading-overlay .spinner-container {{
        text-align: center;
        color: {t['overlay_text']};
        font-size: 1.1rem;
    }}
    .loading-overlay .spinner-container .spinner {{
        width: 48px;
        height: 48px;
        border: 5px solid {t['spinner_border']};
        border-top: 5px solid {t['spinner_top']};
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 12px auto;
    }}
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* ===== Streamlit ネイティブ override ===== */
    .stApp {{
        background-color: {t['st_app_bg']} !important;
    }}
    .main {{
        background-color: {t['main_bg']} !important;
    }}
    /* テキスト色 */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {{
        color: {t['st_header_text']} !important;
    }}
    .main p, .main li, .main span, .main div {{
        color: {t['st_markdown_text']};
    }}
    .main [data-testid="stMarkdown"] p {{
        color: {t['st_markdown_text']} !important;
    }}
    /* キャプション */
    .main [data-testid="stCaptionContainer"] {{
        color: {t['st_caption_text']} !important;
    }}
    .main [data-testid="stCaptionContainer"] p {{
        color: {t['st_caption_text']} !important;
    }}
    /* メトリクス */
    .main [data-testid="stMetricLabel"] {{
        color: {t['st_metric_label']} !important;
    }}
    .main [data-testid="stMetricValue"] {{
        color: {t['st_metric_value']} !important;
    }}
    /* 入力フィールド */
    .main input, .main textarea {{
        background-color: {t['st_input_bg']} !important;
        color: {t['st_input_text']} !important;
        border-color: {t['st_widget_border']} !important;
    }}
    .main [data-testid="stTextInput"] label,
    .main [data-testid="stTextArea"] label,
    .main [data-testid="stSelectbox"] label {{
        color: {t['st_label_text']} !important;
    }}
    /* セレクトボックス */
    .main [data-testid="stSelectbox"] > div > div {{
        background-color: {t['st_input_bg']} !important;
        color: {t['st_input_text']} !important;
        border-color: {t['st_widget_border']} !important;
    }}
    /* サイドバーのテキスト色 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {{
        color: {t['text_primary']} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: {t['st_caption_text']} !important;
    }}
    /* フォーム背景 */
    .main [data-testid="stForm"] {{
        background-color: {t['st_widget_bg']} !important;
        border-color: {t['st_widget_border']} !important;
    }}
    /* Popover コンテンツ背景 */
    [data-testid="stPopover"] {{
        background-color: {t['st_widget_bg']} !important;
    }}
    div[data-popper-reference-hidden] {{
        background-color: {t['st_widget_bg']} !important;
    }}
    /* サイドバー内 popover コンテンツ */
    [data-testid="stSidebar"] [data-testid="stPopover"] {{
        background-color: {t['expander_header_bg']} !important;
    }}
    /* 水平線 */
    .main hr {{
        border-color: {t['st_widget_border']} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {t['popover_border']} !important;
    }}

    /* ===== アラートボックス（st.info / st.success / st.warning / st.error）===== */
    .main [data-testid="stAlert"] {{
        border-radius: 8px !important;
    }}
    .main div[data-testid="stAlert"][data-baseweb*="notification"] {{
        border-radius: 8px !important;
    }}
    /* st.info */
    .main .stAlert div[role="alert"]:has(svg[data-testid="stIconMaterial"]) {{
        background-color: {t['alert_info_bg']} !important;
        color: {t['alert_info_text']} !important;
        border-left-color: {t['alert_info_border']} !important;
    }}
    /* Streamlit の info/success/warning/error は data-baseweb 属性で識別 */
    .main div[data-baseweb="notification"][kind="info"] {{
        background-color: {t['alert_info_bg']} !important;
        color: {t['alert_info_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="info"] div {{
        color: {t['alert_info_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="positive"],
    .main div[data-baseweb="notification"][kind="success"] {{
        background-color: {t['alert_success_bg']} !important;
        color: {t['alert_success_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="positive"] div,
    .main div[data-baseweb="notification"][kind="success"] div {{
        color: {t['alert_success_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="warning"] {{
        background-color: {t['alert_warning_bg']} !important;
        color: {t['alert_warning_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="warning"] div {{
        color: {t['alert_warning_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="negative"],
    .main div[data-baseweb="notification"][kind="error"] {{
        background-color: {t['alert_error_bg']} !important;
        color: {t['alert_error_text']} !important;
    }}
    .main div[data-baseweb="notification"][kind="negative"] div,
    .main div[data-baseweb="notification"][kind="error"] div {{
        color: {t['alert_error_text']} !important;
    }}
    /* 汎用 stAlert セレクタ（Streamlit バージョン互換性対策）*/
    .main [data-testid="stInfo"] {{
        background-color: {t['alert_info_bg']} !important;
        color: {t['alert_info_text']} !important;
    }}
    .main [data-testid="stInfo"] p {{
        color: {t['alert_info_text']} !important;
    }}
    .main [data-testid="stSuccess"] {{
        background-color: {t['alert_success_bg']} !important;
        color: {t['alert_success_text']} !important;
    }}
    .main [data-testid="stSuccess"] p {{
        color: {t['alert_success_text']} !important;
    }}
    .main [data-testid="stWarning"] {{
        background-color: {t['alert_warning_bg']} !important;
        color: {t['alert_warning_text']} !important;
    }}
    .main [data-testid="stWarning"] p {{
        color: {t['alert_warning_text']} !important;
    }}
    .main [data-testid="stError"] {{
        background-color: {t['alert_error_bg']} !important;
        color: {t['alert_error_text']} !important;
    }}
    .main [data-testid="stError"] p {{
        color: {t['alert_error_text']} !important;
    }}
    /* サイドバー内アラートも対応 */
    [data-testid="stSidebar"] [data-testid="stInfo"] {{
        background-color: {t['alert_info_bg']} !important;
        color: {t['alert_info_text']} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stInfo"] p {{
        color: {t['alert_info_text']} !important;
    }}
</style>
"""
    return css
