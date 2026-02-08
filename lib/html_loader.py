"""
HTML アセット読み込み・プレースホルダ置換
assets/html/*.html を読み込み、{{key}} を置換して返す。

ルール（パラメータ名の衝突防止）:
  _replace_placeholders の第1引数（テンプレート文字列を受け取る引数）の名前は、
  いずれの HTML テンプレートのプレースホルダ名とも一致させないこと。
  例: template, html_source など専用名に限定する。過去に content とすると
  {{content}} を持つテンプレートで「複数代入」TypeError が発生した。

テンプレート vs 引数 対応表（変更時はここも更新すること）:
  marker_div.html     -> {{class_name}}           -> get_marker_div_html(class_name=)
  page_anchor.html    -> {{id}}                   -> get_page_anchor_html(id_attr=)  # kwargs: id=
  model_badge.html    -> provider_icon, model_display_name, region_display, provider
  user_message.html   -> timestamp_str, content    -> get_user_message_html
  ai_message.html     -> ai_metrics_color, metrics_str, content
  nav_bottom.html     -> nav_bottom_bg, nav_text
  nav_top.html        -> nav_top_bg, nav_text
  copy_button_block.html -> msg_id, copy_btn_bg, copy_btn_text, copy_btn_copied_bg,
                            copy_btn_copied_text, escaped_content
"""

from pathlib import Path


def _assets_dir() -> Path:
    """プロジェクトルートの assets ディレクトリ"""
    return Path(__file__).resolve().parent.parent / "assets"


def _read_html(name: str) -> str:
    """HTML フラグメントを読み込む"""
    path = _assets_dir() / "html" / f"{name}.html"
    return path.read_text(encoding="utf-8")


def _replace_placeholders(template: str, **kwargs) -> str:
    """{{key}} を kwargs の値で置換する。値は文字列に変換。
    注意: 第1引数名はどのテンプレートのプレースホルダ名とも一致させないこと（衝突で TypeError）。"""
    for key, value in kwargs.items():
        placeholder = f"{{{{{key}}}}}"
        template = template.replace(placeholder, str(value))
    return template


def get_loading_overlay_html() -> str:
    """LLM処理中オーバーレイ用 HTML"""
    return _read_html("loading_overlay").strip()


def get_sidebar_title_html() -> str:
    """サイドバータイトル用 HTML"""
    return _read_html("sidebar_title").strip()


def get_marker_div_html(class_name: str) -> str:
    """マーカー用 div（danger-btn-marker, trash-button-marker, active-session-marker, completed-session-marker）"""
    return _replace_placeholders(_read_html("marker_div").strip(), class_name=class_name)


def get_page_anchor_html(id_attr: str) -> str:
    """ページアンカー用 div（page-top, page-bottom）"""
    return _replace_placeholders(_read_html("page_anchor").strip(), id=id_attr)


def get_model_badge_html(*, provider_icon: str, model_display_name: str, region_display: str, provider: str) -> str:
    """モデルバッジ用 HTML"""
    return _replace_placeholders(
        _read_html("model_badge").strip(),
        provider_icon=provider_icon,
        model_display_name=model_display_name,
        region_display=region_display,
        provider=provider,
    )


def get_user_message_html(*, timestamp_str: str, content: str) -> str:
    """ユーザーメッセージ用 HTML"""
    return _replace_placeholders(
        _read_html("user_message").strip(),
        timestamp_str=timestamp_str,
        content=content,
    )


def get_ai_message_html(*, ai_metrics_color: str, metrics_str: str, content: str) -> str:
    """AIメッセージ用 HTML"""
    return _replace_placeholders(
        _read_html("ai_message").strip(),
        ai_metrics_color=ai_metrics_color,
        metrics_str=metrics_str,
        content=content,
    )


def get_nav_bottom_html(*, nav_bottom_bg: str, nav_text: str) -> str:
    """「最下部へ」ナビ用 HTML"""
    return _replace_placeholders(
        _read_html("nav_bottom").strip(),
        nav_bottom_bg=nav_bottom_bg,
        nav_text=nav_text,
    )


def get_nav_top_html(*, nav_top_bg: str, nav_text: str) -> str:
    """「最上部へ」ナビ + page-bottom 用 HTML"""
    return _replace_placeholders(
        _read_html("nav_top").strip(),
        nav_top_bg=nav_top_bg,
        nav_text=nav_text,
    )


def get_copy_button_block_html(
    *,
    msg_id: str,
    copy_btn_bg: str,
    copy_btn_text: str,
    copy_btn_copied_bg: str,
    copy_btn_copied_text: str,
    escaped_content: str,
) -> str:
    """コピーボタン（HTML+JS）ブロック用。components.html に渡す用。"""
    return _replace_placeholders(
        _read_html("copy_button_block").strip(),
        msg_id=msg_id,
        copy_btn_bg=copy_btn_bg,
        copy_btn_text=copy_btn_text,
        copy_btn_copied_bg=copy_btn_copied_bg,
        copy_btn_copied_text=copy_btn_copied_text,
        escaped_content=escaped_content,
    )
