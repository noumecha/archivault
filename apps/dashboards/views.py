from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count
from datetime import datetime
from apps.dashboards.configs.configs import DASHBOARD_CONFIG
from apps.documents.models import Document, EtatDocument, Theme
from apps.documents.models import TypeDocument, SousTypeDocument
from apps.users.models import RoleUtilisateur, Utilisateur
from apps.administration.models import Cellule
from .services.dashboard_service import DashboardService
from web_project import TemplateLayout
from django.db.models import Count
from django.db.models.functions import TruncMonth
import datetime
import json

class DashboardsView(TemplateView):

    template_name = "new_dashboard_analytics.html"

    def get_dashboard_resume(self, user):
        dashboard_type = DashboardService.get_dashboard_type(user)
        if dashboard_type == "GLOBAL":
            return {
                "title": "Résumé global du système",
                "subtitle": "Vue d’ensemble",
                "description": "Statistiques globales de tous les documents",
            }
        if dashboard_type == "CELLULE":
            return {
                "title": f"Résumé de la cellule {user.cellule.nom}",
                "subtitle": "Vue par cellule",
                "description": "Statistiques des documents de votre cellule",
            }
        return {
            "title": "Mes documents",
            "subtitle": "Vue personnelle",
            "description": "Statistiques de vos documents",
        }

    @method_decorator(login_required(login_url="/login/"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        docs_qs = DashboardService.get_documents_queryset(user)
        dashboard_type = DashboardService.get_dashboard_type(user)
        context["dashboard_type"] = dashboard_type
        context["dashboard_sections"] = DASHBOARD_CONFIG.get(user.role, [])

        # --- Gestion du filtre par année pour le graphique ---
        available_years = docs_qs.dates('Date_creation', 'year', order='DESC')
        try:
            selected_year = int(self.request.GET.get('year', datetime.date.today().year))
        except (ValueError, TypeError):
            selected_year = datetime.date.today().year
        context['available_years'] = available_years
        context['selected_year'] = selected_year

        # resume vars
        context["dashboard_resume"] = self.get_dashboard_resume(user)
        # cards menu link
        if user.role in [RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR]:
            context["manage_menu"] = [
                {"label": "Utilisateurs", "icon": "ri-user-2-line me-1", "section": "users", "link":"utilisateur_list"},
                {"label": "Documents", "icon": "ri-folders-line me-1", "section": "docs", "link":"list_document"},
                {"label": "Types de Documents", "icon": "ri-folder-settings-line me-1", "section": "docstypes", "link":"typedocument_list"},
            ]
        else:
            context["manage_menu"] = [
                {"label": "Documents", "icon": "ri-folders-line me-1", "section": "docs", "link":"list_document"},
            ]
        # counts stats
        context["dashboard_type"] = dashboard_type
        context['total_userdocs'] = docs_qs.filter(cree_par=user).count()
        context["total_docs"] = docs_qs.count()
        context["docs_valides"] = docs_qs.filter(etat=EtatDocument.VALIDE).count()
        context["docs_archives"] = docs_qs.filter(etat=EtatDocument.ARCHIVE).count()
        context["docs_entraitement"] = docs_qs.filter(etat=EtatDocument.EN_TRAITEMENT).count()
        context["docs_attente"] = docs_qs.filter(etat=EtatDocument.EN_ATTENTE).count()

        # --- Données du graphique annuel (filtrées par rôle et année) ---
        docs_by_month_qs = (
            docs_qs.filter(Date_creation__year=selected_year)
            .annotate(month=TruncMonth('Date_creation'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )
        monthly_counts = {i: 0 for i in range(1, 13)}
        for item in docs_by_month_qs:
            monthly_counts[item['month'].month] = item['total']
        month_labels = [
            "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
            "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"
        ]
        context['docs_by_month_labels'] = json.dumps(month_labels)
        context['docs_by_month_data'] = json.dumps(list(monthly_counts.values()))

        # Statistiques visibles uniquement pour les admins (vue globale)
        if dashboard_type == "GLOBAL":
            context["utilisateurs"] = Utilisateur.objects.count()
            context["cellules"] = Cellule.objects.count()
            context["by_cellule"] = (
                Document.objects.values("cellule__nom")
                .annotate(total=Count("id"))
                .order_by("-total")
            )

        # Derniers documents
        context["latest_docs"] = (
            docs_qs.select_related("cree_par", "type_document")
            .order_by("-Date_creation")[:5]
        )

        return context
