# Update Codemaps（言語/フレームワーク不問）

リポジトリの実態（エントリポイント/モジュール/API/データ層/統合）から、**コードマップ（CODEMAPS）**を更新する。

## 前提

- 特定の言語・フレームワーク・ツールチェーンに固定しない（リポジトリの実態に合わせる）
- CODEMAPは **高レベル構造**に絞り、実装詳細の羅列は避ける

## 手順

1. リポジトリ構造をスキャン
   - エントリポイント（例: `main.*`, `src/`, `app/`, `cmd/`, `server/` 等）
   - API/ルーティング定義（Web/APIアプリの場合）
   - ドメイン/ユースケース層（存在する場合）
   - データ層（ORM/DAO/SQL/マイグレーション/DDL）
   - 非同期処理（jobs/workers/cron）
   - UI（templates/components/pages 等、実態に合わせる）
   - 依存関係（manifest + lock: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle*`, `composer.json`, `Gemfile` 等）

2. “外部から見える表面” を把握（可能なら）
   - ルート/エンドポイント/CLIコマンドの一覧を整理
   - フレームワークに一覧コマンドがある場合のみ利用（例: route list / endpoint list 相当）

3. CODEMAP出力（推奨）
   - `docs/CODEMAPS/INDEX.md`
   - `docs/CODEMAPS/surfaces.md`（routes/endpoints/commands）
   - `docs/CODEMAPS/modules.md`（主要モジュール/責務）
   - `docs/CODEMAPS/data.md`（schema/migrations/DDL）
   - `docs/CODEMAPS/ui.md`（UIがある場合）
   - `docs/CODEMAPS/jobs.md`（非同期がある場合）
   - `docs/CODEMAPS/integrations.md`

4. 差分の大きさを計算
   - 既存のCODEMAPと比較し、変更率を算出（概算でOK）
   - **変更率が30%を超える場合は、更新前にユーザー承認を要求**

5. 各CODEMAPに freshness timestamp（更新日）を入れる

6. レポートを保存
   - `.reports/codemap-diff.txt` に差分サマリ（変更率、主な変更点）を出す

## チェック観点

- 表面（routes/endpoints/commands）が実態と一致しているか
- 認可（roles/ACL/policy/middleware 等）をマップに明示できているか（該当する場合）
- DBは schema/migrations/DDL を唯一の真実として整理できているか
- “既存のツール/制約” と矛盾する手順を混ぜていないか
