# apps/documents/web/views/TypeDocumentView.py
from apps.documents.services.visibility_service import VisibilityService

from ...forms import *
from config.views import BaseCRUDView
from web_project import TemplateLayout
from config.roles import *
from config.mixins.permissions import *
from apps.circulation.models import *
from django.db.models import Q

class TypeDocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TypeDocument.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(description__icontains=self.q)
            )
        return qs

class TypeDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('parent_type', TypeDocument, 'Type parent'),
    ]

    def get_queryset(self, search_query=None):
        qs = super().get_queryset(search_query)
        # Filtrer le tableau principal pour l'utilisateur
        return VisibilityService.filter_by_cellule_or_generic(qs, self.request.user)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user

        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
        context['cellules'] = filtered_cellules

        parent_qs = TypeDocument.objects.filter(parent_type__isnull=True)
        context['parent_types'] = VisibilityService.filter_by_cellule_or_generic(parent_qs, user)

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules
            if f['name'] == 'parent_type':
                f['items'] = context['parent_types']
        return context

    model = TypeDocument
    list_route = 'typedocument_list'
    list_template = 'pages/typedocuments_list.html'
    context_object_name = 'typedocuments'
    search_fields = ["libelle","description_typedocument", "cellule__nom"]
    object_name = 'typedocument'
    headers = ["Libelle", "Description"]
    fields = ["libelle","description_typedocument"]
