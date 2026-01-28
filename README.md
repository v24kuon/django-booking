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
