# =============================================================================
# LLM Select Chat - エントリポイント（プロジェクトルート配置）
# =============================================================================
#
# 実行コマンド（プロジェクトルートで）:
#   streamlit run streamlit_app.py
#
# 動作確認チェックリスト（最低限）:
#   [ ] streamlit run streamlit_app.py でエラーなく起動する
#   [ ] ページタイトル・サイドバー「LLM Select Chat」が表示される
#   [ ] 新規セッションでモデル一覧（Japan East / East US2）が表示される
#   [ ] モデルを選び「チャットを開始」でセッションが作成される
#   [ ] プロンプト送信で応答が返り、メトリクスが更新される
#   [ ] data/llm_select_chat_log.json にセッションが保存される
#   [ ] 再起動後、サイドバーからセッションを選ぶと会話が復元される
#
# 設定:
#   .env をルートに用意し、.env.example を参考にキーを設定すること。
#   python-dotenv を入れると .env を自動読込。未導入時は環境変数で指定。
# =============================================================================

import streamlit as st

# import は set_page_config より前に行う（app_main のトップレベルでは st を呼ばない）
from src.llm_select_chat.app_main import run_app

# set_page_config はメインスクリプトで「最初の st 呼び出し」である必要がある
st.set_page_config(
    page_title="LLM Select Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    run_app()
except Exception as e:
    st.error(f"アプリ実行エラー: {type(e).__name__}: {e}")
    st.exception(e)
