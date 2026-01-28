# Update Documentation（言語/フレームワーク不問）

アプリのドキュメントを、**コード/設定**を唯一の真実として同期する。特定の言語・フレームワーク・ツール（Node/PHP等）に固定せず、プロジェクトの実態に合わせる。

## 前提

- ドキュメント生成/更新は、ユーザーが明示的に依頼した場合にのみ行う（このコマンドはその前提で使用）
- セットアップ手順や環境変数は **テンプレート/例** を書く（秘密情報の値そのものは書かない）

## 手順

1. 依存関係/タスク実行の “唯一の真実” を特定する
   - 例: `package.json` / lock、`pyproject.toml` / `requirements*.txt`、`go.mod`、`Cargo.toml`、`pom.xml`/`build.gradle*`、`composer.json`、`Gemfile` など
   - 実行コマンド（install/test/lint/format/build/dev）をそこから抽出し、ドキュメントに反映する

2. 環境変数テンプレートを読み、一覧に落とす
   - 例: `.env.example`, `.env.sample`, `.env.template`, `.envrc`, `config/*` など
   - **目的 / 必須or任意 / 形式 / 例（ダミー値）** を記述

3. `docs/CONTRIB.md` を生成/更新（推奨）
   - 開発フロー（セットアップ/起動/デバッグ）
   - 主要コマンド（install/test/lint/format/build）
   - コーディング規約（formatter/linter/type-check 等がある場合）

4. `docs/RUNBOOK.md` を生成/更新（推奨）
   - デプロイ手順（環境ごとの前提・依存）
   - ロールバック（直前のリリースへ戻す手順、移行/マイグレーションの扱い）
   - よくある障害（DB接続、権限、設定、キャッシュ等）

5. 陳腐化したドキュメントを列挙
   - `docs/` 配下で 90日以上更新されていないファイルをリストアップし、手動レビュー対象として提示

6. 差分サマリを提示（変更ファイル、変更点の要約）

## コマンド例（README/CONTRIB向け・プロジェクトに合わせて選ぶ）

```bash
# 依存関係
# npm ci / pnpm i --frozen-lockfile / yarn install --frozen-lockfile
# pip install -r requirements.txt / uv sync
# go mod download
# cargo build
# mvn test / ./gradlew test
# dotnet test

# テスト
# npm test / pytest / go test ./... / cargo test / mvn test / dotnet test

# フォーマット/静的解析
# npm run lint / ruff / black / gofmt / golangci-lint / cargo fmt / mvn -DskipTests=false ...
```

## Single source of truth（例）

- 依存/タスク: 上記のマニフェスト/ロックファイル
- 環境変数: `.env.example` 等のテンプレート
- 運用手順: 実際の起動/テスト/デプロイ手順（CI・スクリプト・Makefile等）
