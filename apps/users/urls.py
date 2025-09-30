from django.urls import path
from .views import *

urlpatterns = [
    path('', UserView.as_view(), name='users'),
    path('profile', UserProfileView.as_view(template_name="users/user_profile.html"), name='user_profile'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('users/', UserAPIView.as_view(template_name="user_list.html"), name='api-users'),
    path('groups/', GroupAPIView.as_view(), name='api-groups'),
]