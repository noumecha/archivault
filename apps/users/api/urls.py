# apps/users/api/urls.py
from django.urls import path
from apps.users.api.views import LoginAPIView, LogoutAPIView

from config.utils.urls import *

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
]
