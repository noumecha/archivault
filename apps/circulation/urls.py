# apps/circulation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Circulation
    path('', views.CirculationView.as_view(), name='circulation'),
    path('circulations/', views.CirculationView.as_view(), name='circulation_list'),
    path('circulations/<int:pk>/', views.CirculationDetailView.as_view(), name='circulation_detail'),
    path('circulations/create/<int:document_pk>/', views.CirculationCreateView.as_view(), name='circulation_create'),
    path('etapes/<int:etape_pk>/traiter/', views.etape_traiter, name='etape_traiter'),

    # Tâches - Exécution (mes tâches)
    path('taches/', views.TacheView.as_view(), name='tache_list'),
    path('taches/<int:pk>/', views.TacheDetailView.as_view(), name='tache_detail'),
    path('taches/<int:pk>/update/', views.tache_update, name='tache_update'),
    path('taches/<int:pk>/commenter/', views.tache_commenter, name='tache_commenter'),

    # Tâches - Gestion (assignation)
    path('taches-management/', views.TacheManagementView.as_view(), name='tache_management'),
    path('taches/create/', views.TacheCreateView.as_view(), name='tache_create'),
    path('taches/create/<int:document_pk>/', views.TacheCreateFromDocumentView.as_view(), name='tache_create_from_document'),

    # Audit
    path('audit/', views.AuditLogListView.as_view(), name='audit_log_list'),
]
