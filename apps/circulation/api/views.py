# apps/circulation/api/views.py
from datetime import timezone
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ..models import RoleUtilisateur
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import *
from django.db.models import Q
from ..models import *
from django.db import transaction

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
    filter_fields = ['statut', 'priorite', 'assignee_a', 'assignee_par', 'document']

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
            return Response({'success': False, 'message': 'Le contenu est requis'}, status=status.HTTP_400_BAD_REQUEST)

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

class CirculationAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion de la circulation des documents.
    Gère le cycle de vie du circuit et le traitement des étapes.

    Endpoints :

        GET    /api/circulations/              → Liste (paginée, filtrée, recherchée)
        POST   /api/circulations/create              → Créer
        GET    /api/circulations/<id>/         → Détail
        PUT    /api/circulations/<id>/update         → Mise à jour complète
        PATCH  /api/circulations/<id>/update         → Mise à jour partielle
        DELETE /api/circulations/<id>/delete         → Supprimer
        POST   /api/circulations/<id>/traiter_etape         → Traiter une étape
        POST   /api/circulations/<id>/initier_circuit         → Initier un circuit
    """

    model = CirculationDocument
    serializer_class = CirculationDocumentSerializer
    search_fields = ['titre', 'description', 'document__titre']
    filter_fields = ['statut', 'initie_par', 'document']

    allowed_roles = [
        RoleUtilisateur.SUPERADMIN, RoleUtilisateur.ADMIN,
        RoleUtilisateur.SUPERVISEUR, RoleUtilisateur.RESPONSABLE, RoleUtilisateur.GESTIONNAIRE
    ]

    def get_queryset(self):
        user = self.request.user
        # Optimisation avec prefetch_related pour les étapes
        qs = CirculationDocument.objects.select_related('document', 'initie_par').prefetch_related('etapes__destinataire')

        if is_admin(user) or is_superadmin(user):
            return super().get_queryset(queryset=qs)

        # Un utilisateur voit les circulations qu'il a initiées
        # OU celles où il est destinataire d'une étape
        qs = qs.filter(
            Q(initie_par=user) | Q(etapes__destinataire=user)
        ).distinct()

        return super().get_queryset(queryset=qs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS CUSTOM
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'traiter_etape': 'action_traiter_etape',
        'initier_circuit': 'action_initier_circuit',
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
        deleted_count, _ = CirculationDocument.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} circulation(s) supprimée(s)',
            'deleted_count': deleted_count
        })

    def action_initier_circuit(self, request, *args, **kwargs):
        """
        Action pour créer un circuit et ses étapes en une fois (Transactionnel).
        Attendu : { "document": id, "titre": "...", "etapes": [{"destinataire": id, "ordre": 1}, ...] }
        """
        data = request.data
        etapes_data = data.get('etapes', [])

        if not etapes_data:
            return Response({'success': False, 'message': 'Un circuit doit avoir au moins une étape'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Créer la circulation
                circulation = CirculationDocument.objects.create(
                    document_id=data.get('document'),
                    titre=data.get('titre'),
                    description=data.get('description', ''),
                    initie_par=request.user,
                    statut=StatutCirculation.EN_COURS
                )

                # 2. Créer les étapes
                for i, etape in enumerate(etapes_data):
                    is_first = (i == 0)
                    EtapeCirculation.objects.create(
                        circulation=circulation,
                        destinataire_id=etape.get('destinataire'),
                        ordre=etape.get('ordre', i + 1),
                        statut=StatutCirculation.EN_COURS if is_first else StatutCirculation.EN_ATTENTE,
                        est_actuelle=is_first,
                        date_reception=timezone.now() if is_first else None
                    )

                return Response(CirculationDocumentSerializer(circulation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def action_traiter_etape(self, request, pk=None, *args, **kwargs):
        """
        Valider ou rejeter l'étape actuelle.
        Attendu : { "decision": "valide" | "rejete" | "retourne", "commentaire": "..." }
        """
        circulation = get_object_or_404(CirculationDocument, pk=pk)
        etape_actuelle = circulation.etapes.filter(est_actuelle=True).first()

        if not etape_actuelle:
            return Response({'success': False, 'message': 'Aucune étape active sur ce circuit'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier que c'est bien le destinataire qui traite
        if etape_actuelle.destinataire != request.user and not is_admin(request.user):
            return Response({'success': False, 'message': 'Vous n\'êtes pas le destinataire de cette étape'}, status=status.HTTP_403_FORBIDDEN)

        decision = request.data.get('decision')
        commentaire = request.data.get('commentaire', '')

        if decision not in [StatutCirculation.VALIDE, StatutCirculation.REJETE, StatutCirculation.RETOURNE]:
            return Response({'success' : False, 'message': 'Décision invalide'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Clôturer l'étape actuelle
                etape_actuelle.statut = decision
                etape_actuelle.commentaire = commentaire
                etape_actuelle.date_traitement = timezone.now()
                etape_actuelle.traite_par = request.user
                etape_actuelle.est_actuelle = False
                etape_actuelle.save()

                # 2. Logique de flux
                if decision == StatutCirculation.VALIDE:
                    etape_suivante = circulation.etapes.filter(ordre__gt=etape_actuelle.ordre).first()
                    if etape_suivante:
                        etape_suivante.est_actuelle = True
                        etape_suivante.statut = StatutCirculation.EN_COURS
                        etape_suivante.date_reception = timezone.now()
                        etape_suivante.save()
                    else:
                        # Plus d'étapes -> Circuit terminé
                        circulation.statut = StatutCirculation.CLOS
                        circulation.date_fin = timezone.now()
                        circulation.save()

                elif decision == StatutCirculation.REJETE:
                    circulation.statut = StatutCirculation.REJETE
                    circulation.date_fin = timezone.now()
                    circulation.save()

                return Response({'success' : True, 'message': 'Étape traitée avec succès'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
