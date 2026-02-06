"""
モデルカタログ生成（デプロイ一覧・コンストラクターマスタ読込、get_all_models）。
Streamlit に依存しない。
"""
import csv
from pathlib import Path

from src.llm_select_chat import config as _config
from src.llm_select_chat.utils import model_type as _model_type

_constructor_master_cache: dict | None = None


def load_constructor_master() -> dict:
    """コンストラクターマスタCSVを読み込み、deployment_name -> constructor の辞書を返す。"""
    global _constructor_master_cache
    if _constructor_master_cache is not None:
        return _constructor_master_cache
    result = {}
    path = _config.get_constructor_master_path()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                result[row["deployment_name"]] = row["constructor"]
    _constructor_master_cache = result
    return result


def get_constructor_for_deployment(deployment_name: str, constructor_master: dict | None = None) -> str:
    """デプロイ名からコンストラクター名を取得。マスタに無い場合は 'その他'。"""
    if not deployment_name:
        return "その他"
    if constructor_master is None:
        constructor_master = load_constructor_master()
    return constructor_master.get(deployment_name, "その他")


def load_deployments(csv_path: Path) -> list[str]:
    """CSVからデプロイメント名一覧を読み込む。"""
    deployments = []
    path = Path(csv_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                deployments.append(row["deployment_name"])
    return deployments


def get_api_key_for_region(region: str | None, regions: dict | None = None) -> str:
    """リージョンから API Key を取得（旧表記のリージョン名にも対応）。"""
    if not region:
        return ""
    region_display_map = _config.REGION_DISPLAY_MAP
    region_key = region_display_map.get(region, region)
    if regions is None:
        regions = _config.get_regions_for_app()
    region_info = regions.get(region_key)
    if region_info:
        return region_info.get("config", {}).get("Azure API Key", "")
    return ""


def get_anthropic_endpoint_for_region(region: str | None) -> str:
    """
    リージョンに対応する Anthropic 用エンドポイントを .env から取得する。
    例: East US2 → AZURE_OPENAI_EAST_US2_ANTHROPIC_ENDPOINT
    未設定の場合は Azure OpenAI 用 ENDPOINT をフォールバック。セッションにキャッシュされた
    endpoint ではなく常にここで取得することで、.env の ENDPOINT (Anthropic 系) を確実に使う。
    """
    if not region:
        return ""
    region_display_map = _config.REGION_DISPLAY_MAP
    region_key = region_display_map.get(region, region)
    cfg = _config.get_region_config(region_key)
    return (cfg.get("anthropic_endpoint") or cfg.get("endpoint") or "").strip()


def get_all_models(regions: dict | None = None) -> list[dict]:
    """
    全モデル情報を取得。
    regions を省略した場合は config.get_regions_for_app() を使用。
    戻り値の各要素は region, deployment_name, model_type, constructor, constructor_icon,
    endpoint, config, display_name を持つ。
    """
    if regions is None:
        regions = _config.get_regions_for_app()
    constructor_master = load_constructor_master()
    all_models = []
    for region_name, region_info in regions.items():
        try:
            config = region_info.get("config", {})
            deployment_file = region_info.get("deployment_file")
            if not deployment_file:
                continue
            deployments = load_deployments(deployment_file)
            for dep in deployments:
                model_type = _model_type.get_model_type(dep)
                constructor = get_constructor_for_deployment(dep, constructor_master)
                constructor_icon = _model_type.get_constructor_icon(constructor)
                type_display = _model_type.get_model_type_display(model_type)
                endpoint = (
                    config.get("ENDPOINT (Anthropic Model)", config.get("ENDPOINT", ""))
                    if model_type == "anthropic"
                    else config.get("ENDPOINT", "")
                )
                all_models.append({
                    "region": region_name,
                    "deployment_name": dep,
                    "model_type": model_type,
                    "constructor": constructor,
                    "constructor_icon": constructor_icon,
                    "endpoint": endpoint,
                    "config": config,
                    "display_name": f"{constructor_icon} {dep} ({region_name}) {constructor}",
                })
        except Exception:
            pass
    return all_models
