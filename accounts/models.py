from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    スーパーユーザー作成のみを行うカスタムマネージャー
    """
    def create_superuser(self, username, password=None, **extra_fields):
        """
        スーパーユーザーを作成する

        Args:
            username: ユーザー名
            password: パスワード
            extra_fields: その他のフィールド
        """
        if not username:
            raise ValueError("ユーザー名は必須です")

        user = self.model(
            username=username,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    管理サイト用のスーパーユーザーモデル
    Microsoft Entra IDのユーザーはDBに保存しない
    """
    username = models.CharField(
        _("ユーザー名"),
        max_length=150,
        unique=True,
    )
    is_staff = models.BooleanField(
        _("管理者権限"),
        default=False,
    )
    is_superuser = models.BooleanField(
        _("スーパーユーザー権限"),
        default=False,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("管理ユーザー")
        verbose_name_plural = _("管理ユーザー")
