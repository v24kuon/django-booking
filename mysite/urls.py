from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    settings.AUTH.urlpattern,
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
]
