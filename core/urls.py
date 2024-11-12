from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('room/<int:pk>/', views.RoomView.as_view(), name='room'),
]
