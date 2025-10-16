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
    *get_crud_urls(UserView, "utilisateur/utilisateurs", "utilisateur"),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/password/', UserPasswordView.as_view(), name='user_password_update'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('groups/', GroupAPIView.as_view(), name='api-groups'),
]
