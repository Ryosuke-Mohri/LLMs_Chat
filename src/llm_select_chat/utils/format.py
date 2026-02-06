"""
タイムスタンプ・リージョン表示など、表示用ユーティリティ。
Streamlit に依存しない。
"""
from datetime import datetime

# リージョン表示の統一（旧表記・保存データ用）
REGION_DISPLAY_MAP = {
    "JP (Japan East)": "Japan East",
    "US (East US 2)": "East US2",
}


def format_timestamp(ts_str: str) -> str:
    """ISO形式タイムスタンプを表示用にフォーマット。"""
    if not ts_str:
        return ""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(ts_str)


def format_region_display(region: str | None, region_display_map: dict | None = None) -> str:
    """アプリ内表示用にリージョン表記を統一。None/空のときは '不明'。"""
    if not region:
        return "不明"
    m = region_display_map if region_display_map is not None else REGION_DISPLAY_MAP
    return m.get(region, region)
