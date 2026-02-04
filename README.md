# tets

uv を前提にした Python プロジェクト雛形です。

## 前提

- `uv` がインストール済みであること（この環境では `uv 0.8.13` を検出）
- Python は `.python-version`（`3.14.2`）を目安に、必要なら uv で用意します

## セットアップ (pyenv + uv)

1. **Python本体 (pyenv)**
   ```bash
   # プロジェクトで使用する Python を pyenv で指定
   pyenv local 3.14.2
   ```

2. **仮想環境と依存関係 (uv)**
   ```bash
   # pyenv の Python を使って仮想環境を作成
   uv venv

   # 依存関係の同期
   uv sync --all-groups
   ```

## 実行

```bash
export SESSION_SECRET="change-me"
uv run uvicorn app.main:app --reload
```

## Vercel デプロイ（CLI不要）

1. GitHub にリポジトリをプッシュ
2. Vercel ダッシュボードで「Add New…」→「Project」
3. GitHub 連携から対象リポジトリを選択
4. 「Framework Preset」は **Other** を選択
5. 環境変数を設定
   - `SESSION_SECRET`: ランダムな長い文字列
   - `ADMIN_SETUP_TOKEN`: 管理者作成用のトークン（任意の長い文字列）
   - `DATABASE_URL`（任意）: 永続化したい場合は外部DBを指定
6. Deploy

### 注意点
- Vercel ではローカルファイル書き込みが永続化されません。
- 何も設定しない場合、DB は `/tmp/app.db` に作成されます（再デプロイで消えます）。
- 永続化が必要な場合は、PostgreSQL などの外部DBに切り替えて `DATABASE_URL` を設定してください。

### 管理者アカウント作成（Vercel上・CLI不要）

1. Vercel の環境変数 `ADMIN_SETUP_TOKEN` を設定
2. デプロイ後、以下にアクセス
   - `https://<your-domain>/setup/admin`
3. トークン・メール・パスワードを入力して作成
4. 作成後は `ADMIN_SETUP_TOKEN` を削除または別値に変更

## 管理者アカウントの作成

初回起動時に管理者アカウントを作成する場合:

```bash
uv run python scripts/create_admin.py admin@example.com your-password
```

**注意**: パスワードは8文字以上、72バイト以下である必要があります。

## テスト / 静的解析

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## 依存関係の追加

```bash
# ランタイム依存
uv add requests

# 開発依存（dependency group: dev）
uv add --group dev mypy
```
