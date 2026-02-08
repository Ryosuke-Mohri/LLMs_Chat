"""
LLM Select Chat App - Streamlit Frontend
Azure OpenAI / Anthropic モデル選択チャットアプリ

起動コマンド:
    streamlit run streamlit_app.py

機能:
- フロントエンドからプロンプト入力・送信
- セッションごとにメトリクス表示（モデルデプロイ名・リージョン含む）
- 左ペインからセッション選択、過去の会話から再開
- セッション途中ではモデル変更不可
- セッション名の変更可能
- すべての変更をJSONログに記録

対応モデル:
- Azure OpenAI (GPT系): openai SDK
- Anthropic (Claude系): anthropic SDK
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
import time
import uuid
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
import anthropic

load_dotenv()

from lib.logger import get_logger
from lib.themes import THEMES
from lib.css_loader import get_app_css
from lib.js_loader import get_danger_btn_js, get_popover_close_html
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
logger = get_logger(__name__)

# ========================================
# ページ設定
# ========================================
st.set_page_config(
    page_title="LLM Select Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# テーマ初期化
# ========================================
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "light"

# ========================================
# カスタムCSS（テーマ対応）
# ========================================
FONT_ZOOM = 0.8
_current_theme = THEMES[st.session_state.app_theme]
st.markdown(get_app_css(st.session_state.app_theme, FONT_ZOOM), unsafe_allow_html=True)

# 危険ボタン（削除系）の data-danger 属性付与 JS
components.html(get_danger_btn_js(), height=0)

# (CSS は assets/css/app.css + lib/css_loader.get_app_css)

# LLM処理中オーバーレイ表示
if st.session_state.get("is_processing", False):
    st.markdown(get_loading_overlay_html(), unsafe_allow_html=True)

# Popover 強制クローズ（フラグが立っている場合、JS で閉じる）
if st.session_state.get("_close_popover", False):
    st.session_state._close_popover = False
    components.html(get_popover_close_html(), height=0)

# ========================================
# 定数・パス設定
# ========================================
BASE_DIR = Path(__file__).parent
LOG_FILE_PATH = BASE_DIR / os.getenv("LOG_FILE_PATH", "data/chat_log.json")
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

REGIONS = {
    "Japan East": {
        "api_key": os.getenv("AZURE_OPENAI_JAPAN_EAST_API_KEY", ""),
        "endpoint": os.getenv("AZURE_OPENAI_JAPAN_EAST_ENDPOINT", ""),
        "anthropic_endpoint": "",
    },
    "East US2": {
        "api_key": os.getenv("AZURE_OPENAI_EAST_US2_API_KEY", ""),
        "endpoint": os.getenv("AZURE_OPENAI_EAST_US2_ENDPOINT", ""),
        "anthropic_endpoint": os.getenv("AZURE_OPENAI_EAST_US2_ANTHROPIC_ENDPOINT", ""),
    }
}

# リージョン表示の統一（旧表記・保存データを表示用に変換）
REGION_DISPLAY_MAP = {
    "JP (Japan East)": "Japan East",
    "US (East US 2)": "East US2",
}

# --- 起動ログ ---
logger.info("=== アプリケーション起動 ===")
logger.info("LOG_FILE_PATH=%s", LOG_FILE_PATH)
logger.info("API_VERSION=%s", API_VERSION)
for _rname, _rinfo in REGIONS.items():
    logger.info(
        "REGION[%s]: endpoint=%s",
        _rname, _rinfo.get("endpoint", ""),
    )
logger.debug("REGION_DISPLAY_MAP=%s", REGION_DISPLAY_MAP)

def format_region_display(region):
    """アプリ内表示用にリージョン表記を統一する。None/空のときは '不明'。"""
    if not region:
        return "不明"
    return REGION_DISPLAY_MAP.get(region, region)

# ========================================
# モデルメタデータ（config/deployment_models.json）
# ========================================
MODEL_METADATA_PATH = BASE_DIR / "config" / "deployment_models.json"
_model_metadata_cache = None

def load_model_metadata():
    """config/deployment_models.json からモデルメタデータのリストを返す"""
    global _model_metadata_cache
    if _model_metadata_cache is not None:
        return _model_metadata_cache
    try:
        with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _model_metadata_cache = data
        logger.debug("load_model_metadata: %d 件ロード", len(data))
        return data
    except Exception:
        logger.exception("load_model_metadata: ファイル読み込み失敗 (%s)", MODEL_METADATA_PATH)
        _model_metadata_cache = []
        return []

def get_provider_for_deployment(deployment_name):
    """デプロイ名からプロバイダー名を取得。マスタに無い場合は 'その他'。"""
    if not deployment_name:
        return "その他"
    metadata = load_model_metadata()
    for m in metadata:
        if m.get("deployment_name") == deployment_name:
            return m.get("provider", "その他")
    return "その他"

def get_display_name_for_deployment(deployment_name):
    """デプロイ名から表示名を取得。マスタに無い場合はデプロイ名をそのまま返す。"""
    if not deployment_name:
        return "不明"
    metadata = load_model_metadata()
    for m in metadata:
        if m.get("deployment_name") == deployment_name:
            return m.get("display_name", deployment_name)
    return deployment_name

# プロバイダー別アイコン（OpenAI / Anthropic / 中国系 / その他 で区別）
PROVIDER_ICONS = {
    "OpenAI": "🟢",
    "Anthropic": "🟣",
    "DeepSeek": "🟠",
    "Moonshot": "🟠",
    "xAI": "🔵",
    "Meta": "🔵",
}

def get_provider_icon(provider):
    """プロバイダー名から表示用アイコンを返す。"""
    if not provider:
        return "🔵"
    return PROVIDER_ICONS.get(provider, "🔵")

# ========================================
# 料金設定（USD / 1000トークン）
# ========================================
# モデル別料金テーブル
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
    }
}

# デフォルト料金（後方互換性用）
PRICING = {
    "prompt_per_1k": 0.01,
    "completion_per_1k": 0.03,
}
USD_TO_JPY = 150

def get_pricing_for_model(deployment_name, model_type):
    """モデルに応じた料金設定を取得"""
    pricing_category = PRICING_TABLE.get(model_type, PRICING_TABLE["openai"])
    
    # モデル名から料金カテゴリを特定
    dep_lower = deployment_name.lower()
    for key in pricing_category:
        if key != "default" and key in dep_lower:
            return pricing_category[key]
    
    return pricing_category["default"]

# ========================================
# ユーティリティ関数
# ========================================
def load_log_data():
    """ログデータを読み込む"""
    try:
        if LOG_FILE_PATH.exists():
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug("load_log_data: %d セッション読み込み", len(data.get("sessions", {})))
            return data
        logger.debug("load_log_data: ファイルなし、空データ返却")
        return {"sessions": {}}
    except Exception:
        logger.exception("load_log_data: ファイル読み込み失敗 (%s)", LOG_FILE_PATH)
        return {"sessions": {}}

def save_log_data(data):
    """ログデータを保存する"""
    try:
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        logger.debug("save_log_data: 保存完了 (%d セッション)", len(data.get("sessions", {})))
    except Exception:
        logger.exception("save_log_data: ファイル保存失敗 (%s)", LOG_FILE_PATH)

def calculate_cost(prompt_tokens, completion_tokens, pricing=None):
    """トークン数からコストを計算"""
    if pricing is None:
        pricing = PRICING
    prompt_cost = (prompt_tokens / 1000) * pricing["prompt_per_1k"]
    completion_cost = (completion_tokens / 1000) * pricing["completion_per_1k"]
    total_cost = prompt_cost + completion_cost
    return {
        "prompt_cost_usd": round(prompt_cost, 6),
        "completion_cost_usd": round(completion_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "total_cost_jpy": round(total_cost * USD_TO_JPY, 2)
    }

def get_api_key_for_region(region):
    """リージョンから API Key を取得（旧表記のリージョン名にも対応）"""
    region_key = REGION_DISPLAY_MAP.get(region, region)
    region_info = REGIONS.get(region_key)
    if region_info:
        return region_info.get("api_key", "")
    return ""

def is_anthropic_model(deployment_name):
    """Anthropic (Claude) モデルかどうかを判定"""
    return deployment_name.lower().startswith("claude")

def get_model_type(deployment_name):
    """モデルタイプを取得"""
    return "anthropic" if is_anthropic_model(deployment_name) else "openai"

def get_model_type_display(model_type):
    """モデルタイプの表示用情報を取得"""
    if model_type == "anthropic":
        return {"icon": "🟣", "name": "Anthropic (Claude)"}
    else:
        return {"icon": "🟢", "name": "OpenAI (GPT)"}

def get_all_models():
    """全モデル情報を取得（config/deployment_models.json から読み込み、sort_order 昇順でソート）"""
    metadata_list = load_model_metadata()
    all_models = []
    for meta in metadata_list:
        dep = meta.get("deployment_name", "")
        region_name = meta.get("region", "")
        region_info = REGIONS.get(region_name)
        if not region_info:
            logger.warning("get_all_models: リージョン '%s' が REGIONS に存在しません (deployment=%s)", region_name, dep)
            continue
        try:
            model_type = get_model_type(dep)
            provider = meta.get("provider", "その他")
            provider_icon = get_provider_icon(provider)
            display_name = meta.get("display_name", dep)

            # Anthropic モデルの場合は専用エンドポイントを使用
            if model_type == "anthropic":
                endpoint = region_info.get("anthropic_endpoint") or region_info.get("endpoint", "")
            else:
                endpoint = region_info.get("endpoint", "")

            # 後方互換性のため config dict を構築
            config = {
                "Azure API Key": region_info["api_key"],
                "ENDPOINT": region_info["endpoint"],
                "ENDPOINT (Anthropic Model)": region_info.get("anthropic_endpoint", ""),
                "Azure API Version": API_VERSION,
            }

            all_models.append({
                "region": region_name,
                "deployment_name": dep,
                "model_type": model_type,
                "provider": provider,
                "provider_icon": provider_icon,
                "display_name": display_name,
                "release_date": meta.get("release_date", ""),
                "sort_order": meta.get("sort_order", 999),
                "capability_tag": meta.get("capability_tag", []),
                "recommended_usage": meta.get("recommended_usage", ""),
                "endpoint": endpoint,
                "config": config,
                "dropdown_label": f"{provider_icon} {display_name} ({region_name})"
            })
        except Exception:
            logger.exception("get_all_models: モデル '%s' の処理中にエラー", dep)

    # sort_order 昇順でソート
    all_models.sort(key=lambda m: m.get("sort_order", 999))
    logger.info("get_all_models: %d モデルを検出", len(all_models))
    return all_models

def format_timestamp(ts_str):
    """タイムスタンプをフォーマット"""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    except Exception:
        logger.warning("format_timestamp: パース失敗 ts_str=%s", ts_str)
        return ts_str

def generate_session_name_with_llm(session_id, model_info, conversation_history):
    """LLMを使ってセッション名を生成"""
    logger.info(
        "generate_session_name_with_llm: session_id=%s, deployment=%s, model_type=%s",
        session_id, model_info.get("deployment_name"), model_info.get("model_type"),
    )
    # 会話履歴から要約用のテキストを作成
    conversation_text = ""
    for msg in conversation_history[:6]:  # 最初の6メッセージまで
        if msg["role"] == "user":
            conversation_text += f"ユーザー: {msg['content'][:100]}\n"
        elif msg["role"] == "assistant":
            conversation_text += f"AI: {msg['content'][:100]}\n"
    
    if not conversation_text:
        logger.debug("generate_session_name_with_llm: 会話テキストなし、スキップ")
        return None
    
    prompt = f"""以下の会話内容を最大20文字で要約し、セッション名として適切なタイトルを生成してください。
タイトルのみを出力してください。記号や絵文字は使わないでください。

会話内容:
{conversation_text}"""

    try:
        model_type = model_info.get("model_type", "openai")
        api_key = model_info.get("api_key", "")
        if not api_key:
            api_key = get_api_key_for_region(model_info.get("region", ""))
        
        start_time = time.time()
        if model_type == "anthropic":
            logger.debug(
                "generate_session_name_with_llm: Anthropic API 呼び出し開始 endpoint=%s, model=%s",
                model_info.get("endpoint"), model_info.get("deployment_name"),
            )
            client = anthropic.Anthropic(
                api_key=api_key,
                base_url=model_info.get("endpoint", ""),
            )
            response = client.messages.create(
                model=model_info.get("deployment_name", ""),
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text if response.content else None
            generated_name = raw.strip() if raw else None
            logger.debug(
                "generate_session_name_with_llm: Anthropic レスポンス response_id=%s, input_tokens=%s, output_tokens=%s",
                response.id, response.usage.input_tokens, response.usage.output_tokens,
            )
        else:
            logger.debug(
                "generate_session_name_with_llm: OpenAI API 呼び出し開始 endpoint=%s, model=%s",
                model_info.get("endpoint"), model_info.get("deployment_name"),
            )
            client = AzureOpenAI(
                api_key=api_key,
                api_version=model_info.get("api_version", "2024-12-01-preview"),
                azure_endpoint=model_info.get("endpoint", ""),
                timeout=httpx.Timeout(30.0, connect=10.0)
            )
            response = client.chat.completions.create(
                model=model_info.get("deployment_name", ""),
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=4096,
                temperature=0.7
            )
            raw = response.choices[0].message.content if response.choices else None
            generated_name = raw.strip() if raw else None
            logger.debug(
                "generate_session_name_with_llm: OpenAI レスポンス response_id=%s, prompt_tokens=%s, completion_tokens=%s",
                response.id, response.usage.prompt_tokens, response.usage.completion_tokens,
            )
        
        elapsed = time.time() - start_time
        # 20文字に切り詰め
        if generated_name and len(generated_name) > 20:
            generated_name = generated_name[:20]
        
        logger.info(
            "generate_session_name_with_llm: 完了 generated_name='%s', elapsed=%.3fs",
            generated_name, elapsed,
        )
        return generated_name
    except Exception as e:
        logger.exception("generate_session_name_with_llm: エラー session_id=%s", session_id)
        st.error(f"セッション名生成エラー: {e}")
        return None

# ========================================
# セッション状態の初期化
# ========================================
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "is_new_session" not in st.session_state:
    st.session_state.is_new_session = True
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "chat"  # "chat" or "trash"
if "generating_name" not in st.session_state:
    st.session_state.generating_name = False
if "trash_purge_mode" not in st.session_state:
    st.session_state.trash_purge_mode = None  # ゴミ箱の完全削除確認フロー用 (None / "selected" / "all" / "single:{session_id}")
if "_close_popover" not in st.session_state:
    st.session_state._close_popover = False  # popover を強制的に閉じるためのフラグ
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False  # LLM処理中フラグ（UIロック用）
if "active_expander_open" not in st.session_state:
    st.session_state.active_expander_open = True  # アクティブセッション Expander の開閉
if "completed_expander_open" not in st.session_state:
    st.session_state.completed_expander_open = False  # 終了済みセッション Expander の開閉

# ========================================
# モデル情報取得
# ========================================
all_models = get_all_models()

# ========================================
# サイドバー
# ========================================
st.sidebar.markdown(get_sidebar_title_html(), unsafe_allow_html=True)

# ログデータ読み込み
log_data = load_log_data()
sessions = log_data.get("sessions", {})

# 新規セッション作成ボタン
if st.sidebar.button("➕ 新規セッション", use_container_width=True):
    logger.info("サイドバー: 新規セッションボタン押下")
    st.session_state.current_session_id = None
    st.session_state.conversation_history = []
    st.session_state.selected_model = None
    st.session_state.is_new_session = True
    st.session_state.view_mode = "chat"
    st.rerun()

st.sidebar.markdown("---")

# セッション分類
active_sessions = sorted(
    [(k, v) for k, v in sessions.items() if not v.get("deleted", False) and v.get("status", "active") == "active"],
    key=lambda x: x[1].get("last_llm_response_at", x[1].get("created_at", "")),
    reverse=True
)
completed_sessions = sorted(
    [(k, v) for k, v in sessions.items() if not v.get("deleted", False) and v.get("status") == "completed"],
    key=lambda x: x[1].get("last_llm_response_at", x[1].get("created_at", "")),
    reverse=True
)
deleted_sessions = sorted(
    [(k, v) for k, v in sessions.items() if v.get("deleted", False) and not v.get("purged_from_trash", False)],
    key=lambda x: x[1].get("deleted_at", ""),
    reverse=True
)

# --- ヘルパー関数: セッションアイテム表示 ---
def render_session_item(session_id, session_info, container=None, show_resume=False, session_type="active"):
    """サイドバーのセッションアイテムをレンダリング
    
    Args:
        session_id: セッションID
        session_info: セッション情報
        container: 描画先コンテナ（Noneの場合はst.sidebar）
        show_resume: 再開ボタン表示フラグ
        session_type: セッションタイプ（"active" or "completed"）
    """
    if container is None:
        container = st.sidebar
    
    session_name = session_info.get("session_name", session_id)
    model_info = session_info.get("model", {})
    deployment_name = model_info.get("deployment_name", "不明")
    model_display_name = model_info.get("display_name") or get_display_name_for_deployment(deployment_name)
    region_raw = model_info.get("region", "")
    region_display = format_region_display(region_raw)
    model_type = model_info.get("model_type", "openai")
    status = session_info.get("status", "active")
    provider = model_info.get("provider") or model_info.get("constructor") or get_provider_for_deployment(deployment_name)
    type_icon = model_info.get("provider_icon") or model_info.get("constructor_icon") or get_provider_icon(provider)
    
    # CSSマーカーを挿入（セッションタイプ別のスタイル適用用）
    marker_class = "active-session-marker" if session_type == "active" else "completed-session-marker"
    container.markdown(get_marker_div_html(marker_class), unsafe_allow_html=True)
    
    # セッション選択行（カード形式）
    col1, col2 = container.columns([6, 1])
    with col1:
        # セッション名を表示（長すぎる場合は省略）
        display_name = session_name[:25] + "..." if len(session_name) > 25 else session_name
        # モデル情報を全体表示（省略なし）
        model_display = f"{type_icon} {model_display_name} | 📍{region_display}"
        
        # セッションカード風のボタン（2行表示）
        button_label = f"{display_name}\n{model_display}"
        if st.button(button_label, key=f"btn_{session_id}", use_container_width=True):
            logger.info("セッション選択: session_id=%s, name=%s", session_id, session_name)
            st.session_state.current_session_id = session_id
            st.session_state.conversation_history = session_info.get("conversation_history", [])
            model_info_copy = model_info.copy()
            if not model_info_copy.get("api_key"):
                model_info_copy["api_key"] = get_api_key_for_region(region_raw)
            st.session_state.selected_model = model_info_copy
            st.session_state.is_new_session = False
            st.session_state.view_mode = "chat"
            st.rerun()
    
    with col2:
        # メニューボタン（▾）
        with st.popover("▾"):
            if status == "active":
                # ===== アクティブセッション: 名前変更・名前生成・終了 =====
                
                # セッション名変更（常にテキスト入力を表示）
                new_name = st.text_input("📝 新しいセッション名", value=session_name, key=f"sidebar_rename_input_{session_id}")
                if st.button("変更保存", key=f"sidebar_rename_save_{session_id}", use_container_width=True):
                    if new_name and new_name.strip() and new_name.strip() != session_name:
                        log_data = load_log_data()
                        if session_id in log_data.get("sessions", {}):
                            old_name = log_data["sessions"][session_id]["session_name"]
                            logger.info("サイドバー名前変更: session_id=%s, '%s' → '%s'", session_id, old_name, new_name.strip())
                            log_data["sessions"][session_id]["session_name"] = new_name.strip()
                            log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                            log_data["sessions"][session_id]["name_changes"].append({
                                "timestamp": datetime.now().isoformat(),
                                "old_name": old_name,
                                "new_name": new_name.strip()
                            })
                            save_log_data(log_data)
                        st.session_state._close_popover = True
                        st.rerun()
                
                # セッション名生成
                if st.button("✨ 名前生成", key=f"menu_gen_{session_id}", use_container_width=True):
                    st.session_state.is_processing = True
                    with st.spinner("生成中..."):
                        generated = generate_session_name_with_llm(
                            session_id, model_info, session_info.get("conversation_history", [])
                        )
                        if generated:
                            log_data = load_log_data()
                            old_name = log_data["sessions"][session_id]["session_name"]
                            log_data["sessions"][session_id]["session_name"] = generated
                            log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                            log_data["sessions"][session_id]["name_changes"].append({
                                "timestamp": datetime.now().isoformat(),
                                "old_name": old_name,
                                "new_name": generated,
                                "generated_by_llm": True
                            })
                            save_log_data(log_data)
                            st.session_state.is_processing = False
                            st.session_state._close_popover = True
                            st.rerun()
                        else:
                            st.session_state.is_processing = False
                            st.warning("セッション名を生成できませんでした")
                
                # セッション終了
                if st.button("🏁 終了", key=f"menu_end_{session_id}", use_container_width=True):
                    logger.info("サイドバー: セッション終了 session_id=%s", session_id)
                    log_data = load_log_data()
                    session_data = log_data["sessions"][session_id]
                    messages = session_data.get("messages", [])
                    
                    total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
                    total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
                    total_turns = len(messages)
                    response_times = [m.get("response", {}).get("response_time_seconds", 0) for m in messages]
                    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                    
                    session_end = datetime.now()
                    session_start = datetime.fromisoformat(session_data.get("created_at", session_end.isoformat()))
                    session_duration = (session_end - session_start).total_seconds()
                    
                    session_data["status"] = "completed"
                    session_data["ended_at"] = session_end.isoformat()
                    session_data["updated_at"] = session_end.isoformat()
                    session_data["stats"] = {
                        "total_turns": total_turns,
                        "total_tokens": total_tokens,
                        "total_cost_usd": round(total_cost, 6),
                        "total_cost_jpy": round(total_cost * USD_TO_JPY, 2),
                        "avg_response_time_seconds": round(avg_response_time, 3),
                        "min_response_time_seconds": round(min(response_times), 3) if response_times else 0,
                        "max_response_time_seconds": round(max(response_times), 3) if response_times else 0,
                        "session_duration_seconds": round(session_duration, 3),
                        "conversation_length": len(session_data.get("conversation_history", []))
                    }
                    logger.debug("セッション終了統計: turns=%d, tokens=%d, cost=$%.6f, duration=%.1fs", total_turns, total_tokens, total_cost, session_duration)
                    save_log_data(log_data)
                    st.session_state._close_popover = True
                    st.rerun()
            
            else:
                # ===== 終了済セッション: 再開・削除（ダイレクト実行） =====
                
                # セッション再開
                if st.button("🔄 再開", key=f"menu_resume_{session_id}", use_container_width=True):
                    logger.info("サイドバー: セッション再開 session_id=%s", session_id)
                    log_data = load_log_data()
                    log_data["sessions"][session_id]["status"] = "active"
                    log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                    save_log_data(log_data)
                    st.session_state.current_session_id = session_id
                    st.session_state.conversation_history = session_info.get("conversation_history", [])
                    model_info_copy = model_info.copy()
                    if not model_info_copy.get("api_key"):
                        model_info_copy["api_key"] = get_api_key_for_region(region_raw)
                    st.session_state.selected_model = model_info_copy
                    st.session_state.is_new_session = False
                    st.session_state.view_mode = "chat"
                    st.session_state._close_popover = True
                    st.rerun()
                
                # セッション削除（ゴミ箱へ移動・確認なし）
                if st.button("🗑️ 削除", key=f"menu_del_{session_id}", use_container_width=True):
                    logger.info("サイドバー: セッション削除 session_id=%s", session_id)
                    log_data = load_log_data()
                    log_data["sessions"][session_id]["deleted"] = True
                    log_data["sessions"][session_id]["deleted_at"] = datetime.now().isoformat()
                    log_data["sessions"][session_id]["updated_at"] = datetime.now().isoformat()
                    save_log_data(log_data)
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                        st.session_state.conversation_history = []
                        st.session_state.selected_model = None
                        st.session_state.is_new_session = True
                    st.session_state._close_popover = True
                    st.rerun()

# --- アクティブセッション ---
with st.sidebar.expander(f"▶️ アクティブ ({len(active_sessions)})", expanded=st.session_state.active_expander_open):
    if active_sessions:
        for session_id, session_info in active_sessions:
            render_session_item(session_id, session_info, container=st, session_type="active")
    else:
        st.caption("アクティブなセッションはありません")

# --- 終了済みセッション ---
with st.sidebar.expander(f"✅ 終了済み ({len(completed_sessions)})", expanded=st.session_state.completed_expander_open):
    if completed_sessions:
        for session_id, session_info in completed_sessions:
            render_session_item(session_id, session_info, container=st, show_resume=True, session_type="completed")
    else:
        st.caption("終了済みのセッションはありません")

st.sidebar.markdown("---")

# --- ゴミ箱 ---
# CSSマーカーを挿入
st.sidebar.markdown(get_marker_div_html("trash-button-marker"), unsafe_allow_html=True)
if st.sidebar.button(f"🗑️ ゴミ箱 ({len(deleted_sessions)})", use_container_width=True):
    st.session_state.view_mode = "trash"
    st.session_state.current_session_id = None
    st.session_state.is_new_session = False
    st.session_state.trash_purge_mode = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"アクティブ: {len(active_sessions)} | 終了: {len(completed_sessions)} | 削除: {len(deleted_sessions)}")

# ========================================
# メインコンテンツ
# ========================================

# ゴミ箱表示モード
if st.session_state.view_mode == "trash":
    st.title("ゴミ箱")
    st.markdown("---")
    
    log_data = load_log_data()
    deleted_sessions = sorted(
        [(k, v) for k, v in log_data.get("sessions", {}).items() if v.get("deleted", False) and not v.get("purged_from_trash", False)],
        key=lambda x: x[1].get("deleted_at", ""),
        reverse=True
    )
    
    has_sessions = len(deleted_sessions) > 0
    
    # --- 一括操作ボタン群（上部） ---
    btn_row1_col1, btn_row1_col2, btn_row1_col3 = st.columns(3)
    
    # チェック済みセッションを事前に取得（ボタンの有効/無効判定に使用）
    trash_checked_ids = {sid for sid, _ in deleted_sessions if st.session_state.get(f"trash_cb_{sid}", False)}
    has_checked = len(trash_checked_ids) > 0
    
    with btn_row1_col1:
        if st.button("☑️ 全て選択", use_container_width=True, disabled=not has_sessions):
            for sid, _ in deleted_sessions:
                st.session_state[f"trash_cb_{sid}"] = True
            st.rerun()
    
    with btn_row1_col2:
        if st.button("⬜ チェックを全て外す", use_container_width=True, disabled=not has_checked):
            for sid, _ in deleted_sessions:
                st.session_state[f"trash_cb_{sid}"] = False
            st.rerun()
    
    with btn_row1_col3:
        if st.button("🔄 チェックしたセッションを復元", use_container_width=True, disabled=not has_checked):
            logger.info("ゴミ箱: チェックしたセッションを復元 (%d件)", len(trash_checked_ids))
            log_data = load_log_data()
            for sid in trash_checked_ids:
                if sid in log_data.get("sessions", {}):
                    log_data["sessions"][sid]["deleted"] = False
                    log_data["sessions"][sid].pop("deleted_at", None)
                    log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
            save_log_data(log_data)
            st.rerun()
    
    st.markdown(get_marker_div_html("danger-btn-marker"), unsafe_allow_html=True)
    if st.button("🗑️ チェックしたセッションを完全削除", type="primary", use_container_width=True, disabled=not has_checked):
        st.session_state.trash_purge_mode = "selected"
        st.rerun()
    
    # --- 完全削除の確認フロー ---
    if st.session_state.trash_purge_mode == "selected":
        st.markdown("")
        st.error("⚠️ 完全削除すると元に戻せません")
        
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            st.markdown(get_marker_div_html("danger-btn-marker"), unsafe_allow_html=True)
            if st.button("完全削除する", type="primary", use_container_width=True):
                logger.info("ゴミ箱: チェックしたセッションを完全削除 (%d件)", len(trash_checked_ids))
                log_data = load_log_data()
                for sid in trash_checked_ids:
                    if sid in log_data.get("sessions", {}):
                        log_data["sessions"][sid]["purged_from_trash"] = True
                        log_data["sessions"][sid]["updated_at"] = datetime.now().isoformat()
                save_log_data(log_data)
                st.session_state.trash_purge_mode = None
                st.rerun()
        
        with cancel_col:
            if st.button("キャンセル", use_container_width=True):
                st.session_state.trash_purge_mode = None
                st.rerun()
    
    st.markdown("---")
    
    # --- セッション一覧 ---
    if has_sessions:
        for session_id, session_info in deleted_sessions:
            session_name = session_info.get("session_name", session_id)
            model_info = session_info.get("model", {})
            provider = model_info.get("provider") or model_info.get("constructor") or get_provider_for_deployment(model_info.get("deployment_name", ""))
            type_icon = model_info.get("provider_icon") or model_info.get("constructor_icon") or get_provider_icon(provider)
            
            messages = session_info.get("messages", [])
            total_turns = len(messages)
            total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
            total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
            
            with st.container():
                col_cb, col1, col2, col3, col4, col5 = st.columns([0.4, 2.6, 2, 1, 1, 2])
                with col_cb:
                    st.checkbox("", key=f"trash_cb_{session_id}", label_visibility="collapsed")
                with col1:
                    st.markdown(f"**{session_name}**")
                    trash_display_name = model_info.get("display_name") or get_display_name_for_deployment(model_info.get("deployment_name", ""))
                    st.caption(f"{type_icon} {trash_display_name} | 📍 {format_region_display(model_info.get('region', ''))}")
                with col2:
                    st.caption(f"🕐 作成: {format_timestamp(session_info.get('created_at', ''))}")
                    st.caption(f"🗑️ 削除: {format_timestamp(session_info.get('deleted_at', ''))}")
                with col3:
                    st.metric("ターン", total_turns)
                with col4:
                    st.metric("トークン", f"{total_tokens:,}")
                with col5:
                    st.metric("コスト", f"${total_cost:.4f}")
                st.markdown("---")
    else:
        st.info("🗑️ ゴミ箱は空です")
    
    st.markdown("")
    
    # 戻るボタン
    if st.button("↩️ 戻る", use_container_width=True):
        st.session_state.view_mode = "chat"
        st.session_state.is_new_session = True
        st.session_state.trash_purge_mode = None
        st.rerun()

else:
    # 現在のセッション情報取得
    current_session = None
    if st.session_state.current_session_id:
        log_data = load_log_data()
        current_session = log_data.get("sessions", {}).get(st.session_state.current_session_id)

    # ========================================
    # テーマ切替トグル（右ペイン上部）
    # ========================================
    _theme_cols = st.columns([8, 1])
    with _theme_cols[1]:
        _is_dark = st.toggle("🌙", value=(st.session_state.app_theme == "dark"), key="theme_toggle")
        if _is_dark != (st.session_state.app_theme == "dark"):
            st.session_state.app_theme = "dark" if _is_dark else "light"
            st.rerun()

    # ========================================
    # ヘッダー部分
    # ========================================
    if st.session_state.is_new_session or current_session is None:
        # 新規セッション - モデル選択
        st.title("新規チャットセッション")
        st.markdown("---")
        
        st.subheader("🤖 使用するモデルを選択")
        
        if all_models:
            model_options = [m["dropdown_label"] for m in all_models]
            selected_dropdown_label = st.selectbox(
                "モデル選択",
                model_options,
                index=0
            )
            
            # 選択されたモデル情報を取得
            selected_model_info = next(
                (m for m in all_models if m["dropdown_label"] == selected_dropdown_label),
                None
            )
            
            if selected_model_info:
                cap_tags = ", ".join(selected_model_info.get("capability_tag", []))
                st.info(f"""
                **選択されたモデル:**
                - モデル名: `{selected_model_info['display_name']}`
                - プロバイダー: {selected_model_info.get('provider_icon', '🔵')} `{selected_model_info.get('provider', 'その他')}`
                - リージョン: `{format_region_display(selected_model_info.get('region', ''))}`
                - リリース: `{selected_model_info.get('release_date', '')}`
                - 用途タグ: `{cap_tags}`
                - 利用推奨: `{selected_model_info.get('recommended_usage', '')}`
                """)
                
                # セッション開始ボタン
                if st.button("🚀 チャットを開始", type="primary", use_container_width=True):
                    # 新規セッション作成
                    session_start = datetime.now()
                    new_session_id = session_start.strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
                    auto_session_name = f"Session_{session_start.strftime('%Y%m%d_%H%M%S')}"
                    logger.info(
                        "新規セッション作成: session_id=%s, deployment=%s, region=%s, model_type=%s",
                        new_session_id, selected_model_info["deployment_name"],
                        selected_model_info["region"], selected_model_info["model_type"],
                    )
                    
                    config = selected_model_info["config"]
                    
                    new_session = {
                        "session_id": new_session_id,
                        "session_name": auto_session_name,
                        "created_at": session_start.isoformat(),
                        "updated_at": session_start.isoformat(),
                        "last_llm_response_at": session_start.isoformat(),
                        "status": "active",
                        "model": {
                            "deployment_name": selected_model_info["deployment_name"],
                            "display_name": selected_model_info.get("display_name", selected_model_info["deployment_name"]),
                            "region": selected_model_info["region"],
                            "model_type": selected_model_info["model_type"],
                            "provider": selected_model_info.get("provider", get_provider_for_deployment(selected_model_info["deployment_name"])),
                            "provider_icon": selected_model_info.get("provider_icon", get_provider_icon(selected_model_info.get("provider", "その他"))),
                            "release_date": selected_model_info.get("release_date", ""),
                            "sort_order": selected_model_info.get("sort_order", 999),
                            "capability_tag": selected_model_info.get("capability_tag", []),
                            "recommended_usage": selected_model_info.get("recommended_usage", ""),
                            "endpoint": selected_model_info["endpoint"],
                            "api_version": config.get("Azure API Version", "2024-12-01-preview"),
                            "api_key": config.get("Azure API Key", "")
                        },
                        "config": {
                            "pricing": PRICING,
                            "usd_to_jpy": USD_TO_JPY
                        },
                        "conversation_history": [
                            {"role": "system", "content": "あなたは親切で知識豊富なアシスタントです。日本語で回答してください。会話の文脈を踏まえて応答してください。"}
                        ],
                        "messages": [],
                        "errors": [],
                        "stats": None,
                        "name_changes": []
                    }
                    
                    log_data = load_log_data()
                    log_data["sessions"][new_session_id] = new_session
                    save_log_data(log_data)
                    
                    st.session_state.current_session_id = new_session_id
                    st.session_state.conversation_history = new_session["conversation_history"]
                    st.session_state.selected_model = new_session["model"]
                    st.session_state.is_new_session = False
                    st.rerun()
        else:
            logger.warning("利用可能なモデルが 0 件。REGIONS 設定を確認してください。")
            st.error("利用可能なモデルがありません。設定ファイルを確認してください。")

    else:
        # 既存セッション - チャット画面
        session_name = current_session.get("session_name", st.session_state.current_session_id)
        model_info = current_session.get("model", {})
        session_status = current_session.get("status", "active")
        is_completed = session_status == "completed"
        
        # ========================================
        # セッションヘッダー
        # ========================================
        st.title(session_name)
        created_at = current_session.get("created_at", "")
        if created_at:
            st.caption(f"📅 作成: {format_timestamp(created_at)}")
        
        col_left, col_right = st.columns([3, 1])
        with col_right:
            with st.popover("操作"):
                if session_status == "active":
                    # ===== アクティブセッション: 名前変更・名前生成・終了 =====
                    
                    # セッション名変更
                    new_name = st.text_input("📝 新しいセッション名", value=session_name, key=f"rename_input_{st.session_state.current_session_id}")
                    if st.button("入力した名前に変更", key="rename_btn", use_container_width=True):
                        if new_name and new_name != session_name:
                            log_data = load_log_data()
                            old_name = log_data["sessions"][st.session_state.current_session_id]["session_name"]
                            logger.info("メイン名前変更: session_id=%s, '%s' → '%s'", st.session_state.current_session_id, old_name, new_name)
                            log_data["sessions"][st.session_state.current_session_id]["session_name"] = new_name
                            log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                            log_data["sessions"][st.session_state.current_session_id]["name_changes"].append({
                                "timestamp": datetime.now().isoformat(),
                                "old_name": old_name,
                                "new_name": new_name
                            })
                            save_log_data(log_data)
                            st.success("セッション名を変更しました")
                            st.session_state._close_popover = True
                            st.rerun()
                    
                    # セッション名生成
                    if st.button("✨ LLMで名前を生成", key="gen_name_btn", use_container_width=True):
                        st.session_state.is_processing = True
                        with st.spinner("生成中..."):
                            generated = generate_session_name_with_llm(
                                st.session_state.current_session_id,
                                model_info,
                                st.session_state.conversation_history
                            )
                            if generated:
                                log_data = load_log_data()
                                old_name = log_data["sessions"][st.session_state.current_session_id]["session_name"]
                                log_data["sessions"][st.session_state.current_session_id]["session_name"] = generated
                                log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                                log_data["sessions"][st.session_state.current_session_id]["name_changes"].append({
                                    "timestamp": datetime.now().isoformat(),
                                    "old_name": old_name,
                                    "new_name": generated,
                                    "generated_by_llm": True
                                })
                                save_log_data(log_data)
                                st.session_state.is_processing = False
                                st.success(f"生成完了: {generated}")
                                st.session_state._close_popover = True
                                st.rerun()
                            else:
                                st.session_state.is_processing = False
                                st.warning("セッション名を生成できませんでした")
                    
                    # セッション終了
                    if st.button("🏁 このセッションを終了", key="end_session_btn", use_container_width=True):
                        logger.info("メイン: セッション終了 session_id=%s", st.session_state.current_session_id)
                        log_data = load_log_data()
                        session_data = log_data["sessions"][st.session_state.current_session_id]
                        messages = session_data.get("messages", [])
                        
                        total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
                        total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
                        total_turns = len(messages)
                        response_times = [m.get("response", {}).get("response_time_seconds", 0) for m in messages]
                        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                        
                        session_end = datetime.now()
                        session_start = datetime.fromisoformat(session_data.get("created_at", session_end.isoformat()))
                        session_duration = (session_end - session_start).total_seconds()
                        
                        session_data["status"] = "completed"
                        session_data["ended_at"] = session_end.isoformat()
                        session_data["updated_at"] = session_end.isoformat()
                        session_data["stats"] = {
                            "total_turns": total_turns,
                            "total_tokens": total_tokens,
                            "total_cost_usd": round(total_cost, 6),
                            "total_cost_jpy": round(total_cost * USD_TO_JPY, 2),
                            "avg_response_time_seconds": round(avg_response_time, 3),
                            "min_response_time_seconds": round(min(response_times), 3) if response_times else 0,
                            "max_response_time_seconds": round(max(response_times), 3) if response_times else 0,
                            "session_duration_seconds": round(session_duration, 3),
                            "conversation_length": len(session_data.get("conversation_history", []))
                        }
                        logger.debug("セッション終了統計: turns=%d, tokens=%d, cost=$%.6f, duration=%.1fs", total_turns, total_tokens, total_cost, session_duration)
                        save_log_data(log_data)
                        st.success("セッションを終了しました")
                        st.session_state._close_popover = True
                        st.rerun()
                
                else:
                    # ===== 終了済セッション: 再開・削除（ダイレクト実行） =====
                    
                    # セッション再開
                    if st.button("🔄 セッションを再開", key="resume_session_btn", use_container_width=True):
                        logger.info("メイン: セッション再開 session_id=%s", st.session_state.current_session_id)
                        log_data = load_log_data()
                        log_data["sessions"][st.session_state.current_session_id]["status"] = "active"
                        log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                        save_log_data(log_data)
                        st.success("セッションを再開しました")
                        st.session_state._close_popover = True
                        st.rerun()
                    
                    # セッション削除（ゴミ箱へ移動・確認なし）
                    if st.button("🗑️ このセッションを削除", key="delete_session_btn", use_container_width=True):
                        logger.info("メイン: セッション削除 session_id=%s", st.session_state.current_session_id)
                        log_data = load_log_data()
                        log_data["sessions"][st.session_state.current_session_id]["deleted"] = True
                        log_data["sessions"][st.session_state.current_session_id]["deleted_at"] = datetime.now().isoformat()
                        log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                        save_log_data(log_data)
                        st.session_state.current_session_id = None
                        st.session_state.conversation_history = []
                        st.session_state.selected_model = None
                        st.session_state.is_new_session = True
                        st.session_state._close_popover = True
                        st.rerun()
        
        # モデル情報表示（変更不可）※プロバイダーで表示
        provider = model_info.get("provider") or model_info.get("constructor") or get_provider_for_deployment(model_info.get("deployment_name", ""))
        provider_icon = model_info.get("provider_icon") or model_info.get("constructor_icon") or get_provider_icon(provider)
        model_display_name = model_info.get("display_name") or get_display_name_for_deployment(model_info.get("deployment_name", ""))
        st.markdown(get_model_badge_html(
            provider_icon=provider_icon,
            model_display_name=model_display_name,
            region_display=format_region_display(model_info.get("region", "")),
            provider=provider,
        ), unsafe_allow_html=True)
        # 追加メタデータ表示
        header_cap_tags = model_info.get("capability_tag", [])
        if isinstance(header_cap_tags, list):
            header_cap_tags = ", ".join(header_cap_tags)
        release_date = model_info.get("release_date", "")
        recommended_usage = model_info.get("recommended_usage", "")
        meta_parts = []
        if release_date:
            meta_parts.append(f"リリース: {release_date}")
        if header_cap_tags:
            meta_parts.append(f"用途: {header_cap_tags}")
        if recommended_usage:
            meta_parts.append(f"推奨: {recommended_usage}")
        if meta_parts:
            st.caption(" | ".join(meta_parts))
        
        st.caption("※ セッション途中でモデルを変更することはできません")
        
        st.markdown("---")
        
        # ========================================
        # メトリクス表示
        # ========================================
        # ページ上部アンカー
        st.markdown(get_page_anchor_html("page-top"), unsafe_allow_html=True)
        
        stats = current_session.get("stats")
        messages = current_session.get("messages", [])
        
        # リアルタイム統計計算
        total_tokens = sum(m.get("metrics", {}).get("total_tokens", 0) for m in messages)
        total_cost = sum(m.get("cost", {}).get("total_cost_usd", 0) for m in messages)
        total_turns = len(messages)
        avg_response_time = (
            sum(m.get("response", {}).get("response_time_seconds", 0) for m in messages) / len(messages)
            if messages else 0
        )
        
        # メトリクス行
        metric_cols = st.columns([1, 1, 1, 1, 1])
        with metric_cols[0]:
            st.metric("ターン数", total_turns)
        with metric_cols[1]:
            st.metric("総トークン", f"{total_tokens:,}")
        with metric_cols[2]:
            st.metric("コスト (USD)", f"${total_cost:.4f}")
        with metric_cols[3]:
            st.metric("コスト (JPY)", f"¥{total_cost * USD_TO_JPY:.2f}")
        with metric_cols[4]:
            st.metric("平均応答時間", f"{avg_response_time:.2f}秒")
        
        st.markdown("---")
        
        # ========================================
        # 会話履歴表示（最下部へを同段右側に配置）
        # ========================================
        col_hist, col_bottom = st.columns([4, 1])
        with col_hist:
            st.subheader("📝 会話履歴")
        with col_bottom:
            st.markdown(get_nav_bottom_html(
                nav_bottom_bg=_current_theme["nav_bottom_bg"],
                nav_text=_current_theme["nav_text"],
            ), unsafe_allow_html=True)
        
        conversation = st.session_state.conversation_history
        
        # 会話インデックスからメッセージログへのマッピング
        user_msg_idx = 0
        for i, msg in enumerate(conversation):
            if msg["role"] == "system":
                continue  # システムメッセージは非表示
            
            if msg["role"] == "user":
                # 対応するメッセージログからタイムスタンプを取得
                msg_log = messages[user_msg_idx] if user_msg_idx < len(messages) else None
                timestamp_str = ""
                if msg_log:
                    request_ts = msg_log.get("request", {}).get("timestamp", "")
                    if request_ts:
                        timestamp_str = f'<span style="color:{_current_theme["timestamp_color"]}; font-size:0.8em; float:right;">📤 {format_timestamp(request_ts)}</span>'
                
                st.markdown(get_user_message_html(
                    timestamp_str=timestamp_str,
                    content=msg["content"],
                ), unsafe_allow_html=True)
            
            elif msg["role"] == "assistant":
                # 対応するメッセージログを検索
                msg_log = messages[user_msg_idx] if user_msg_idx < len(messages) else None
                user_msg_idx += 1  # 次のユーザーメッセージへ
                
                if msg_log:
                    response_time = msg_log.get("response", {}).get("response_time_seconds", 0)
                    tokens = msg_log.get("metrics", {}).get("total_tokens", 0)
                    cost_jpy = msg_log.get("cost", {}).get("total_cost_jpy", 0)
                    metrics_str = f"⏱️ {response_time:.2f}秒 | 🔢 {tokens:,}トークン | 💰 ¥{cost_jpy:.2f}"
                else:
                    metrics_str = ""
                
                # ユニークなメッセージIDを生成
                msg_id = f"ai_msg_{i}"
                # コンテンツをエスケープ（JavaScriptで使用）
                escaped_content = msg['content'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('`', '\\`')
                
                # AI回答表示（コピーボタンなしのマークダウン部分）
                st.markdown(get_ai_message_html(
                    ai_metrics_color=_current_theme["ai_metrics_color"],
                    metrics_str=metrics_str,
                    content=msg["content"],
                ), unsafe_allow_html=True)
                
                # コピーボタン（components.htmlで動作するJavaScript）
                components.html(get_copy_button_block_html(
                    msg_id=msg_id,
                    copy_btn_bg=_current_theme["copy_btn_bg"],
                    copy_btn_text=_current_theme["copy_btn_text"],
                    copy_btn_copied_bg=_current_theme["copy_btn_copied_bg"],
                    copy_btn_copied_text=_current_theme["copy_btn_copied_text"],
                    escaped_content=escaped_content,
                ), height=40)
        
        # 最上部へのナビゲーション
        st.markdown(get_nav_top_html(
            nav_top_bg=_current_theme["nav_top_bg"],
            nav_text=_current_theme["nav_text"],
        ), unsafe_allow_html=True)
        
        st.markdown("---")
    
        # ========================================
        # プロンプト入力フォーム
        # ========================================
        
        # 終了済みセッションの場合は入力を無効化
        if is_completed:
            st.info("✅ このセッションは終了済みです。メッセージを送信するには、セッションを再開してください。")
            
            if st.button("🔄 セッションを再開してチャットを続ける", type="primary", use_container_width=True):
                log_data = load_log_data()
                log_data["sessions"][st.session_state.current_session_id]["status"] = "active"
                log_data["sessions"][st.session_state.current_session_id]["updated_at"] = datetime.now().isoformat()
                save_log_data(log_data)
                st.success("セッションを再開しました")
                st.rerun()
        else:
            st.subheader("💬 メッセージ送信")
            
            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_area(
                    "プロンプトを入力",
                    height=100,
                    placeholder="メッセージを入力してください...",
                    key="user_input",
                    label_visibility="collapsed"
                )
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    submit_button = st.form_submit_button("📤 送信", type="primary", use_container_width=True)
        
        if not is_completed and submit_button and user_input.strip():
            # API呼び出し
            st.session_state.is_processing = True
            logger.info(
                "チャット送信: session_id=%s, input_chars=%d",
                st.session_state.current_session_id, len(user_input.strip()),
            )
            model_type = model_info.get("model_type", "openai")
            type_display = get_model_type_display(model_type)
            deployment_name = model_info.get("deployment_name", "")
            
            # API Key を取得（保存されていなければリージョンから取得）
            api_key = model_info.get("api_key", "")
            if not api_key:
                api_key = get_api_key_for_region(model_info.get("region", ""))
                # セッションに API Key を保存
                if api_key:
                    log_data = load_log_data()
                    log_data["sessions"][st.session_state.current_session_id]["model"]["api_key"] = api_key
                    save_log_data(log_data)
            
            # モデル別料金を取得
            model_pricing = get_pricing_for_model(deployment_name, model_type)
            
            with st.spinner(f"🔄 {type_display['icon']} AIが応答を生成中..."):
                try:
                    # 会話履歴更新
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    request_time = datetime.now()
                    start_time = time.time()
                    
                    # ========================================
                    # モデルタイプに応じたAPI呼び出し
                    # ========================================
                    if model_type == "anthropic":
                        # Anthropic クライアント初期化
                        logger.info(
                            "API呼び出し開始 [Anthropic]: deployment=%s, endpoint=%s, region=%s, history_len=%d",
                            deployment_name, model_info.get("endpoint"), model_info.get("region"),
                            len(st.session_state.conversation_history),
                        )
                        client = anthropic.Anthropic(
                            api_key=api_key,
                            base_url=model_info.get("endpoint", ""),
                        )
                        
                        # system メッセージを分離
                        system_message = ""
                        anthropic_messages = []
                        for msg in st.session_state.conversation_history:
                            if msg["role"] == "system":
                                system_message = msg["content"]
                            else:
                                anthropic_messages.append(msg)
                        
                        # Anthropic API呼び出し
                        response = client.messages.create(
                            model=model_info.get("deployment_name", ""),
                            max_tokens=16384,
                            system=system_message,
                            messages=anthropic_messages
                        )
                        
                        elapsed = time.time() - start_time
                        response_time_dt = datetime.now()
                        
                        # Anthropic レスポンス解析
                        ai_response = response.content[0].text if response.content else ""
                        prompt_tokens = response.usage.input_tokens
                        completion_tokens = response.usage.output_tokens
                        total_tokens_turn = prompt_tokens + completion_tokens
                        finish_reason = response.stop_reason
                        response_model = response.model
                        response_id = response.id
                        
                        logger.info(
                            "API応答完了 [Anthropic]: response_id=%s, model=%s, elapsed=%.3fs, "
                            "prompt_tokens=%d, completion_tokens=%d, total_tokens=%d, finish_reason=%s",
                            response_id, response_model, elapsed,
                            prompt_tokens, completion_tokens, total_tokens_turn, finish_reason,
                        )
                        logger.debug(
                            "API応答詳細 [Anthropic]: response_chars=%d, stop_reason=%s",
                            len(ai_response), finish_reason,
                        )
                        
                    else:
                        # OpenAI クライアント初期化
                        logger.info(
                            "API呼び出し開始 [OpenAI]: deployment=%s, endpoint=%s, region=%s, "
                            "api_version=%s, history_len=%d",
                            deployment_name, model_info.get("endpoint"), model_info.get("region"),
                            model_info.get("api_version"), len(st.session_state.conversation_history),
                        )
                        client = AzureOpenAI(
                            api_key=api_key,
                            api_version=model_info.get("api_version", "2024-12-01-preview"),
                            azure_endpoint=model_info.get("endpoint", ""),
                            timeout=httpx.Timeout(120.0, connect=10.0)
                        )
                        
                        # OpenAI API呼び出し
                        response = client.chat.completions.create(
                            model=model_info.get("deployment_name", ""),
                            messages=st.session_state.conversation_history,
                            max_completion_tokens=16384,
                            temperature=0.7
                        )
                        
                        elapsed = time.time() - start_time
                        response_time_dt = datetime.now()
                        
                        # OpenAI レスポンス解析
                        choice = response.choices[0]
                        ai_response = choice.message.content or ""
                        prompt_tokens = response.usage.prompt_tokens
                        completion_tokens = response.usage.completion_tokens
                        total_tokens_turn = response.usage.total_tokens
                        finish_reason = choice.finish_reason
                        response_model = response.model
                        response_id = response.id
                        
                        logger.info(
                            "API応答完了 [OpenAI]: response_id=%s, model=%s, elapsed=%.3fs, "
                            "prompt_tokens=%d, completion_tokens=%d, total_tokens=%d, finish_reason=%s",
                            response_id, response_model, elapsed,
                            prompt_tokens, completion_tokens, total_tokens_turn, finish_reason,
                        )
                        logger.debug(
                            "API応答詳細 [OpenAI]: response_chars=%d, finish_reason=%s",
                            len(ai_response), finish_reason,
                        )
                    
                    cost_info = calculate_cost(prompt_tokens, completion_tokens, model_pricing)
                    
                    # 会話履歴に追加
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    # ログ保存
                    message_log = {
                        "turn": len(messages) + 1,
                        "request": {
                            "timestamp": request_time.isoformat(),
                            "user_input": user_input,
                            "user_input_chars": len(user_input)
                        },
                        "response": {
                            "timestamp": response_time_dt.isoformat(),
                            "response_time_seconds": round(elapsed, 3),
                            "model": response_model,
                            "model_type": model_type,
                            "region": model_info.get("region", ""),
                            "response_id": response_id,
                            "finish_reason": finish_reason,
                            "ai_response": ai_response,
                            "ai_response_chars": len(ai_response)
                        },
                        "metrics": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens_turn,
                            "tokens_per_second": round(completion_tokens / elapsed, 2) if elapsed > 0 else 0
                        },
                        "cost": cost_info
                    }
                    
                    log_data = load_log_data()
                    log_data["sessions"][st.session_state.current_session_id]["messages"].append(message_log)
                    log_data["sessions"][st.session_state.current_session_id]["conversation_history"] = st.session_state.conversation_history
                    log_data["sessions"][st.session_state.current_session_id]["updated_at"] = response_time_dt.isoformat()
                    log_data["sessions"][st.session_state.current_session_id]["last_llm_response_at"] = response_time_dt.isoformat()
                    save_log_data(log_data)
                    
                    st.session_state.is_processing = False
                    st.rerun()
                    
                except Exception as e:
                    # エラー処理
                    logger.exception(
                        "API呼び出しエラー: session_id=%s, deployment=%s, model_type=%s, region=%s",
                        st.session_state.current_session_id, deployment_name, model_type,
                        model_info.get("region"),
                    )
                    error_time = datetime.now()
                    st.session_state.conversation_history.pop()  # 失敗したユーザー入力を削除
                    
                    error_log = {
                        "turn": len(messages) + 1,
                        "timestamp": error_time.isoformat(),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "user_input": user_input
                    }
                    
                    log_data = load_log_data()
                    log_data["sessions"][st.session_state.current_session_id]["errors"].append(error_log)
                    log_data["sessions"][st.session_state.current_session_id]["updated_at"] = error_time.isoformat()
                    save_log_data(log_data)
                    
                    st.session_state.is_processing = False
                    st.error(f"❌ エラーが発生しました: {type(e).__name__}: {e}")
        
        # ========================================
        # エラー表示
        # ========================================
        errors = current_session.get("errors", [])
        if errors:
            with st.expander(f"❌ エラー履歴 ({len(errors)}件)", expanded=False):
                for error in errors:
                    st.error(f"""
                    **{error.get('error_type', 'Error')}** ({format_timestamp(error.get('timestamp', ''))})
                    
                    {error.get('error_message', '')[:200]}...
                    """)

# ========================================
# フッター
# ========================================
st.markdown("---")
st.caption(f"📁 ログファイル: {LOG_FILE_PATH}")
