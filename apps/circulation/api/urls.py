# apps/circulation/api/urls.py
from django.urls import path
from apps.circulation.api.views import *
from config.utils.urls import *

urlpatterns = [
    # Tâches API
    path('taches/', TacheAPIView.as_view(), name='api_tache_list', kwargs={'action': 'list'}),
    path('taches/create/', TacheAPIView.as_view(), name='api_tache_create', kwargs={'action': 'create'}),
    path('taches/<int:pk>/', TacheAPIView.as_view(), name='api_tache_detail', kwargs={'action': 'retrieve'}),
    path('taches/<int:pk>/update/', TacheAPIView.as_view(), name='api_tache_update', kwargs={'action': 'update'}),
    path('taches/<int:pk>/delete/', TacheAPIView.as_view(), name='api_tache_delete', kwargs={'action': 'delete'}),
    path('taches/<int:pk>/commenter/', TacheAPIView.as_view(), name='api_tache_comment', kwargs={'action': 'comment'}),
    path('taches/bulk-delete/', TacheAPIView.as_view(), name='api_tache_bulk_delete', kwargs={'action': 'bulk_delete'}),
]
