from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('', views.CirculationView.as_view(), name='circulation'),
    # Circulation
    path('circulations/', views.circulation_list, name='circulation_list'),
    path('circulations/<int:pk>/', views.circulation_detail, name='circulation_detail'),
    path('circulations/create/<int:document_pk>/', views.circulation_create, name='circulation_create'),
    path('etapes/<int:etape_pk>/traiter/', views.etape_traiter, name='etape_traiter'),

    # Tâches
    path('taches/', views.tache_list, name='tache_list'),
    path('taches/<int:pk>/', views.tache_detail, name='tache_detail'),
    path('taches/create/<int:document_pk>/', views.tache_create, name='tache_create'),
    path('taches/<int:pk>/update/', views.tache_update, name='tache_update'),
    path('taches/<int:pk>/commenter/', views.tache_commenter, name='tache_commenter'),

    # Audit
    path('audit/', views.audit_log_list, name='audit_log_list'),
]
