from apps.documents.models import Avenants, Bailleurs, Document, EtatDocument, ProfilDoc, SousTypeDocument, Theme, TypeDocument
from apps.users.models import RoleUtilisateur, Utilisateur
from .models import *
from .forms import *
from config.views import BaseCRUDView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.contrib import messages
from config.utils.utils import generates_filters
from django.db.models import Count
from config.mixins.permissions import *
from config.roles import *

class CelluleView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]
    model = Cellule
    form_class = CellulesForm
    list_route = 'cellule_list'
    list_template = 'cellules_list.html'
    context_object_name = 'cellules'
    object_label = 'Unité de traitement'
    search_fields = ["nom","description_cellule"]
    headers = ["Nom", "Description"]
    fields = ["nom", "description_cellule"]
    delete_url = "cellule_delete"
    manage_url = "cellule_manage"
    manage_menu = [
        {"label": "Statistiques", "icon": "ri-bar-chart-line me-1", "section": "stats"},
        {"label": "Utilisateurs", "icon": "ri-user-2-line me-1", "section": "users"},
        {"label": "Documents", "icon": "ri-folders-line me-1", "section": "docs"},
        {"label": "Types de Documents", "icon": "ri-folder-settings-line me-1", "section": "docstypes"},
        {"label": "Bailleurs", "icon": "ri-wallet-2-fill me-1", "section": "bailleurs"},
        {"label": "Avenants", "icon": "ri-bill-fill me-1", "section": "avenants"},
    ]
    manage_template = 'cellules/manage_base.html'

    def get_form_kwargs(self, request, **kwargs):
        form_kwargs = super().get_form_kwargs(request, **kwargs)

        # Si on est dans un manage contextuel
        cellule_id = kwargs.get("pk")
        section = kwargs.get("section")
        print("section = ", section)

        if cellule_id and section == "docstypes":
            form_kwargs["cellule"] = get_object_or_404(Cellule, pk=cellule_id)

        return form_kwargs

    def get_manage_menu(self, obj):
        menu = super().get_manage_menu(obj)
        if not obj.accepte_bailleurs:
            # Si la cellule n'accepte pas les bailleurs, on retire les sections correspondantes
            menu = [item for item in menu if item['section'] not in ['bailleurs', 'avenants']]
        return menu

    # gérer les types de documents
    def manage_docstypes(self, request, context, obj):
        template = self.get_manage_template("docstypes")
        return render(request, template, context)

    # gerer les documents
    def manage_docs(self, request, context, obj):
        template = self.get_manage_template("docs")
        filters = [
            ('type_document', TypeDocument),
            ('sous_type', SousTypeDocument),
            ('etat', EtatDocument),
            ('profil_document', ProfilDoc, 'Profil du Document'),
            ('theme', Theme),
            ('bailleur', Bailleurs),
        ]
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    # gérer les bailleurs
    def manage_bailleurs(self, request, context, obj):
        template = self.get_manage_template("bailleurs")
        return render(request, template, context)

    # gérer les avenants
    def manage_avenants(self, request, context, obj):
        template = self.get_manage_template("avenants")
        filters = [
            ('bailleur', Bailleurs),
        ]
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    # gérer les utilisateurs
    def manage_users(self, request, context, obj):
        # Logiques personnalisées pour la section membres
        # Le filtre sur la cellule est désormais implicite, on ne garde que les autres filtres.
        filters = [
            ('role', RoleUtilisateur),
        ]
        template = self.get_manage_template("users")
        context['filters'] = generates_filters(filters)
        return render(request, template, context)

    # gérer les statistiques
    def manage_stats(self, request, context, obj):
        template = self.get_manage_template("stats")

        # 1. Récupérer tous les documents de la cellule
        documents = Document.objects.filter(cellule=obj)

        # 2. Créer une liste dynamique de cartes de statistiques
        stats_cards = [
            {"label": "Documents", "value": documents.count(), "icon": "ri-folders-line", "color_class": "bg-label-primary"},
            {"label": "Utilisateurs", "value": Utilisateur.objects.filter(cellule=obj).count(), "icon": "ri-user-2-line", "color_class": "bg-label-info"},
        ]

        # Ajouter les bailleurs et avenants seulement si la cellule les accepte
        if obj.accepte_bailleurs:
            stats_cards.append({"label": "Bailleurs", "value": Bailleurs.objects.filter(cellule=obj).count(), "icon": "ri-wallet-2-fill", "color_class": "bg-label-success"})
            stats_cards.append({"label": "Avenants", "value": Avenants.objects.filter(bailleur__cellule=obj).count(), "icon": "ri-bill-fill", "color_class": "bg-label-warning"})

        # 3. Calculer les autres statistiques pour les graphiques et listes
        docs_by_status = documents.values('etat').annotate(count=Count('etat')).order_by('-count')
        stats = {
            'recent_documents': documents.order_by('-Date_creation')[:5]
        }

        # 4. Préparer les données pour les graphiques (Chart.js)
        status_labels = [item['etat'] for item in docs_by_status]
        status_data = [item['count'] for item in docs_by_status]

        # 5. Déterminer la classe de colonne pour un affichage responsive
        num_cards = len(stats_cards)
        if num_cards > 0 and 12 % num_cards == 0:
            col_class = f"col-lg-{12 // num_cards}"
        else:
            col_class = "col-lg-3" # Valeur par défaut

        # 6. Ajouter les statistiques au contexte
        context['stats_cards'] = stats_cards
        context['col_class'] = col_class
        context['stats'] = stats
        context['chart_status_labels'] = status_labels
        context['chart_status_data'] = status_data

        return render(request, template, context)

class DivisionView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]
    model = Division
    form_class = DivisionForm
    list_route = 'division_list'
    list_template = 'divisions_list.html'
    context_object_name = 'divisions'
    search_fields = ["nom","description_division"]
    headers = ["Nom", "Description", "Statut"]
    fields = ["nom", "description_division", "statut"]
    delete_url = "division_delete"
    manage_url = "division_manage"
    # 🔹 Déclaration des actions personnalisées
    custom_actions = {
        "toggle_status": "toggle_status_action"
    }

    def toggle_status_action(self, request, pk):
        """Active ou désactive une division"""
        division = get_object_or_404(Division, pk=pk)
        if division.statut == 'activé':
            division.statut = 'desactivé'
        else:
            division.statut = 'activé'
        division.save()
        messages.success(request, f"La division '{division.nom}' a été {division.statut}.")
        return redirect(self.list_route)

class MinistereView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]
    model = Ministere
    form_class = MinistereForm
    list_route = 'ministere_list'
    list_template = 'ministeres_list.html'
    context_object_name = 'ministeres'
    search_fields = ["nom","description_ministere","code","abrevation"]
    headers = ["Nom", "Description","Code","abrevation"]
    fields = ["nom", "description_ministere","code","abrevation"]
    delete_url = "ministere_delete"
    manage_url = "ministere_manage"

class DirectionGeneraleView(RoleRequiredMixin, BaseCRUDView):
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
    ]
    model = DirectionGenerale
    form_class = DirectionGeneraleForm
    list_route = 'directiongenerale_list'
    list_template = 'directiongenerales_list.html'
    context_object_name = 'directiongenerales'
    search_fields = ["nom","description_direction_generale"]
    headers = ["Nom", "Description", "Ministere"]
    fields = ["nom", "description_direction_generale", "ministere"]
    delete_url = "directiongenerale_delete"
    manage_url = "directiongenerale_manage"
    object_name = "directiongenerale"
