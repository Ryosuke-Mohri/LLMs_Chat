# LLM Select Chat

Azure OpenAI および Anthropic（Claude）など、複数リージョン・複数モデルを切り替えながら利用できるチャットアプリです。Streamlit でフロントエンドを構築し、会話はセッション単位で保存され、メトリクス（トークン数・コスト・応答時間）を表示します。

---

## 主な機能

- **複数モデル対応**: 起動時に `config/deployment_models.json` で定義したデプロイ一覧からモデルを選択。Azure OpenAI（GPT 系）と Anthropic（Claude 系）の両方に対応。
- **複数リージョン**: Japan East / East US2 など、環境変数で指定したリージョンごとに API Key とエンドポイントを切り替え。
- **セッション管理**: 会話はセッション単位で保持。左サイドバーから「新規セッション」作成、既存セッションの選択・再開が可能。セッションごとにモデルは固定（途中変更不可）。
- **セッション名**: 手動で変更可能。オプションで LLM による自動要約タイトル生成に対応。
- **メトリクス表示**: ターン数、総トークン数、コスト（USD/JPY）、平均応答時間をセッションごとに表示。為替レートは環境変数 `USD_TO_JPY` で指定。
- **ライト/ダークテーマ**: アプリ内トグルで切り替え。配色は `lib/themes.py` の `THEMES` と `assets/css/app.css` で管理。
- **会話ログ**: すべての会話とメタデータは `data/chat_log.json`（パスは `LOG_FILE_PATH` で変更可）に JSON で記録。削除は論理削除（ゴミ箱）→ 完全削除の 2 段階。

---

## 技術スタック

- **フロント**: Streamlit（Python）
- **API**: OpenAI Python SDK（Azure OpenAI）, Anthropic Python SDK（Claude）
- **その他**: httpx, python-dotenv

表示まわりの HTML / CSS / JavaScript は `assets/` と `lib` の loader（`css_loader`, `html_loader`, `js_loader`）で分離して管理しています。

---

## プロジェクト構成

```
LLMs_Chat/
├── streamlit_app.py      # エントリポイント（Streamlit アプリ本体）
├── requirements.txt      # Python 依存
├── .env.example          # 環境変数テンプレート（.env は git 管理外）
├── verify_loaders.py     # 開発用: 全 loader の読み込み検証
├── .streamlit/
│   └── config.toml      # Streamlit 設定（テーマ・ツールバー等）
├── assets/               # 静的アセット（CSS / HTML / JS）
│   ├── css/
│   │   └── app.css      # アプリ全体のスタイル（テーマ変数は {{key}} で置換）
│   ├── html/            # HTML フラグメント（会話表示・ナビ・マーカー等）
│   └── js/              # Popover 閉じ・危険ボタン用など
├── lib/                  # Python ライブラリ
│   ├── themes.py        # テーマ配色辞書 THEMES
│   ├── css_loader.py     # assets/css 読み込み・テーマ置換
│   ├── html_loader.py    # assets/html 読み込み・プレースホルダ置換
│   ├── js_loader.py      # assets/js 読み込み
│   └── logger.py        # ログ設定
├── config/               # モデル定義（git 管理外を想定）
│   └── deployment_models.json
├── data/                 # 会話ログ（git 管理外）
│   └── chat_log.json
└── logs/                 # アプリログ（任意・git 管理外）
```

- **config/**: デプロイ名・リージョン・表示名・sort_order などを定義。リポジトリに含めない場合は `.env.example` の説明に従い手元で用意。
- **data/**: 会話ログの保存先。`.gitignore` で無視。
- **assets/ と lib/**: 追跡対象。`.gitignore` で `lib/` は標準の無視ルールのあと `!lib/` で復元。

---

## セットアップ

### 1. リポジトリのクローンと依存関係

```bash
git clone <repo_url>
cd LLMs_Chat
pip install -r requirements.txt
```

### 2. 環境変数

`.env.example` をコピーして `.env` を作成し、API Key とエンドポイントを設定します。

```bash
cp .env.example .env
# .env を編集して各リージョンの AZURE_OPENAI_*_API_KEY, *_ENDPOINT を設定
```

主な項目:

| 変数名 | 説明 |
|--------|------|
| `AZURE_OPENAI_JAPAN_EAST_API_KEY` | Japan East の API Key |
| `AZURE_OPENAI_JAPAN_EAST_ENDPOINT` | Japan East のエンドポイント URL |
| `AZURE_OPENAI_EAST_US2_*` | East US2 用（Anthropic 用は `*_ANTHROPIC_ENDPOINT`） |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API バージョン（既定: 2024-12-01-preview） |
| `USD_TO_JPY` | 為替レート（コスト表示用、既定: 150） |
| `LOG_FILE_PATH` | 会話ログ JSON のパス（既定: data/chat_log.json） |
| `LOG_LEVEL` | ログレベル（DEBUG / INFO / WARNING / ERROR） |

### 3. モデル定義（config/deployment_models.json）

`config/` は `.gitignore` で無視されるため、手元で `config/deployment_models.json` を用意します。  
各デプロイを次のようなオブジェクトの配列で定義します。

- **必須**: `deployment_name`, `region`（環境変数のリージョン名と一致）
- **推奨**: `display_name`, `provider`, `sort_order`
- **任意**: `release_date`, `capability_tag`, `recommended_usage` など

`region` は `REGIONS` に存在するキー（例: `"Japan East"`, `"East US2"`）である必要があります。  
Anthropic モデルは East US2 用に `AZURE_OPENAI_EAST_US2_ANTHROPIC_ENDPOINT` を設定します。

### 4. Streamlit 設定（.streamlit/config.toml）

プロジェクトにはすでに次の設定があります。

- **theme**: `base = "light"`, `primaryColor = "#2e7d32"`
- **client**: `toolbarMode = "minimal"`（右上メニューを最小限に）

必要に応じて編集してください。

---

## 起動方法

プロジェクトルートで次を実行します。

```bash
streamlit run streamlit_app.py
```

ブラウザで開き、左サイドバーから「新規セッション」でモデルを選び、メインエリアでプロンプトを入力して送信します。

---

## データの流れ

- **会話ログ**: `load_log_data()` / `save_log_data()` で `LOG_FILE_PATH` の JSON を読み書き。セッションの作成・更新・削除（論理削除・完全削除）はすべてこのファイルに反映されます。
- **モデル一覧**: `get_all_models()` が `config/deployment_models.json` を読み、`REGIONS` と突き合わせて利用可能なモデルリストを組み立てます。`sort_order` 昇順で表示されます。
- **テーマ**: `st.session_state.app_theme` が `"light"` / `"dark"` を保持。`get_app_css(theme_name, font_zoom)` が `assets/css/app.css` をテーマ変数で置換し、ページに注入します。

---

## 開発時確認（分離後セットで確認）

HTML / CSS / JS を `assets/` と `lib` の loader で分離しているため、アセットや loader を変更したあとは、次で全 loader が正常に読み込めることを確認するとよいです。

```bash
python verify_loaders.py
```

- 成功時: `OK: all loaders verified.` と表示されます。
- 失敗時: どの loader でエラーになったかが表示されます（ファイル不在・プレースホルダ未置換など）。

---

## ライセンス・注意事項

- API Key やエンドポイントは `.env` に記載し、`.env` はリポジトリにコミットしないでください。
- `config/` に機密を含めない場合は、必要に応じてサンプルの `deployment_models.json` をリポジトリに含める運用も可能です。
- 本 README はプロジェクトの現状を俯瞰した説明です。細かい仕様は `streamlit_app.py` および `lib/` のソースを参照してください。
