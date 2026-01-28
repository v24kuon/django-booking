# Code Review（言語/フレームワーク不問）

未コミット差分に対して、セキュリティ/品質レビューを実施する（特定の言語・フレームワーク前提にしない）。

## 前提

- プロジェクトの既存ルール/制約/ツールチェーンに合わせる（新しい前提を勝手に追加しない）
- テスト/静的解析は、リポジトリの標準コマンドがある場合のみ適切なスコープで実行する

## 手順

1. 変更ファイルを取得
- `git diff --name-only HEAD`

2. 変更ファイルごとにレビュー（特に `routes/`, `app/Http/`, `app/Models/`, `database/migrations/`, `resources/views/`）
   - ※ディレクトリ名はプロジェクトにより異なるため、実態に合わせて読み替える

### セキュリティ（CRITICAL）
- **認可漏れ（IDOR）**: show/edit/update/delete でオブジェクト所有者チェックがない（Policy/Gate/authorize不足）
- **入力バリデーション漏れ**: 必須/形式/境界値/NULL/空のチェックが不足、ユーザー入力をそのまま利用
- **Unsafe binding / mass assignment**: ユーザー入力のmap/objectをそのまま永続化層へ渡す
- **Injection**: 文字列連結のクエリ/コマンド、パラメータバインド不足
- **XSS**: エスケープされない出力、ユーザー入力のHTML出力
- **SSRF**: ユーザー指定URLをサーバ側でそのままfetch
- **アップロード**: 拡張子/サイズ/保存先/公開範囲の不備、ファイル名をユーザー入力で決める
- **CSRF**: cookie認証で state-changing をするのに CSRF 対策がない
- **秘密情報の混入**: APIキー/トークン/Stripeキー等のハードコード、ログへの出力

### 品質（HIGH）
- **I/O境界の肥大化**: handler/controller/route層にビジネスロジックが詰まりすぎ
- **例外/エラー処理の不足**: 404/403/409、決済失敗、満席、締切などの失敗系が握りつぶされている
- **DB整合性**: 予約定員/残高/サブスク枠などの不変条件がトランザクション/制約で守られていない
- **N+1/性能劣化**: ループ内クエリ、ページング不足、過剰なI/O
- **デバッグ痕跡**: `print`, `console.log`, `debugger`, `dd()` 等、過剰ログ
- **テスト不足**: 主要happy path + failure path + boundary が不足

### ベストプラクティス（MEDIUM）
- 日時/タイムゾーンの扱いが曖昧
- ページング未実装で一覧が肥大化
- ルート名/ビュー名の不整合（変更に追随できていない）

3. レポートを生成（優先度付き）
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- File:Line（可能なら）
- Issue（何が危険/問題か）
- Fix（プロジェクトの言語/フレームワークに合わせた直し方）

4. 判定
- **CRITICAL または HIGH があれば commit/merge をブロック**（修正が先）

Never approve code with security vulnerabilities.
