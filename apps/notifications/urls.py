from django.urls import path, include
from .web import views

urlpatterns = [
    path('notifications/list', views.NotificationManagementView.as_view(), name='notification_list'),
    # api views
    path('api/', include('apps.notifications.api.urls')),
]
