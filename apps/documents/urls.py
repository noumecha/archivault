from django.urls import path
from . import views

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
    *get_crud_urls(views.TypeDocumentView, "typedocument/typedocuments", "typedocument"),
    *get_crud_urls(views.DocumentView, "document/documents", "document"),
    # Gestion types et thèmes
    *get_crud_urls(views.DocumentView, "theme/themes", "themes"),
    # documents
    # path('', views.DocumentListView.as_view(), name='documents'),
    # path("all/", views.get_documents, name='get_documents'),
    # path("form/", views.document_form_view, name='document_form'), # load form
    # path("edit/<int:pk>", views.document_form_view, name='document_update'),
    # path("update/<int:pk>", views.update_documents, name='update_document'),
    # path("delete/<int:pk>", views.document_delete_view, name='document_delete'),
    path('nouveau/', views.DocumentCreateView.as_view(), name="create"),
    path('upload/', views.DocumentUploadAPI.as_view(), name='api-upload'),
    path('types/<int:type_id>/sous-types/', views.SousTypesAPIView.as_view(), name='api-sous-types'),
]