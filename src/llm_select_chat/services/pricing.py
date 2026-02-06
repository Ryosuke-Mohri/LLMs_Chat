"""
料金計算（USD/JPY、トークン単価）。
Streamlit に依存しない。
"""
from src.llm_select_chat import config as _config

# モデル別料金テーブル（USD / 1000トークン）
PRICING_TABLE = {
    "openai": {
        "default": {"prompt_per_1k": 0.01, "completion_per_1k": 0.03},
        "gpt-4": {"prompt_per_1k": 0.03, "completion_per_1k": 0.06},
        "gpt-4.1": {"prompt_per_1k": 0.002, "completion_per_1k": 0.008},
        "gpt-5": {"prompt_per_1k": 0.005, "completion_per_1k": 0.015},
    },
    "anthropic": {
        "default": {"prompt_per_1k": 0.003, "completion_per_1k": 0.015},
        "claude-haiku": {"prompt_per_1k": 0.001, "completion_per_1k": 0.005},
        "claude-sonnet": {"prompt_per_1k": 0.003, "completion_per_1k": 0.015},
        "claude-opus": {"prompt_per_1k": 0.015, "completion_per_1k": 0.075},
    },
}

PRICING_DEFAULT = {"prompt_per_1k": 0.01, "completion_per_1k": 0.03}


def get_usd_to_jpy() -> float:
    """為替レートを取得（config 経由）。"""
    return _config.get_usd_to_jpy()


def get_pricing_for_model(deployment_name: str, model_type: str) -> dict:
    """モデルに応じた料金設定を取得。"""
    pricing_category = PRICING_TABLE.get(model_type, PRICING_TABLE["openai"])
    dep_lower = (deployment_name or "").lower()
    for key in pricing_category:
        if key != "default" and key in dep_lower:
            return pricing_category[key]
    return pricing_category["default"]


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    pricing: dict | None = None,
    usd_to_jpy: float | None = None,
) -> dict:
    """トークン数からコストを計算。戻り値は prompt_cost_usd, completion_cost_usd, total_cost_usd, total_cost_jpy。"""
    if pricing is None:
        pricing = PRICING_DEFAULT
    if usd_to_jpy is None:
        usd_to_jpy = get_usd_to_jpy()
    prompt_cost = (prompt_tokens / 1000) * pricing["prompt_per_1k"]
    completion_cost = (completion_tokens / 1000) * pricing["completion_per_1k"]
    total_cost = prompt_cost + completion_cost
    return {
        "prompt_cost_usd": round(prompt_cost, 6),
        "completion_cost_usd": round(completion_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "total_cost_jpy": round(total_cost * usd_to_jpy, 2),
    }
