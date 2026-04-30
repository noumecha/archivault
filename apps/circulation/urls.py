# apps/circulation/urls.py
from django.urls import include, path
from .web import views

urlpatterns = [
    # Circulation
    path('circulations/', views.CirculationManagementView.as_view(), name='circulation_list'),
    path('circulations/detail/<int:pk>/', views.CirculationDetailView.as_view(), name='circulation_detail'),

    # Tâches - Exécution (mes tâches)
    path('taches/detail/<int:pk>/', views.TacheDetailView.as_view(), name='tache_detail'),
    path('taches-management/', views.TacheManagementView.as_view(), name='tache_management'),

    # Audit
    path('audit/', views.AuditLogListView.as_view(), name='audit_log_list'),
    # api views
    path('api/', include('apps.circulation.api.urls')),
]
