# apps/documents/api/urls.py
from django.urls import path
from apps.documents.api.views import *

from config.utils.urls import *

urlpatterns = [
    path('documents/', DocumentAPIView.as_view(), name='api_document_list', kwargs={'action': 'list'}),
    path('documents/create', DocumentAPIView.as_view(), name='api_document_create', kwargs={'action': 'create'}),
    path('documents/upload-multiple/', DocumentAPIView.as_view(), name='api_document_upload_multiple', kwargs={'action': 'upload_multiple'}),
    path('documents/<int:pk>/', DocumentAPIView.as_view(), name='api_document_detail', kwargs={'action': 'retrieve'}),
    path('documents/<int:pk>/update/', DocumentAPIView.as_view(), name='api_document_update', kwargs={'action': 'update'}),
    path('documents/<int:pk>/delete/', DocumentAPIView.as_view(), name='api_document_delete', kwargs={'action': 'delete'}),
    path('documents/bulk-delete/', DocumentAPIView.as_view(), name='api_document_bulk_delete', kwargs={'action': 'bulk_delete'}),
    path('documents/check-conflict/', DocumentAPIView.as_view(), name='api_document_check_conflict', kwargs={'action': 'check_conflict'}),
    path('documents/<int:pk>/add-tache/', DocumentAPIView.as_view(), name='api_document_add_tache', kwargs={'action': 'add_tache'}),
    path('documents/<int:pk>/add-circulation/', DocumentAPIView.as_view(), name='api_document_add_circulation', kwargs={'action': 'add_circulation'}),
    # urls for themes
    path('themes/', ThemeAPIView.as_view(), name='api_theme_list', kwargs={'action': 'list'}),
    path('themes/create', ThemeAPIView.as_view(), name='api_theme_create', kwargs={'action': 'create'}),
    path('themes/<int:pk>/', ThemeAPIView.as_view(), name='api_theme_detail', kwargs={'action': 'retrieve'}),
    path('themes/<int:pk>/update', ThemeAPIView.as_view(), name='api_theme_update', kwargs={'action': 'update'}),
    path('themes/<int:pk>/delete', ThemeAPIView.as_view(), name='api_theme_delete', kwargs={'action': 'delete'}),
    path('themes/bulk-delete/', ThemeAPIView.as_view(), name='api_theme_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # urls for typedocuments
    path('typedocuments/', TypeDocumentAPIView.as_view(), name='api_typedocument_list', kwargs={'action': 'list'}),
    path('typedocuments/create', TypeDocumentAPIView.as_view(), name='api_typedocument_create', kwargs={'action': 'create'}),
    path('typedocuments/<int:pk>/', TypeDocumentAPIView.as_view(), name='api_typedocument_detail', kwargs={'action': 'retrieve'}),
    path('typedocuments/<int:pk>/update', TypeDocumentAPIView.as_view(), name='api_typedocument_update', kwargs={'action': 'update'}),
    path('typedocuments/<int:pk>/delete', TypeDocumentAPIView.as_view(), name='api_typedocument_delete', kwargs={'action': 'delete'}),
    path('typedocuments/bulk-delete/', TypeDocumentAPIView.as_view(), name='api_typedocument_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # urls for soustypedocuments
    path('soustypedocuments/', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_list', kwargs={'action': 'list'}),
    path('soustypedocuments/create', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_create', kwargs={'action': 'create'}),
    path('soustypedocuments/<int:pk>/', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_detail', kwargs={'action': 'retrieve'}),
    path('soustypedocuments/<int:pk>/update', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_update', kwargs={'action': 'update'}),
    path('soustypedocuments/<int:pk>/delete', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_delete', kwargs={'action': 'delete'}),
    path('soustypedocuments/bulk-delete/', SousTypeDocumentAPIView.as_view(), name='api_soustypedocument_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # urls for avenants
    path('avenants/', AvenantAPIView.as_view(), name='api_avenant_list', kwargs={'action': 'list'}),
    path('avenants/create', AvenantAPIView.as_view(), name='api_avenant_create', kwargs={'action': 'create'}),
    path('avenants/<int:pk>/', AvenantAPIView.as_view(), name='api_avenant_detail', kwargs={'action': 'retrieve'}),
    path('avenants/<int:pk>/update', AvenantAPIView.as_view(), name='api_avenant_update', kwargs={'action': 'update'}),
    path('avenants/<int:pk>/delete', AvenantAPIView.as_view(), name='api_avenant_delete', kwargs={'action': 'delete'}),
    path('avenants/bulk-delete/', AvenantAPIView.as_view(), name='api_avenant_bulk_delete', kwargs={'action': 'bulk_delete'}),
    # urls for bailleurs
    path('bailleurs/', BailleurAPIView.as_view(), name='api_bailleur_list', kwargs={'action': 'list'}),
    path('bailleurs/create', BailleurAPIView.as_view(), name='api_bailleur_create', kwargs={'action': 'create'}),
    path('bailleurs/<int:pk>/', BailleurAPIView.as_view(), name='api_bailleur_detail', kwargs={'action': 'retrieve'}),
    path('bailleurs/<int:pk>/update', BailleurAPIView.as_view(), name='api_bailleur_update', kwargs={'action': 'update'}),
    path('bailleurs/<int:pk>/delete', BailleurAPIView.as_view(), name='api_bailleur_delete', kwargs={'action': 'delete'}),
    path('bailleurs/bulk-delete/', BailleurAPIView.as_view(), name='api_bailleur_bulk_delete', kwargs={'action': 'bulk_delete'}),
]
