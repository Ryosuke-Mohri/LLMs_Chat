"""
モデルタイプ・コンストラクター表示用ユーティリティ。
Streamlit に依存しない。
"""

# コンストラクター別アイコン
CONSTRUCTOR_ICONS = {
    "OpenAI": "🟢",
    "Anthropic": "🟣",
    "DeepSeek": "🟠",
    "Moonshot": "🟠",
    "xAI": "🔵",
    "Meta": "🔵",
}


def get_constructor_icon(constructor: str | None) -> str:
    """コンストラクター名から表示用アイコンを返す。"""
    if not constructor:
        return "🔵"
    return CONSTRUCTOR_ICONS.get(constructor, "🔵")


def is_anthropic_model(deployment_name: str) -> bool:
    """Anthropic (Claude) モデルかどうかを判定。"""
    if not deployment_name:
        return False
    return deployment_name.lower().startswith("claude")


def get_model_type(deployment_name: str) -> str:
    """モデルタイプを取得（'anthropic' or 'openai'）。"""
    return "anthropic" if is_anthropic_model(deployment_name) else "openai"


def get_model_type_display(model_type: str) -> dict:
    """モデルタイプの表示用情報を取得。"""
    if model_type == "anthropic":
        return {"icon": "🟣", "name": "Anthropic (Claude)"}
    return {"icon": "🟢", "name": "OpenAI (GPT)"}
