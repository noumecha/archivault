from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from web_project import TemplateLayout
from config.views import BaseCRUDView
from apps.notifications.models import Notification
from apps.users.models import RoleUtilisateur

class NotificationManagementView(LoginRequiredMixin, BaseCRUDView):
    """Vue pour consulter et gérer ses notifications."""
    model = Notification
    list_route = 'notification_list'
    template_name = "pages/notification_management.html"
    context_object_name = 'notifications'

    # Tout utilisateur connecté peut voir ses notifications
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR, RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE
    ]

    # Ces headers doivent correspondre au nombre de <td> dans ton UI.js
    headers = ["Date", "Message", "Catégorie", "Actions"]

    # Définit ce qui sera rendu par {% for name, options, label in filters %}
    filters = [
        ('is_read', [('1', 'Lues'), ('0', 'Non lues')], 'Statut'),
        ('categorie', [('tache', 'Tâches'), ('circulation', 'Circulation'), ('systeme', 'Système')], 'Catégorie'),
    ]

    search_fields = ['titre', 'message']

    def get_queryset(self, search_query=None):
        """L'utilisateur ne gère que ses propres notifications."""
        user = self.request.user
        queryset = Notification.objects.filter(destinataire=user)

        if search_query:
            queryset = queryset.filter(
                Q(titre__icontains=search_query) |
                Q(message__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = TemplateLayout.init(self, context)
        # On transforme les tuples en dictionnaires pour correspondre à ton template générique
        formatted_filters = []
        for name, options, label in self.filters:
            formatted_filters.append({
                'name': name,
                'label': label,
                'items': [{'value': val, 'label': txt} for val, txt in options]
            })
        context['headers'] = self.headers
        context['filters'] = formatted_filters
        return TemplateLayout.init(self, context)
