from django.urls import path
from .views.views import *
from .views.api_views import *
from config.utils.urls import *

urlpatterns = [
    *get_crud_urls(TypeDocumentView, "typedocument/typedocuments", "typedocument"),
    *get_crud_urls(SousTypeDocumentView, "soustypedocument/soustypedocuments", "soustypedocument"),
    *get_crud_urls(DocumentView, "document/documents", "document"),
    *get_crud_urls(NiveauAccesDocumentView, "niveauaccess/niveauaccesss", "niveauaccess"),
    *get_crud_urls(ThemeListView, "theme/themes", "themes"),
    *get_crud_urls(BailleursView, "bailleur/bailleurs", "bailleurs"),
    *get_crud_urls(AvenantsView, "avenant/avenants", "avenants"),
    *get_crud_urls(DocumentView, "document/documents", "documents"),
    # documents
    path('document/details/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('document/upload/', DocumentCreateMultipleView.as_view(), name='upload_page'),
    path('document/api/upload/', DocumentUploadAPIView.as_view(), name='upload_document'),
    path('document/documents/list/', DocumentListView.as_view(), name='list_document'),
    path('document/edit/<int:pk>/', DocumentUpdateView.as_view(), name='edit_document'),
    path('document/delete/<int:pk>/', DocumentDeleteView.as_view(), name='delete_document'),
    # autocomplete
    path('typedocument/autocomplete/', TypeDocumentAutocomplete.as_view(), name='typedocument_autocomplete'),
    path('soustypedocument/autocomplete/', SousTypeDocumentAutocomplete.as_view(), name='soustypedocument_autocomplete'),
    path('document/autocomplete/', DocumentAutocomplete.as_view(), name='document_autocomplete'),
    path('bailleur/autocomplete/', BailleurAutocomplete.as_view(), name='bailleur_autocomplete'),
    path('avenant/autocomplete/', AvenantAutocomplete.as_view(), name='avenant_autocomplete'),
    #
    path("soustypes/", getsoustypes, name='getsoustypes'),
    #
    path('check-document/', check_document, name='check_document'),

]
