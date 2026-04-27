# apps/administration/api/urls.py
from django.urls import path
from apps.administration.api.views import *

from apps.users.api.views import UserAPIView
from config.utils.urls import *

urlpatterns = [
    # ministeres api urls
    path('ministeres/', MinistereAPIView.as_view(), name='api_ministere_list', kwargs={'action': 'list'}),
    path('ministeres/create', MinistereAPIView.as_view(), name='api_ministere_create', kwargs={'action': 'create'}),
    path('ministeres/<int:pk>/', MinistereAPIView.as_view(), name='api_ministere_detail', kwargs={'action': 'retrieve'}),
    path('ministeres/<int:pk>/update', MinistereAPIView.as_view(), name='api_ministere_update', kwargs={'action': 'update'}),
    path('ministeres/<int:pk>/delete', MinistereAPIView.as_view(), name='api_ministere_delete', kwargs={'action': 'delete'}),
    path('ministeres/bulk-delete/', MinistereAPIView.as_view(), name='api_ministere_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # cellules api urls
    path('cellules/', CelluleAPIView.as_view(), name='api_cellule_list', kwargs={'action': 'list'}),
    path('cellules/create', CelluleAPIView.as_view(), name='api_cellule_create', kwargs={'action': 'create'}),
    path('cellules/<int:pk>/', CelluleAPIView.as_view(), name='api_cellule_detail', kwargs={'action': 'retrieve'}),
    path('cellules/<int:pk>/update', CelluleAPIView.as_view(), name='api_cellule_update', kwargs={'action': 'update'}),
    path('cellules/<int:pk>/delete', CelluleAPIView.as_view(), name='api_cellule_delete', kwargs={'action': 'delete'}),
    path('cellules/bulk-delete/', CelluleAPIView.as_view(), name='api_cellule_bulk_delete', kwargs={'action': 'bulk_delete'}),
    path('cellules/<int:pk>/toggle-accepte-bailleurs/', CelluleAPIView.as_view(), name='api_cellule_accepte_bailleurs', kwargs={'action' : 'toggle_accepte_bailleurs'}),
    path('cellules/toggle-accepte-bailleurs/', CelluleAPIView.as_view(), name='api_cellule_toggle_accepte_bailleurs', kwargs={'action': 'bulk_toggle_accepte_bailleurs'}),
    # directions generales api urls
    path('directiongenerales/', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_list', kwargs={'action': 'list'}),
    path('directiongenerales/create', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_create', kwargs={'action': 'create'}),
    path('directiongenerales/<int:pk>/', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_detail', kwargs={'action': 'retrieve'}),
    path('directiongenerales/<int:pk>/update', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_update', kwargs={'action': 'update'}),
    path('directiongenerales/<int:pk>/delete', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_delete', kwargs={'action': 'delete'}),
    path('directiongenerales/bulk-delete/', DirectionGeneraleAPIView.as_view(), name='api_directiongenerale_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # divisions api urls
    path('divisions/', DivisionAPIView.as_view(), name='api_division_list', kwargs={'action': 'list'}),
    path('divisions/create', DivisionAPIView.as_view(), name='api_division_create', kwargs={'action': 'create'}),
    path('divisions/<int:pk>/', DivisionAPIView.as_view(), name='api_division_detail', kwargs={'action': 'retrieve'}),
    path('divisions/<int:pk>/update', DivisionAPIView.as_view(), name='api_division_update', kwargs={'action': 'update'}),
    path('divisions/<int:pk>/delete', DivisionAPIView.as_view(), name='api_division_delete', kwargs={'action': 'delete'}),
    path('divisions/bulk-delete/', DivisionAPIView.as_view(), name='api_division_bulk_delete', kwargs={'action': 'bulk_delete'}),
    path('divisions/<int:pk>/toggle-status/', DivisionAPIView.as_view(), name='api_division_toggle_status', kwargs={'action' : 'toggle_status'}),
    path('divisions/bulk-toggle-status/', DivisionAPIView.as_view(), name='api_division_bulk_toggle_status', kwargs={'action': 'bulk_toggle_status'}),
]
