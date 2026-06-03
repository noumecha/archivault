
# apps/documents/web/views/SousTypeDocumentView.py
from ...forms import *
from config.views import BaseCRUDView
from web_project import TemplateLayout
from config.roles import *
from config.mixins.permissions import *
from apps.circulation.models import *
from django.db.models import Q

class SousTypeDocumentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SousTypeDocument.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(description__icontains=self.q)
            )
        return qs

class SousTypeDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
        ('type_document', TypeDocument, 'Type Document'),
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
        context['cellules'] = filtered_cellules

        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['types_documents'] = TypeDocument.objects.all()
        else:
            context['types_documents'] = TypeDocument.objects.filter(cellule_id=user.cellule_id) if user.cellule else TypeDocument.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules
            if f['name'] == 'type_document':
                f['items'] = context['types_documents']
        return context

    model = SousTypeDocument
    form_class = SousTypeDocumentsForm
    list_route = 'soustypedocument_list'
    list_template = 'pages/soustypedocument_list.html'
    context_object_name = 'soustypedocuments'
    object_name = 'soustypedocument'
    search_fields = ["libelle","description_soustypedocument"]
    headers = ["Libelle", "Description", "Type"]
    fields = ["libelle","description_soustypedocument", "type_document"]
