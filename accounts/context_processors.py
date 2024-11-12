from django.conf import settings

def microsoft_auth_context(request):
    """
    Microsoft Entra IDのユーザー情報をテンプレートに提供するコンテキストプロセッサ
    管理画面アクセス時は通常のDjango認証情報を使用
    """
    # 管理画面へのアクセスかどうかを確認
    if request.path.startswith('/admin/'):
        # 管理画面の場合は空のコンテキストを返す
        # Django標準の auth context_processor が処理する
        return {}

    try:
        # 通常のページアクセス時：セッションからユーザー情報を取得
        user_data = request.session.get('_logged_in_user', {})

        # 必要な情報のみを抽出
        user = {
            'name': user_data.get('name'),
            'preferred_username': user_data.get('preferred_username')
        }
        return {'user': user}

    except Exception as e:
        # エラーが発生した場合は安全な値を返す
        if settings.DEBUG:
            print(f"Error in microsoft_auth_context: {str(e)}")
        return {'user': {}}
