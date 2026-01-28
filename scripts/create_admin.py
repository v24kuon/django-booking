#!/usr/bin/env python3
"""管理者アカウント作成スクリプト

使用方法:
    uv run python scripts/create_admin.py <email> <password>
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db import get_session
from app.repositories.user_repo import get_user_by_email
from app.security import hash_password
from app.services.auth_service import register_user


def main() -> None:
    if len(sys.argv) != 3:
        print("使用方法: uv run python scripts/create_admin.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    session = get_session()
    try:
        # 既存ユーザーをチェック
        existing = get_user_by_email(session, email)
        if existing:
            print(f"エラー: メールアドレス '{email}' は既に登録されています。")
            sys.exit(1)

        # 管理者アカウントを作成
        user = register_user(session, email, password, role="admin", allow_admin=True)
        print(f"管理者アカウントを作成しました:")
        print(f"  メールアドレス: {user.email}")
        print(f"  ロール: {user.role}")
        print(f"  ユーザーID: {user.id}")
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
