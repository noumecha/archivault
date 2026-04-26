# apps/documents/api/views.py
from rest_framework import status
from rest_framework.response import Response
from apps.documents.services.visibility_service import VisibilityService
from config.api.base_api_view import BaseAPIView
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ..models import Document, TypeDocument, Theme, SousTypeDocument, Bailleurs, Avenants
from ..services.permissions import DocumentPermissionService
from ..services.document_service import DocumentService as DocBusinessService
from ..forms import UploadMultipleForm
from apps.users.models import RoleUtilisateur
from rest_framework.permissions import IsAuthenticated
from .serializers import DocumentSerializer, ThemeSerializer, TypeDocumentSerializer, SousTypeDocumentSerializer, AvenantSerializer, BailleurSerializer
import os, json

class DocumentAPIView(BaseAPIView):
    """
    API pour la gestion des documents.

    Endpoints :

        GET    /api/documents/              → Liste (paginée, filtrée, recherchée)
        POST   /api/documents/create              → Créer
        GET    /api/documents/<id>/         → Détail
        PUT    /api/documents/<id>/update         → Mise à jour complète
        PATCH  /api/documents/<id>/update         → Mise à jour partielle
        DELETE /api/documents/<id>/delete         → Supprimer
    """
    model = Document
    serializer_class = DocumentSerializer
    search_fields = ['titre', 'metadonnees']
    filter_fields = ['type_document', 'theme', 'etat', 'cellule']

    def get_queryset(self):
        """Applique les contraintes de visibilité basées sur le service de permissions."""
        user = self.request.user
        qs = DocumentPermissionService.get_visible_documents(user)
        return super().get_queryset(queryset=qs)

    custom_actions = {
        'check_conflict': 'action_check_conflict',
        'upload_multiple': 'action_upload_multiple'
    }

    def action_check_conflict(self, request):
        filename = request.GET.get("filename", "")
        name = os.path.splitext(filename)[0]
        titre = name.replace('_', ' ').replace('-', ' ').strip()

        exists = Document.objects.filter(titre__iexact=titre).first()
        if exists:
            return Response({
                "exists": True,
                "document_id": exists.id,
                "titre": exists.titre,
            })
        return Response({"exists": False})

    def action_upload_multiple(self, request):
        # Utilisation du formulaire pour valider les métadonnées communes
        form = UploadMultipleForm(request.POST, request.FILES, user=request.user)

        if not form.is_valid():
            return Response({
                "success": False,
                "message": "Données de formulaire invalides",
                "errors": form.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('fichiers')
        actions_raw = request.POST.getlist("actions[]")

        # Reconstruction du dictionnaire d'actions indexé par nom de fichier
        actions_map = {}
        for act_str in actions_raw:
            try:
                act_data = json.loads(act_str)
                # Le frontend envoie l'objet file complet, on récupère le nom
                filename = act_data.get('file', {}).get('name') or act_data.get('name')
                if filename:
                    actions_map[filename] = act_data
            except json.JSONDecodeError:
                continue

        # Appel du service métier pour le traitement transactionnel
        result = DocBusinessService.process_upload(
            user=request.user,
            files=files,
            actions=actions_map,
            data=form.cleaned_data
        )

        msg = f"{len(result['documents'])} documents traités, {len(result['versions'])} nouvelles versions."
        if result['skipped']:
            msg += f" ({len(result['skipped'])} ignorés)"

        return Response({
            "success": True,
            "message": msg,
            "data": {
                "count_docs": len(result['documents']),
                "count_versions": len(result['versions'])
            }
        })

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Ajout de helpers pour le rendu des badges en JS
        return context

    def update_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_edit(request.user, instance):
            return Response({"message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        return super().update_action(request, pk, *args, **kwargs)

    def delete_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_delete(request.user, instance):
            return Response({"message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
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
