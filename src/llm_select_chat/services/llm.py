"""
LLM 呼び出し（Azure OpenAI / Anthropic の振り分けと実行）。
Streamlit に依存せず、例外を投げて呼び出し元で表示する。
"""
import time
from typing import Any

import httpx
from openai import AzureOpenAI
import anthropic

from src.llm_select_chat.services import catalog as _catalog


def _ensure_api_key(model_info: dict) -> str:
    """model_info に api_key が無ければリージョンから取得。"""
    api_key = model_info.get("api_key", "").strip()
    if api_key:
        return api_key
    return _catalog.get_api_key_for_region(model_info.get("region", ""))


def call_llm_chat(
    model_type: str,
    deployment_name: str,
    api_key: str,
    endpoint: str,
    api_version: str,
    messages: list[dict],
    system_message: str | None = None,
    max_tokens: int = 4000,
) -> dict[str, Any]:
    """
    チャット1ターン分のLLM呼び出し。
    戻り値: ai_response, prompt_tokens, completion_tokens, total_tokens,
            finish_reason, response_model, response_id, response_time_seconds
    エラー時は例外を投げる。
    """
    start = time.time()
    if model_type == "anthropic":
        client = anthropic.Anthropic(api_key=api_key, base_url=endpoint)
        msg_list = [m for m in messages if m.get("role") != "system"]
        system = system_message or ""
        if not system and messages and messages[0].get("role") == "system":
            system = messages[0].get("content", "")
        response = client.messages.create(
            model=deployment_name,
            max_tokens=max_tokens,
            system=system,
            messages=msg_list,
        )
        elapsed = time.time() - start
        text = response.content[0].text if response.content else ""
        return {
            "ai_response": text,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "finish_reason": response.stop_reason,
            "response_model": response.model,
            "response_id": response.id,
            "response_time_seconds": round(elapsed, 3),
        }
    else:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            max_completion_tokens=max_tokens,
            temperature=0.7,
        )
        elapsed = time.time() - start
        choice = response.choices[0]
        return {
            "ai_response": (choice.message.content or ""),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "finish_reason": choice.finish_reason,
            "response_model": response.model,
            "response_id": response.id,
            "response_time_seconds": round(elapsed, 3),
        }


def generate_session_name(model_info: dict, conversation_history: list[dict]) -> str | None:
    """
    LLMでセッション名を生成（会話要約から最大20文字）。
    失敗時は例外を投げる。会話が空の場合は None を返す。
    """
    conversation_text = ""
    for msg in conversation_history[:6]:
        if msg.get("role") == "user":
            content = (msg.get("content") or "")[:100]
            conversation_text += f"ユーザー: {content}\n"
        elif msg.get("role") == "assistant":
            content = (msg.get("content") or "")[:100]
            conversation_text += f"AI: {content}\n"
    if not conversation_text.strip():
        return None

    prompt = f"""以下の会話内容を最大20文字で要約し、セッション名として適切なタイトルを生成してください。
タイトルのみを出力してください。記号や絵文字は使わないでください。

会話内容:
{conversation_text}"""

    api_key = _ensure_api_key(model_info)
    model_type = model_info.get("model_type", "openai")
    endpoint = model_info.get("endpoint", "")
    deployment_name = model_info.get("deployment_name", "")
    api_version = model_info.get("api_version", "2024-12-01-preview")

    if model_type == "anthropic":
        client = anthropic.Anthropic(api_key=api_key, base_url=endpoint)
        response = client.messages.create(
            model=deployment_name,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        generated_name = response.content[0].text.strip() if response.content else None
    else:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
            timeout=httpx.Timeout(30.0, connect=10.0),
        )
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=50,
            temperature=0.7,
        )
        generated_name = (
            response.choices[0].message.content.strip() if response.choices and response.choices[0].message else None
        )

    if generated_name and len(generated_name) > 20:
        generated_name = generated_name[:20]
    return generated_name
