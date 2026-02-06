"""
設定の集約: .env を読み込み、プロジェクトルート基準のパスとリージョン設定を提供する。
"""
import os
from pathlib import Path

# プロジェクトルート（このファイルが src/llm_select_chat/config.py にある前提）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_env():
    """.env を読み込む（python-dotenv があれば使用、なければ os.environ のみ）。"""
    try:
        from dotenv import load_dotenv
        env_path = _PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass


def get_project_root() -> Path:
    """プロジェクトルートの Path を返す。"""
    return _PROJECT_ROOT


def get_config_dir() -> Path:
    """CONFIG_DIR（設定CSV等）の絶対パス。"""
    _load_env()
    raw = os.environ.get("CONFIG_DIR", "config")
    if Path(raw).is_absolute():
        return Path(raw)
    return _PROJECT_ROOT / raw


def get_data_dir() -> Path:
    """DATA_DIR の絶対パス。"""
    _load_env()
    raw = os.environ.get("DATA_DIR", "data")
    if Path(raw).is_absolute():
        return Path(raw)
    return _PROJECT_ROOT / raw


def get_log_file_path() -> Path:
    """ログJSONの絶対パス。"""
    _load_env()
    raw = os.environ.get("LOG_FILE_PATH", "data/llm_select_chat_log.json")
    if Path(raw).is_absolute():
        return Path(raw)
    return _PROJECT_ROOT / raw


def get_usd_to_jpy() -> float:
    """USD -> JPY の為替レート。"""
    _load_env()
    try:
        return float(os.environ.get("USD_TO_JPY", "150"))
    except ValueError:
        return 150.0


def get_azure_api_version() -> str:
    """Azure OpenAI API バージョン（共通）。"""
    _load_env()
    return os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")


# リージョン定義キー（PoC の REGIONS に対応）
REGION_KEYS = ("Japan East", "East US2")

# リージョン表示の統一（旧表記・保存データ用）
REGION_DISPLAY_MAP = {
    "JP (Japan East)": "Japan East",
    "US (East US 2)": "East US2",
}


def _get_region_env_key(region_name: str, suffix: str) -> str:
    """リージョン名から環境変数キーを生成。"""
    key = region_name.replace(" ", "_").upper()
    return f"AZURE_OPENAI_{key}_{suffix}"


def get_region_config(region_name: str) -> dict:
    """
    リージョン名に対応する設定を返す。
    戻り値: api_key, endpoint, anthropic_endpoint, api_version, deployment_file (Path)
    """
    _load_env()
    root = get_project_root()
    config_dir = get_config_dir()
    api_version = get_azure_api_version()

    # デプロイ一覧CSVのファイル名を環境変数から取得
    if region_name == "Japan East":
        deployment_file = os.environ.get("CONFIG_DEPLOYMENT_JAPAN_EAST", "deployment_name_JPEast.csv")
    elif region_name == "East US2":
        deployment_file = os.environ.get("CONFIG_DEPLOYMENT_EAST_US2", "deployment_name_EastUS2.csv")
    else:
        deployment_file = ""

    deployment_path = config_dir / deployment_file if deployment_file else config_dir

    base = f"AZURE_OPENAI_{region_name.replace(' ', '_').upper()}"
    api_key = os.environ.get(f"{base}_API_KEY", "")
    endpoint = os.environ.get(f"{base}_ENDPOINT", "")
    anthropic_endpoint = os.environ.get(f"{base}_ANTHROPIC_ENDPOINT", "")

    return {
        "api_key": api_key,
        "endpoint": endpoint,
        "anthropic_endpoint": anthropic_endpoint or endpoint,
        "api_version": api_version,
        "deployment_file": config_dir / deployment_file if deployment_file else None,
    }


def get_regions_for_app() -> dict:
    """
    アプリが期待する REGIONS 形式を返す。
    各リージョンに deployment_file (Path) と、config 相当の dict（api_key, endpoint 等）を含める。
    """
    _load_env()
    config_dir = get_config_dir()
    api_version = get_azure_api_version()
    result = {}

    for region_name in REGION_KEYS:
        base = f"AZURE_OPENAI_{region_name.replace(' ', '_').upper()}"
        api_key = os.environ.get(f"{base}_API_KEY", "")
        endpoint = os.environ.get(f"{base}_ENDPOINT", "")
        anthropic_endpoint = os.environ.get(f"{base}_ANTHROPIC_ENDPOINT", "")

        if region_name == "Japan East":
            deployment_file = os.environ.get("CONFIG_DEPLOYMENT_JAPAN_EAST", "deployment_name_JPEast.csv")
        else:
            deployment_file = os.environ.get("CONFIG_DEPLOYMENT_EAST_US2", "deployment_name_EastUS2.csv")

        deployment_path = config_dir / deployment_file
        # config 相当の辞書（get_all_models 等で使う）
        config_dict = {
            "Azure API Key": api_key,
            "ENDPOINT": endpoint,
            "ENDPOINT (Anthropic Model)": anthropic_endpoint or endpoint,
            "Azure API Version": api_version,
        }
        result[region_name] = {
            "deployment_file": deployment_path,
            "config": config_dict,
        }
    return result


def get_constructor_master_path() -> Path:
    """コンストラクターマスタCSVの絶対パス。"""
    _load_env()
    config_dir = get_config_dir()
    raw = os.environ.get("CONFIG_CONSTRUCTOR_MASTER", "deployment_constructor_master.csv")
    if Path(raw).is_absolute():
        return Path(raw)
    return config_dir / raw
