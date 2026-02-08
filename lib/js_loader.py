"""
JavaScript アセット読み込み
assets/js/*.js を読み込み、<script> でラップして返す。
"""

from pathlib import Path


def _assets_dir() -> Path:
    """プロジェクトルートの assets ディレクトリ"""
    return Path(__file__).resolve().parent.parent / "assets"


def _read_js(name: str) -> str:
    """JS ファイルの中身を読み込む"""
    path = _assets_dir() / "js" / f"{name}.js"
    return path.read_text(encoding="utf-8").strip()


def get_popover_close_html() -> str:
    """Popover 強制クローズ用の HTML（<script> ラップ済み）。components.html に渡す用。"""
    content = _read_js("popover_close")
    return f"<script>\n{content}\n</script>"


def get_danger_btn_js() -> str:
    """危険ボタン data-danger 付与用の HTML（<script> ラップ済み）。components.html に渡す用。"""
    content = _read_js("danger_btn")
    return f"<script>\n{content}\n</script>"
