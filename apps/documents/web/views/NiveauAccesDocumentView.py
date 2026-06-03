# apps/documents/web/views/NiveauAccesDocumentView.py
from ...forms import *
from config.views import BaseCRUDView
from config.roles import *
from config.mixins.permissions import *
from apps.circulation.models import *

class NiveauAccesDocumentView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    model = NiveauAccesDocument
    form_class = NiveauAccesDocumentsForm
    list_route = 'niveauaccess_list'
    list_template = 'pages/niveauaccesss_list.html'
    context_object_name = 'niveauaccesss'
    object_name = 'niveauaccess'
    search_fields = ["niveau","description_niveauaccess"]
    filters = []
    headers = ["Libelle", "Description"]
    fields = ["niveau","description_niveauaccess"]
    delete_url = "niveauaccess_delete"
