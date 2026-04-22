# apps/users/urls.py
from django.urls import include, path
from .web.views import *
from .api.views import *
from config.utils.urls import *

urlpatterns = [
    *get_crud_urls(UserView, "utilisateur/utilisateurs", "utilisateur"),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/password/', UserPasswordView.as_view(), name='user_password_update'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('groups/', GroupAPIView.as_view(), name='api-groups'),
    path('api/', include('apps.users.api.urls')),
]
