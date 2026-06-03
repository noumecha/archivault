# apps/documents/web/views/BailleursView.py
from ...forms import *
from config.views import BaseCRUDView
from web_project import TemplateLayout
from config.roles import *
from django.db.models import Q
from config.mixins.permissions import *
from apps.circulation.models import *


class BailleurAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Bailleurs.objects.all()
        if self.q:
            qs = qs.filter(
                Q(libelle__icontains=self.q) | Q(abrevation__icontains=self.q)
            )
        return qs

class BailleursView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement')
    ]
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            context['cellules_list'] = Cellule.objects.all()
        else:
            context['cellules_list'] = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()

        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = context['cellules_list']
        return context
    model = Bailleurs
    form_class = BailleursFrom
    list_route = 'bailleurs_list'
    list_template = 'pages/bailleurs_list.html'
    context_object_name = 'bailleurs',
    search_fields = ["abrevation","libelle","description"]
    headers = ["Abrevation","Libelle"]
    fields = ["abrevation","libelle"]
    object_name = 'bailleur'
