"""
CSS アセット読み込み・テーマ置換
assets/css/app.css を読み込み、THEMES と font_zoom でプレースホルダを置換して返す。
"""

from pathlib import Path

from lib.themes import THEMES


def _assets_dir() -> Path:
    """プロジェクトルートの assets ディレクトリ"""
    return Path(__file__).resolve().parent.parent / "assets"


def get_app_css(theme_name: str, font_zoom: float = 0.8) -> str:
    """
    テーマ名と font_zoom に応じた完全な CSS 文字列を返す。
    assets/css/app.css を読み込み、{{key}} を THEMES と font_zoom で置換し、
    <style>...</style> でラップして返す。
    """
    t = THEMES[theme_name]
    css_path = _assets_dir() / "css" / "app.css"
    raw = css_path.read_text(encoding="utf-8")

    replacements = {}
    for key, value in t.items():
        replacements[f"{{{{{key}}}}}"] = str(value)
    replacements["{{font_zoom}}"] = str(font_zoom)
    replacements["{{font_zoom_95}}"] = str(font_zoom * 0.95)
    replacements["{{font_zoom_90}}"] = str(font_zoom * 0.9)

    for placeholder, value in replacements.items():
        raw = raw.replace(placeholder, value)

    return f"<style>\n{raw}\n</style>"
