"""ユーティリティ関数"""

# イベントステータスの日本語ラベル
EVENT_STATUS_LABELS = {
    "draft": "下書き",
    "pending_review": "審査待ち",
    "open": "公開中",
    "closed": "終了",
}

# 応募ステータスの日本語ラベル
APPLICATION_STATUS_LABELS = {
    "pending": "審査待ち",
    "approved": "承認済み",
    "rejected": "否認",
    "cancelled": "キャンセル済み",
}

# 通報ステータスの日本語ラベル
REPORT_STATUS_LABELS = {
    "open": "対応中",
    "closed": "対応済み",
    "resolved": "解決済み",
}

# プロフィール審査ステータスの日本語ラベル
PROFILE_REVIEW_STATUS_LABELS = {
    "pending": "審査待ち",
    "approved": "承認済み",
    "rejected": "否認",
}


def get_event_status_label(status: str) -> str:
    """イベントステータスを日本語に変換"""
    return EVENT_STATUS_LABELS.get(status, status)


def get_application_status_label(status: str) -> str:
    """応募ステータスを日本語に変換"""
    return APPLICATION_STATUS_LABELS.get(status, status)


def get_report_status_label(status: str) -> str:
    """通報ステータスを日本語に変換"""
    return REPORT_STATUS_LABELS.get(status, status)


def get_profile_review_status_label(status: str) -> str:
    """プロフィール審査ステータスを日本語に変換"""
    return PROFILE_REVIEW_STATUS_LABELS.get(status, status)
