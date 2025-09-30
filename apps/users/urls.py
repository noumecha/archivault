from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='users'),
    path('profile', views.UserProfileView.as_view(), name='user_profile'),
    path('login/', views.LoginAPIView.as_view(), name='api-login'),
    path('logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('users/', views.UserAPIView.as_view(), name='api-users'),
    path('groups/', views.GroupAPIView.as_view(), name='api-groups'),
    #path('login', views.LoginView.as_view(), name='login'),
    #path('logout', views.LogoutView.as_view(), name='logout'),
]