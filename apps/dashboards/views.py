from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count
from datetime import datetime
from apps.documents.models import Document, EtatDocument, Theme
from apps.documents.models import TypeDocument, SousTypeDocument
from apps.users.models import RoleUtilisateur, Utilisateur
from apps.administration.models import Cellule
from web_project import TemplateLayout
from django.db.models import Count
from django.db.models.functions import TruncMonth
import datetime
import json

class DashboardsView(TemplateView):
    #template_name = "dashboard.html"
    template_name = "new_dashboard_analytics.html"

    @method_decorator(login_required(login_url="/login/"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        now = datetime.datetime.now()

        # annual stats :
        current_year = datetime.date.today().year
        docs_by_month_qs = (
            Document.objects.filter(Date_creation__year=current_year)
            .annotate(month=TruncMonth('Date_creation'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )

        # Initialiser les données pour les 12 mois à 0
        monthly_counts = {i: 0 for i in range(1, 13)}
        for item in docs_by_month_qs:
            monthly_counts[item['month'].month] = item['total']

        # Noms des mois en français
        month_labels = [
            "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
            "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"
        ]

        # Ajouter les données au contexte
        # Il est préférable de les passer en JSON pour le JavaScript
        context['docs_by_month_labels'] = json.dumps(month_labels)
        context['docs_by_month_data'] = json.dumps(list(monthly_counts.values()))

        # === Statistiques principales ===
        context["total_docs"] = Document.objects.count()
        context["docs_valides"] = Document.objects.filter(etat=EtatDocument.VALIDE).count()
        context["docs_archives"] = Document.objects.filter(etat=EtatDocument.ARCHIVE).count()
        context["docs_entraitement"] = Document.objects.filter(etat=EtatDocument.EN_TRAITEMENT).count()
        context["docs_attente"] = Document.objects.filter(etat=EtatDocument.EN_ATTENTE).count()
        context["utilisateurs"] = Utilisateur.objects.count()
        context["cellules"] = Cellule.objects.count()

        # === Documents créés par mois (année en cours) ===
        monthly_data = (
            Document.objects.filter(Date_creation__year=now.year)
            .annotate(month=Count("Date_creation__month"))
            .values_list("Date_creation__month")
        )
        context["monthly_counts"] = [
            Document.objects.filter(Date_creation__month=m, Date_creation__year=now.year).count()
            for m in range(1, 13)
        ]

        # === Répartition par cellule ===
        context["by_cellule"] = (
            Document.objects.values("cellule__nom")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        # === Derniers documents ===
        context["latest_docs"] = (
            Document.objects.select_related("cree_par", "type_document")
            .order_by("-Date_creation")[:5]
        )

        return context


#class DashboardsView(TemplateView):
#    # Predefined function
#    def get_context_data(self, **kwargs):
#        # A function to init the global layout. It is defined in web_project/__init__.py file
#        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
#
#        return context
#
#    @method_decorator(login_required(login_url="/login/"))
#    def dispatch(self, *args, **kwargs):
#        return super().dispatch(*args, **kwargs)
