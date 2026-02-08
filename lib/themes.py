"""
テーマ定義モジュール
ライト/ダーク配色の辞書（THEMES）。
CSS/JS は assets/ と lib/css_loader / lib/js_loader で管理。
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
        "popover_hover_bg": "#d0d0d0",

        # --- セッションボタン ---
        "btn_secondary_border": "#d0d0d0",
        "btn_secondary_bg": "#ffffff",
        "active_session_bg": "#e3f2fd",
        "active_session_hover": "#90caf9",
        "completed_session_bg": "#e8f5e9",
        "completed_session_hover": "#a5d6a7",

        # --- 新規セッションボタン ---
        "new_session_btn_start": "#1565c0",
        "new_session_btn_end": "#1976d2",
        "new_session_btn_hover_start": "#fff8e1",
        "new_session_btn_hover_end": "#fffde7",
        "new_session_btn_hover_text": "#5d4037",

        # --- ゴミ箱ボタン ---
        "trash_btn_bg": "#616161",
        "trash_btn_hover_bg": "#333333",
        "trash_btn_text": "#ffffff",

        # --- 危険ボタン（削除系）---
        "danger_btn_start": "#ef5350",
        "danger_btn_end": "#e53935",
        "danger_btn_text": "#ffffff",
        "danger_btn_hover_start": "#c62828",
        "danger_btn_hover_end": "#b71c1c",
        "danger_btn_hover_text": "#ffffff",

        # --- Expander ---
        "expander_header_bg": "#ffffff",
        "expander_content_bg": "#ffffff",

        # --- メインエリア popover ---
        "main_popover_bg_start": "#f5f5f5",
        "main_popover_bg_end": "#eeeeee",
        "main_popover_hover_start": "#d0d0d0",
        "main_popover_hover_end": "#c0c0c0",

        # --- コードブロック ---
        "code_bg": "#1e1e1e",
        "code_text": "#d4d4d4",

        # --- メインプライマリボタン ---
        "main_primary_btn_start": "#c8e6c9",
        "main_primary_btn_end": "#a5d6a7",
        "main_primary_btn_text": "#2e7d32",
        "main_primary_btn_hover_start": "#81c784",
        "main_primary_btn_hover_end": "#66bb6a",
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
        "text_primary": "#f8f8f8",
        "text_secondary": "#e0e0e0",
        "text_muted": "#c0c0c0",
        "timestamp_color": "#d0d0d0",
        "ai_metrics_color": "#d8d8d8",

        # --- セッションヘッダー ---
        "session_header_start": "#1b5e20",
        "session_header_end": "#2e7d32",
        "session_header_text": "#ffffff",

        # --- モデルバッジ ---
        "model_badge_bg": "#252540",
        "model_badge_text": "#f0f0f8",

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
        "copy_btn_text": "#e0e0e8",
        "copy_btn_hover_bg": "#555580",
        "copy_btn_copied_bg": "#1b5e20",
        "copy_btn_copied_text": "#a5d6a7",

        # --- メトリクスボックス ---
        "metric_box_bg_start": "#1e1c14",
        "metric_box_bg_end": "#24221a",

        # --- サイドバー ---
        "sidebar_title_color": "#64b5f6",
        "popover_bg": "#252540",
        "popover_border": "#3a3a58",
        "popover_hover_bg": "#40406a",

        # --- セッションボタン ---
        "btn_secondary_border": "#3a3a58",
        "btn_secondary_bg": "#1e1e30",
        "active_session_bg": "#141e30",
        "active_session_hover": "#253d6a",
        "completed_session_bg": "#141e14",
        "completed_session_hover": "#254035",

        # --- 新規セッションボタン ---
        "new_session_btn_start": "#1565c0",
        "new_session_btn_end": "#1976d2",
        "new_session_btn_hover_start": "#1e88e5",
        "new_session_btn_hover_end": "#42a5f5",
        "new_session_btn_hover_text": "#ffffff",

        # --- ゴミ箱ボタン ---
        "trash_btn_bg": "#3a3a50",
        "trash_btn_hover_bg": "#555578",
        "trash_btn_text": "#e8e8f0",

        # --- 危険ボタン（削除系）---
        "danger_btn_start": "#7f1d1d",
        "danger_btn_end": "#991b1b",
        "danger_btn_text": "#fca5a5",
        "danger_btn_hover_start": "#c62828",
        "danger_btn_hover_end": "#ef5350",
        "danger_btn_hover_text": "#ffffff",

        # --- Expander ---
        "expander_header_bg": "#1e1e30",
        "expander_content_bg": "#1e1e30",

        # --- メインエリア popover ---
        "main_popover_bg_start": "#1a1a30",
        "main_popover_bg_end": "#151528",
        "main_popover_hover_start": "#38385a",
        "main_popover_hover_end": "#30304e",

        # --- コードブロック ---
        "code_bg": "#1e1e2e",
        "code_text": "#d4d4d4",

        # --- メインプライマリボタン ---
        "main_primary_btn_start": "#1b5e20",
        "main_primary_btn_end": "#2e7d32",
        "main_primary_btn_text": "#a5d6a7",
        "main_primary_btn_hover_start": "#43a047",
        "main_primary_btn_hover_end": "#66bb6a",
        "main_primary_btn_hover_text": "#ffffff",

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
        "nav_text": "#f0f0f0",

        # --- Streamlit ネイティブ override ---
        "st_app_bg": "#0a0a14",
        "st_widget_bg": "#1e1e30",
        "st_widget_border": "#3a3a58",
        "st_input_bg": "#1e1e30",
        "st_input_text": "#f8f8f8",
        "st_label_text": "#e8e8f0",
        "st_caption_text": "#c0c0c8",
        "st_metric_label": "#e0e0e8",
        "st_metric_value": "#ffffff",
        "st_header_text": "#ffffff",
        "st_markdown_text": "#f8f8f8",

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

