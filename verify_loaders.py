#!/usr/bin/env python3
"""
分離後セットで確認: 全 loader（css / js / html）がアセットを正常に読み込めることを検証する。
プロジェクトルートで実行すること: python verify_loaders.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

def main():
    errors = []
    # CSS
    from lib.css_loader import get_app_css
    try:
        s = get_app_css("light", 0.8)
        assert "<style>" in s and "{{" not in s
    except Exception as e:
        errors.append(("get_app_css", e))
    # JS
    from lib.js_loader import get_danger_btn_js, get_popover_close_html
    try:
        s = get_danger_btn_js()
        assert "<script>" in s
    except Exception as e:
        errors.append(("get_danger_btn_js", e))
    try:
        s = get_popover_close_html()
        assert "<script>" in s
    except Exception as e:
        errors.append(("get_popover_close_html", e))
    # HTML（プレースホルダありはサンプル値で呼ぶ）
    from lib.html_loader import (
        get_loading_overlay_html,
        get_sidebar_title_html,
        get_marker_div_html,
        get_page_anchor_html,
        get_model_badge_html,
        get_user_message_html,
        get_ai_message_html,
        get_nav_bottom_html,
        get_nav_top_html,
        get_copy_button_block_html,
    )
    from lib.themes import THEMES
    t = THEMES["light"]
    try:
        get_loading_overlay_html()
        get_sidebar_title_html()
        get_marker_div_html("danger-btn-marker")
        get_page_anchor_html("page-top")
        get_model_badge_html(provider_icon="", model_display_name="", region_display="", provider="")
        get_user_message_html(timestamp_str="", content="")
        get_ai_message_html(ai_metrics_color="", metrics_str="", content="")
        get_nav_bottom_html(nav_bottom_bg="", nav_text="")
        get_nav_top_html(nav_top_bg="", nav_text="")
        get_copy_button_block_html(
            msg_id="x", copy_btn_bg="", copy_btn_text="",
            copy_btn_copied_bg="", copy_btn_copied_text="", escaped_content="",
        )
    except Exception as e:
        errors.append(("html loaders", e))
    if errors:
        for name, err in errors:
            print(f"FAIL {name}: {err}")
        sys.exit(1)
    print("OK: all loaders verified.")

if __name__ == "__main__":
    main()
