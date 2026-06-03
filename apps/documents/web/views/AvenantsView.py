# apps/documents/web/views/AvenantsView.py
from ...forms import *
from config.views import BaseCRUDView
from web_project import TemplateLayout
from config.roles import *
from config.mixins.permissions import *
from django.db.models import Q
from apps.circulation.models import *

class AvenantAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Avenants.objects.all()
        if self.q:
            qs = qs.filter(
                Q(nom__icontains=self.q) | Q(prenom__icontains=self.q)
            )
        return qs

class AvenantsView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['bailleurs_list'] = Bailleurs.objects.all()
        else:
            context['bailleurs_list'] = Bailleurs.objects.filter(cellule_id=user.cellule_id) if user.cellule else Bailleurs.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'bailleur':
                f['items'] = context['bailleurs_list']
        return context

    model = Avenants
    form_class = AvenantsForm
    list_route = 'avenants_list'
    list_template = 'pages/avenants_list.html'
    context_object_name = 'avenants',
    search_fields = ["nom","prenom"]
    filters = [
        ('bailleur', Bailleurs),
    ]
    headers = ["Nom","Prenom","Bailleur"]
    fields = ["nom","prenom","bailleur"]
    object_name = 'avenant'
