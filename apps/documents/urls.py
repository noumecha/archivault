from django.urls import path
from .views import *

# crud urls helper
def get_crud_urls(view_class, prefix, name):
    """ Helper function to generate CRUD URLs for a view class """
    #name = view_class.model._meta.model_name
    return [
        path(f"{prefix}/", view_class.as_view(template_name=view_class.list_template), name=f'{name}_list'),
        path(f"{prefix}/all/", view_class.as_view(), {'action': 'list'}, name=f'get_{name}s'),
        path(f"{prefix}/form/", view_class.as_view(), {'action': 'form'}, name=f'{name}_form'),
        path(f"{prefix}/edit/<int:pk>", view_class.as_view(), {'action': 'form'}, name=f'{name}_update'),
        path(f"{prefix}/update/<int:pk>", view_class.as_view(), {'action': 'update'}, name=f'{name}_update'),
        path(f"{prefix}/delete/<int:pk>", view_class.as_view(), {'action': 'delete'}, name=f'{name}_delete'),
    ]


urlpatterns = [
    *get_crud_urls(TypeDocumentView, "typedocument/typedocuments", "typedocument"),
    *get_crud_urls(SousTypeDocumentView, "soustypedocument/soustypedocuments", "soustypedocument"),
    *get_crud_urls(DocumentView, "document/documents", "document"),
    *get_crud_urls(RegleClassementView, "regleclassement/regleclassements", "regleclassement"),
    *get_crud_urls(NiveauAccesDocumentView, "niveauaccess/niveauaccesss", "niveauaccess"),
    *get_crud_urls(ThemeListView, "theme/themes", "themes"),
    # documents
    path('upload/', DocumentCreateMultipleView.as_view(), name='upload_document'),
    path('documents/list/', DocumentListView.as_view(), name='list_document'),
    path('edit/<int:pk>/', DocumentUpdateView.as_view(), name='edit_document'),
]
