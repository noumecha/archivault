# apps/documents/api/views.py
from rest_framework import status
from rest_framework.response import Response
from apps.documents.services.visibility_service import VisibilityService
from config.api.base_api_view import BaseAPIView
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ..models import *
from ..services.permissions import DocumentPermissionService
from ..services.document_service import DocumentService as DocBusinessService
from ..forms import UploadMultipleForm
from rest_framework.permissions import IsAuthenticated
from .serializers import *
import os, json
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.circulation.models import Tache, CirculationDocument
from apps.administration.models import Cellule
from apps.users.models import Utilisateur, RoleUtilisateur

class DocumentAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API Centralisée pour les Documents.

    Endpoints :

    GET    /api/documents/              → Liste (paginée, filtrée, recherchée)
    POST   /api/documents/create              → Créer
    GET    /api/documents/<id>/         → Détail
    PUT    /api/documents/<id>/update         → Mise à jour complète
    PATCH  /api/documents/<id>/update         → Mise à jour partielle
    DELETE /api/documents/<id>/delete         → Supprimer
    BULK DELETE /api/documents/bulk-delete       → Suppression de masse
    UPLOAD MULTIPLE /api/documents/upload-multiple/     → Upload Multiple
    CHECK CONFLICT /api/documents/check-conflict/       → Check de conflit sur les documents
    ADD TACHE /api/documents/<id>/add-tache/            → Préparer l'ajout d'une tâche
    ADD CIRCULATION /api/documents/<id>/add-circulation/ → Préparer l'ajout d'une circulation
    """
    model = Document
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser] # Pour gérer les fichiers
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ['titre']
    filter_fields = [
        'type',
        'sous_type',
        'theme',
        'etat',
        'profil_document',
        'cellule',
        'niveau_acces',
    ]

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE,
    ]

    def get_queryset(self):
        user = self.request.user
        qs = DocumentPermissionService.get_visible_documents(user)
        params = self._get_query_params()
        date_debut = params.get('date_debut')
        date_fin = params.get('date_fin')
        extension = params.get('ext')
        if date_debut:
            qs = qs.filter(Date_creation__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(Date_creation__date__lte=date_fin)
        if extension:
            qs = qs.filter(versions__fichier__iendswith='.' + extension.lstrip('.')).distinct()
        return super().get_queryset(queryset=qs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS CUSTOM SPÉCIFIQUES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'upload_multiple': 'upload_multiple_action',
        'check_conflict': 'check_conflict_action',
        'retrieve': 'retrieve_action', # Override pour ajouter le log/versions
        'add_tache': 'add_tache_action',
        'add_circulation': 'add_circulation_action',
        'bulk_delete': 'bulk_delete_action'
    }

    # 1. Upload Multiple (Remplace DocumentCreateMultipleView)
    def upload_multiple_action(self, request, *args, **kwargs):
        files = request.FILES.getlist('fichiers')
        if not files:
            return Response({'success': False, 'message': 'Aucun fichier fourni'}, status=400)

        # Parsing des actions envoyées par le JS
        actions_map = {}
        actions_raw = request.data.getlist('actions[]')
        for item in actions_raw:
            try:
                data_json = json.loads(item)
                actions_map[data_json['name']] = data_json
            except: continue

        # Préparation des métadonnées (ID uniquement pour éviter les requêtes inutiles dans la boucle)
        metadata = {
            'type_document_id': request.data.get('type_document'),
            'theme_id': request.data.get('theme'),
            'sous_type_id': request.data.get('sous_type'),
            'niveau_acces': request.data.get('niveau_acces'),
            'etat': request.data.get('etat'),
            'profil_document': request.data.get('profil_document'),
            'cellule': request.data.get('cellule'),
            'responsable_document_id': request.data.get('responsable_document'),
        }

        # APPEL UNIQUE AU SERVICE
        results = DocBusinessService.process_upload(request.user, files, actions_map, metadata)

        return Response({
            'success': len(results['errors']) == 0,
            'message': f"Traitement terminé. {results['created']} créés, {results['versioned']} versions.",
            'details': results
        })

    # 2. Check Conflict (Remplace check_document)
    def check_conflict_action(self, request):
        filename = request.query_params.get('filename', '') or request.GET.get('filename', '')
        doc, titre = DocBusinessService.check_conflict(filename, request.user)

        return Response({
            'exists': doc is not None,
            'titre': titre,
            'document_id': doc.id if doc else None,
            'suggested_action': 'version' if doc else 'create'
        })

    # 3. Détail enrichi (Remplace DocumentDetailView)
    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(Document, pk=pk)

        # Vérification permissions via le service mis à jour
        if not DocumentPermissionService.can_view(request.user, instance):
            return Response({'success': False, 'message': 'Accès refusé'}, status=403)

        user = request.user

        # Détermination des querysets de paramètres selon le contexte du document
        if is_admin(user) or is_superadmin(user):
            cellules = Cellule.objects.all()
            types_docs = TypeDocument.objects.all()
            themes = Theme.objects.all()
            sous_types = SousTypeDocument.objects.all()
        else:
            # Règle : La cellule du document en question (Accès transversal lié à la tâche)
            cellules_ids = list(filter(None, [instance.cellule_id]))

            cellules = Cellule.objects.filter(id__in=cellules_ids)
            types_docs = TypeDocument.objects.filter(cellule_id__in=cellules_ids)
            themes = Theme.objects.filter(cellule_id__in=cellules_ids)
            sous_types = SousTypeDocument.objects.filter(type_document__cellule_id__in=cellules_ids)

        # Récupération contextuelle complète pour l'injection côté UI
        context_data = {
            'document': self.get_serializer(instance).data,
            'versions': VersionDocumentSerializer(instance.versions.all(), many=True).data,
            'taches': [],
            'circulations': [],
            # 🟢 On injecte les listes de paramètres filtrées pour le formulaire d'édition
            'options_formulaire': {
                'cellules': [{'id': c.id, 'nom': c.nom} for c in cellules],
                'types_documents': [{'id': t.id, 'libelle': t.libelle} for t in types_docs],
                'themes': [{'id': th.id, 'libelle': th.libelle} for th in themes],
                'sous_types': [{'id': st.id, 'libelle': st.libelle, 'type_document_id': st.type_document_id} for st in sous_types],
            }
        }

        return Response({
            'success': True,
            'data': context_data
        })

    # 4. Ajouter une tâche (Action rapide)
    def add_tache_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # Logique simplifiée pour l'API, les données réelles sont gérées par le service Tache
        # Ici on peut renvoyer les infos nécessaires pour le formulaire ou traiter une création rapide
        return Response({
            'success': True,
            'message': 'Prêt à ajouter une tâche',
            'document_id': instance.id,
            'titre': instance.titre
        })

    # 5. Ajouter une circulation (Action rapide)
    def add_circulation_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # Logique simplifiée pour l'API
        return Response({
            'success': True,
            'message': 'Prêt à ajouter une circulation',
            'document_id': instance.id,
            'titre': instance.titre
        })

    # 6. Suppression groupée
    def bulk_delete_action(self, request, *args, **kwargs):
        """Suppression en masse."""
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = Document.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} document(s) supprimé(s)',
            'deleted_count': deleted_count
        })

    # Override de list_action pour gérer les filtres spécifiques si besoin
    def list_action(self, request, *args, **kwargs):
        # La base gère déjà la pagination et les filtres, on peut ajouter des logs ici
        return super().list_action(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Ajout de helpers pour le rendu des badges en JS
        return context

    def update_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_edit(request.user, instance):
            return Response({ "success" : False, "message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_delete(request.user, instance):
            return Response({ "success" : False, "message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete_action(request, pk, *args, **kwargs)

class ThemeAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des themes.

    Endpoints :

        GET    /api/themes/              → Liste (paginée, filtrée, recherchée)
        POST   /api/themes/create              → Créer
        GET    /api/themes/<id>/         → Détail
        PUT    /api/themes/<id>/update         → Mise à jour complète
        PATCH  /api/themes/<id>/update         → Mise à jour partielle
        DELETE /api/themes/<id>/delete         → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Theme
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['libelle', 'description_theme']
    filter_fields = ['cellule']

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        queryset = Theme.objects.select_related('cellule').all()
        qs = VisibilityService.filter_by_cellule(queryset, self.request.user)
        return super().get_queryset(qs)

    # ─────────────────────────────────────────────────────────────────────────
    # OVERRIDE DES ACTIONS POUR AJOUTER DES PERMISSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def create_action(self, request, *args, **kwargs):
        """Création avec vérification du rôle."""
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        """Mise à jour avec vérification du rôle."""
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression avec vérification du rôle."""
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        """Suppression en masse."""
        self.check_role_permission(request)

        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'success': False,
                'message': 'Aucun ID fourni'
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Theme.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} theme(s) supprimé(s)',
            'deleted_count': deleted_count
        })


class TypeDocumentAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des types de documents.

    Endpoints :

        GET    /api/typedocuments/              → Liste (paginée, filtrée, recherchée)
        POST   /api/typedocuments/create              → Créer
        GET    /api/typedocuments/<id>/         → Détail
        PUT    /api/typedocuments/<id>/update         → Mise à jour complète
        PATCH  /api/typedocuments/<id>/update         → Mise à jour partielle
        DELETE /api/typedocuments/<id>/delete         → Supprimer
    """
    model = TypeDocument
    serializer_class = TypeDocumentSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['libelle', 'description_typedocument']
    filter_fields = ['cellule', 'parent_type']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        queryset = TypeDocument.objects.select_related('cellule', 'parent_type').all()
        qs = VisibilityService.filter_by_cellule(queryset, self.request.user)
        return super().get_queryset(qs)

    def create_action(self, request, *args, **kwargs):
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'success': False, 'message': 'Aucun ID fourni'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = TypeDocument.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} type(s) supprimé(s)',
            'deleted_count': deleted_count
        })


class SousTypeDocumentAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """API pour la gestion des sous-types de documents.

    Endpoints :

        GET    /api/soustypedocuments/              → Liste (paginée, filtrée, recherchée)
        POST   /api/soustypedocuments/create              → Créer
        GET    /api/soustypedocuments/<id>/         → Détail
        PUT    /api/soustypedocuments/<id>/update         → Mise à jour complète
        PATCH  /api/soustypedocuments/<id>/update         → Mise à jour partielle
        DELETE /api/soustypedocuments/<id>/delete         → Supprimer
    """
    model = SousTypeDocument
    serializer_class = SousTypeDocumentSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['libelle', 'description_soustypedocument']
    filter_fields = {
        'cellule': 'type_document__cellule',
        'type_document': 'type_document',
    }
    #filter_fields = ['type_document__cellule', 'type_document']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        base_qs = SousTypeDocument.objects.select_related('type_document__cellule')
        filtered_qs = VisibilityService.filter_by_cellule(
            base_qs,
            self.request.user,
            field_name='type_document__cellule'
        )
        return super().get_queryset(filtered_qs)

    def create_action(self, request, *args, **kwargs):
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'success': False, 'message': 'Aucun ID fourni'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = SousTypeDocument.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} sous-type(s) supprimé(s)',
            'deleted_count': deleted_count
        })


class AvenantAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """API pour la gestion des avenants.

    Endpoints :

        GET    /api/avenants/              → Liste (paginée, filtrée, recherchée)
        POST   /api/avenants/create              → Créer
        GET    /api/avenants/<id>/         → Détail
        PUT    /api/avenants/<id>/update         → Mise à jour complète
        PATCH  /api/avenants/<id>/update         → Mise à jour partielle
        DELETE /api/avenants/<id>/delete         → Supprimer
    """
    model = Avenants
    serializer_class = AvenantSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['libelle', 'numero']
    filter_fields = ['bailleur']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        # Filtrage indirect : Avenant -> Bailleur -> Cellule
        base_qs = self.model.objects.select_related('bailleur__cellule').all()
        filtered_qs = VisibilityService.filter_by_cellule(
            base_qs,
            self.request.user,
            field_name='bailleur__cellule'
        )
        return super().get_queryset(filtered_qs)

    def create_action(self, request, *args, **kwargs):
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'success': False, 'message': 'Aucun ID fourni'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = self.model.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} avenant(s) supprimé(s)',
            'deleted_count': deleted_count
        })


class BailleurAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """API pour la gestion des bailleurs.

    Endpoints :

        GET    /api/bailleurs/              → Liste (paginée, filtrée, recherchée)
        POST   /api/bailleurs/create              → Créer
        GET    /api/bailleurs/<id>/         → Détail
        PUT    /api/bailleurs/<id>/update         → Mise à jour complète
        PATCH  /api/bailleurs/<id>/update         → Mise à jour partielle
        DELETE /api/bailleurs/<id>/delete         → Supprimer
    """
    model = Bailleurs
    serializer_class = BailleurSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ['abrevation', 'libelle', 'description', 'cellule__nom']
    filter_fields = ['cellule']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR
    ]

    def get_queryset(self):
        base_qs = self.model.objects.select_related('cellule').all()
        filtered_qs = VisibilityService.filter_by_cellule(
            base_qs,
            self.request.user,
            field_name='cellule'
        )
        return super().get_queryset(filtered_qs)

    def create_action(self, request, *args, **kwargs):
        self.check_role_permission(request)
        return super().create_action(request, *args, **kwargs)

    def update_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        self.check_role_permission(request)
        return super().delete_action(request, pk, *args, **kwargs)

    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
    }

    def action_bulk_delete(self, request, *args, **kwargs):
        self.check_role_permission(request)
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'success': False, 'message': 'Aucun ID fourni'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = self.model.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} bailleurs(s) supprimé(s)',
            'deleted_count': deleted_count
        })
