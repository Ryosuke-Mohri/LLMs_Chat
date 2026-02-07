"""
lib/logger.py - アプリケーション・デバッグログ設定モジュール

会話ログ (data/chat_log.json) とは別に、開発・運用向けの詳細ログを
logs/ ディレクトリへ出力する。

特徴:
- QueueHandler + QueueListener でファイル I/O をバックグラウンドスレッドに委譲
  → Streamlit の UI スレッドをブロックしない
- RotatingFileHandler でファイルサイズを制限 (デフォルト 10 MB × 5 世代)
- 環境変数 LOG_LEVEL でログレベルを制御 (デフォルト: DEBUG)

使い方:
    from lib.logger import get_logger
    logger = get_logger(__name__)
    logger.info("起動しました")
"""

import atexit
import logging
import logging.handlers
import os
import queue
from pathlib import Path

# ========================================
# 定数
# ========================================
_BASE_DIR = Path(__file__).resolve().parent.parent
_LOG_DIR = _BASE_DIR / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FILE = _LOG_DIR / "app.log"
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 5

_LOG_FORMAT = (
    "[%(asctime)s] [%(levelname)-8s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ========================================
# ログキュー・リスナー（プロセス内で 1 つだけ）
# ========================================
_log_queue: queue.Queue = queue.Queue(-1)  # 上限なし
_listener: logging.handlers.QueueListener | None = None


def _ensure_listener() -> None:
    """QueueListener がまだ起動していなければ初期化・起動する。"""
    global _listener
    if _listener is not None:
        return

    # --- ファイルハンドラ (RotatingFileHandler) ---
    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(_LOG_FILE),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # ファイルには常に全レベル記録

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    file_handler.setFormatter(formatter)

    # --- QueueListener (バックグラウンドスレッドで書き込み) ---
    _listener = logging.handlers.QueueListener(
        _log_queue,
        file_handler,
        respect_handler_level=True,
    )
    _listener.start()
    atexit.register(_shutdown_listener)


def _shutdown_listener() -> None:
    """アプリ終了時にリスナーを安全に停止する。"""
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None


# ========================================
# 公開 API
# ========================================
def get_logger(name: str = "app") -> logging.Logger:
    """名前付きロガーを取得する。

    内部で QueueHandler を経由し、実際のファイル書き込みは
    バックグラウンドスレッド (QueueListener) が行う。

    Args:
        name: ロガー名。通常は ``__name__`` を渡す。

    Returns:
        設定済み logging.Logger インスタンス。
    """
    _ensure_listener()

    logger = logging.getLogger(name)

    # ハンドラが未設定の場合のみ追加（Streamlit の再実行で重複しないようにする）
    if not logger.handlers:
        queue_handler = logging.handlers.QueueHandler(_log_queue)
        logger.addHandler(queue_handler)

    # 環境変数でレベルを制御
    level_name = os.getenv("LOG_LEVEL", "DEBUG").upper()
    level = getattr(logging, level_name, logging.DEBUG)
    logger.setLevel(level)

    return logger
