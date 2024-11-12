from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    """
    管理サイト用のユーザー管理画面設定
    """
    list_display = ['username', 'is_superuser']
    list_filter = ['is_superuser']
    search_fields = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('権限'), {'fields': ('is_superuser',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_superuser'),
        }),
    )

    ordering = ['username']

# 管理サイトにスーパーユーザーモデルを登録
admin.site.register(User, CustomUserAdmin)
