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
    path('taches/<int:pk>/log-consultation/', TacheAPIView.as_view(), name='api_tache_log_consultation', kwargs={'action': 'log_consultation'}),

    # ─── Circulations API ────────────────────────────────────────────────────
    path('circulations/', CirculationAPIView.as_view(), name='api_circulation_list', kwargs={'action': 'list'}),
    path('circulations/create/', CirculationAPIView.as_view(), name='api_circulation_create', kwargs={'action': 'create'}),
    path('circulations/<int:pk>/', CirculationAPIView.as_view(), name='api_circulation_detail', kwargs={'action': 'retrieve'}),
    path('circulations/<int:pk>/update/', CirculationAPIView.as_view(), name='api_circulation_update', kwargs={'action': 'update'}),
    path('circulations/<int:pk>/delete/', CirculationAPIView.as_view(), name='api_circulation_delete', kwargs={'action': 'delete'}),
    path('circulations/bulk-delete/', CirculationAPIView.as_view(), name='api_circulation_bulk_delete', kwargs={'action': 'bulk_delete'}),
    path('circulations/<int:pk>/log-consultation/', CirculationAPIView.as_view(), name='api_circulation_log_consultation', kwargs={'action': 'log_consultation'}),

    # Actions Spécifiques au Workflow
    path('circulations/initier/', CirculationAPIView.as_view(), name='api_circulation_initier', kwargs={'action': 'initier_circuit'}),
    path('circulations/<int:pk>/traiter/', CirculationAPIView.as_view(), name='api_circulation_traiter', kwargs={'action': 'traiter_etape'}),
]
