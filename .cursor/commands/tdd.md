---
description: 言語/フレームワーク不問でTDD（テスト観点表→RED→GREEN→REFACTOR）を強制します。
argument-hint: [what to build]
---

# /tdd（言語/フレームワーク不問）

このコマンドは **tdd-guide** を前提に、テストファーストで実装を進めます（プロジェクトの言語/テストランナーに合わせて運用）。

## 前提
- プロジェクトルールにより、テスト作業開始時は **テスト観点表（Markdown）** と **Given/When/Then コメント**が必須。

## このコマンドがやること
1. **テスト観点表**を作る（正常系/異常系/境界値）
2. 先に **失敗するテスト（RED）** を書く（Feature/Unit）
3. プロジェクトのテストコマンドで **失敗を確認**
4. 最小実装（GREEN）
5. 再実行して **成功を確認**
6. リファクタ（REFACTOR）＋再実行
7. （任意）カバレッジ確認（環境が対応している場合）

## 使いどころ
- 新機能追加（予約/決済/残高/サブスク付与など）
- バグ修正（再現テスト→修正）
- リファクタ（挙動維持をテストで担保）

## コマンド例（置き換え）
```bash
# 最小スコープで実行（例）
# pytest path/to/test_file.py -q
# go test ./... -run TestName
# cargo test test_name
# mvn -Dtest=SomeTest test
# dotnet test --filter FullyQualifiedName~TestName
# npm test -- path/to/test

# カバレッジ（例）
# pytest --cov
# go test -cover ./...
# dotnet test /p:CollectCoverage=true
# npm test -- --coverage
```

## チェック観点（汎用）
- **認可**: オブジェクト単位の認可が抜けていないか（IDOR防止）
- **バリデーション**: 入力チェックが散らばらず一貫しているか
- **DB整合性**: 不変条件がトランザクション/制約で守られているか
- **失敗系**: 403/404/409、競合、外部API失敗、二重送信など
- **境界値**: 0/最小/最大/±1/空/NULL（意味がある範囲で）

## 関連
- レビュー: `/code-review`
- カバレッジ: `/test-coverage`
