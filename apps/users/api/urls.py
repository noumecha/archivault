# apps/users/api/urls.py
from django.urls import path
from apps.users.api.views import LoginAPIView, LogoutAPIView, ProfileAPIView, UserAPIView

from config.utils.urls import *

urlpatterns = [
    # auth api urls
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    # user api urls
    path('users/', UserAPIView.as_view(), name='api_user_list', kwargs={'action': 'list'}),
    path('users/create', UserAPIView.as_view(), name='api_user_create', kwargs={'action': 'create'}),
    path('users/<int:pk>/', UserAPIView.as_view(), name='api_user_detail', kwargs={'action': 'retrieve'}),
    path('users/<int:pk>/update', UserAPIView.as_view(), name='api_user_update', kwargs={'action': 'update'}),
    path('users/<int:pk>/delete', UserAPIView.as_view(), name='api_user_delete', kwargs={'action': 'delete'}),
    path('users/<int:pk>/toggle-status/', UserAPIView.as_view(), name='api_user_toggle_status', kwargs={'action': 'toggle_status'}),
    path('users/bulk-toggle-status/', UserAPIView.as_view(), name='api_user_bulk_toggle_status', kwargs={'action': 'bulk_toggle_status'}),
    path('users/bulk-delete/', UserAPIView.as_view(), name='api_user_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # user profile
    path('users/profile/update/', ProfileAPIView.as_view(), name='api_profile_update', kwargs={'action': 'update_profile'}),
    path('users/profile/change-password/', ProfileAPIView.as_view(), name='api_profile_change_password', kwargs={'action': 'change_password'}),
]
