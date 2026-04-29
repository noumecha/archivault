# apps/circulation/api/views.py
from datetime import timezone
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ..models import RoleUtilisateur
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import *
from django.db.models import Q
from ..models import Tache, StatutTache

class TacheAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion des tâches.
    Remplace TacheManagementView et TacheView en version full API.

    Endpoints :
        GET    /api/taches/              → Liste (paginée, filtrée, recherchée)
        POST   /api/taches/create              → Créer
        GET    /api/taches/<id>/         → Détail
        PUT    /api/taches/<id>/update         → Mise à jour complète
        PATCH  /api/taches/<id>/update         → Mise à jour partielle
        DELETE /api/taches/<id>/delete         → Supprimer
    """

    # ── Configuration du modèle ──────────────────────────────────────────────
    model = Tache
    serializer_class = TacheSerializer
    permission_classes = [IsAuthenticated]

    # ── Recherche & Filtrage ─────────────────────────────────────────────────
    search_fields = ['titre', 'description', 'document__titre']
    filter_fields = ['statut', 'priorite', 'assignee_a', 'assignee_par']

    # ── Permissions ──────────────────────────────────────────────────────────
    allowed_roles = [
        RoleUtilisateur.SUPERADMIN,
        RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR,
        RoleUtilisateur.RESPONSABLE,
        RoleUtilisateur.GESTIONNAIRE
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # QUERYSET PERSONNALISÉ
    # ─────────────────────────────────────────────────────────────────────────
    def get_queryset(self):
        """
        Retourne les tâches visibles par l'utilisateur selon son rôle et sa cellule.
        """
        user = self.request.user
        qs = Tache.objects.select_related('document', 'assignee_par', 'assignee_a')
        if is_admin(user) or is_superadmin(user):
            return super().get_queryset(queryset=qs)
        if is_superviseur(user):
            if hasattr(user, 'cellule') and user.cellule:
                qs = qs.filter(
                    Q(assignee_a__cellule=user.cellule) |
                    Q(assignee_par__cellule=user.cellule)
                )
            else:
                qs = qs.filter(Q(assignee_a=user) | Q(assignee_par=user))
        else:
            qs = qs.filter(Q(assignee_a=user) | Q(assignee_par=user))

        return super().get_queryset(queryset=qs)

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
        'comment': 'action_comment'
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
        deleted_count, _ = Tache.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} tâche(s) supprimée(s)',
            'deleted_count': deleted_count
        })

    def action_comment(self, request, pk=None, *args, **kwargs):
        """Ajouter un commentaire à une tâche et éventuellement changer son statut."""
        tache = get_object_or_404(Tache, pk=pk)
        contenu = request.data.get('contenu')
        nouveau_statut = request.data.get('statut')

        if not contenu:
            return Response({'success': False, 'message': 'Le contenu est requis'}, status=400)

        ancien_statut = tache.statut

        # Création du commentaire
        CommentaireTache.objects.create(
            tache=tache,
            auteur=request.user,
            contenu=contenu,
            ancien_statut=ancien_statut,
            nouveau_statut=nouveau_statut or ancien_statut
        )

        if nouveau_statut and nouveau_statut in StatutTache.values:
            tache.statut = nouveau_statut
            if nouveau_statut == StatutTache.TERMINEE:
                tache.date_cloture = timezone.now()
            tache.save()

        return Response({
            'success': True,
            'message': 'Commentaire ajouté avec succès',
            'data': TacheSerializer(tache).data
        })
