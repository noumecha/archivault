# apps/circulation/urls.py
from django.urls import include, path
from .web import views

urlpatterns = [
    # Circulation
    path('', views.CirculationView.as_view(), name='circulation'),
    path('circulations/', views.CirculationView.as_view(), name='circulation_list'),
    path('circulations/<int:pk>/', views.CirculationDetailView.as_view(), name='circulation_detail'),
    path('circulations/create/<int:document_pk>/', views.CirculationCreateView.as_view(), name='circulation_create'),
    path('etapes/<int:etape_pk>/traiter/', views.etape_traiter, name='etape_traiter'),

    # Tâches - Exécution (mes tâches)
    path('taches/detail/<int:pk>/', views.TacheDetailView.as_view(), name='tache_detail'),
    path('taches-management/', views.TacheManagementView.as_view(), name='tache_management'),

    # Audit
    path('audit/', views.AuditLogListView.as_view(), name='audit_log_list'),
    # api views
    path('api/', include('apps.circulation.api.urls')),
]
