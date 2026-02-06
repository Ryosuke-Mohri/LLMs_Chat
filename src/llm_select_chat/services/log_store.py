"""
ログ永続化（llm_select_chat_log.json の読込・保存）。
パスは config から取得。Streamlit に依存しない。
"""
import json
from pathlib import Path

from src.llm_select_chat import config as _config


def get_log_file_path() -> Path:
    """ログファイルの絶対パス（config 経由）。"""
    return _config.get_log_file_path()


def load_log_data() -> dict:
    """ログデータを読み込む。存在しなければ {"sessions": {}}。"""
    path = get_log_file_path()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sessions": {}}


def save_log_data(data: dict) -> None:
    """ログデータを保存する。親ディレクトリが無ければ作成。"""
    path = get_log_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
