# apps/documents/web/views/ThemeListView.py
from ...forms import *
from config.views import BaseCRUDView
from web_project import TemplateLayout
from config.roles import *
from config.mixins.permissions import *
from apps.circulation.models import *

class ThemeListView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    filters = [
        ('cellule', Cellule, 'Unité de traitement'),
    ]
    # surchage de get_context_data pour afficher les filters en fonction des roles
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        # --- FILTRAGE DES CELLULES ---
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN]:
            filtered_cellules = Cellule.objects.all()
        else:
            filtered_cellules = Cellule.objects.filter(id=user.cellule_id) if user.cellule else Cellule.objects.none()
        context['cellules'] = filtered_cellules
        for f in context.get('filters', []):
            if f['name'] == 'cellule':
                f['items'] = filtered_cellules

        return context
    model = Theme
    form_class = ThemesForm
    list_route = 'themes_list'
    list_template = 'pages/themes_list.html'
    context_object_name = 'themes'
    search_fields = ["libelle","description_theme", "cellule__nom"]
    headers = ["Libelle", "Description", "Cellule"]
    fields = ["libelle","description_theme", "cellule"]
