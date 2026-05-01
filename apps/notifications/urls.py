from django.urls import path
from .web import views

urlpatterns = [
    path('', views.NotificationView.as_view(), name='notification_list'),
]
