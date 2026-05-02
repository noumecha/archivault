# apps/notifications/api/urls.py
from django.urls import path
from .views import NotificationAPIView

urlpatterns = [
    # Liste et base
    path('notifications/', NotificationAPIView.as_view(), kwargs={'action': 'list'}, name='api_notification_list'),
    # Actions sur une notification spécifique
    path('notifications/<int:pk>/read/', NotificationAPIView.as_view(), kwargs = {'action': 'mark_as_read'}, name='api_notification_read'),
    path('notifications/<int:pk>/delete/', NotificationAPIView.as_view(), kwargs = {'action': 'delete'}, name='api_notification_delete'),
    path('notifications/bulk-delete/', NotificationAPIView.as_view(), kwargs = {'action': 'bulk_delete'}, name='api_notification_bulk_delete'),

    # Actions globales
    path('notifications/read-all/', NotificationAPIView.as_view(), kwargs = {'action': 'mark_all_as_read'}, name='api_notification_read_all'),
    path('notifications/unread-count/', NotificationAPIView.as_view(), kwargs = {'action': 'unread_count'}, name='api_notification_unread_count'),
]
