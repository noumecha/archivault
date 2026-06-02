# apps/circulation/api/views/TacheAPIView.py
from datetime import timezone
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import RoleUtilisateur
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..serializers import *
from django.db.models import Q
from ...models import *
from apps.documents.models import VersionDocument
from django.db import transaction
from apps.circulation.services.audit_service import AuditService

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
                    Q(assignee_par__cellule=user.cellule) |
                    Q(assignee_a=user) |
                    Q(assignee_par=user)
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
        """Création d'une tâche avec traçabilité immédiate."""
        self.check_role_permission(request)
        response = super().create_action(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            payload_data = response.data.get('data', {})
            if 'id' in payload_data:
                try:
                    AuditService.log(
                        request, action=ActionAudit.CREATION, label=payload_data.get('titre', ''), statut=StatutAudit.SUCCESS,
                        details={
                            "tache_id": payload_data.get('id'),
                            "document_id": payload_data.get('document'),
                            "assignee_a_id": payload_data.get('assignee_a'),
                            "priorite": payload_data.get('priorite')
                        }
                    )
                except Exception as e:
                    pass
        return response

    def update_action(self, request, pk=None, *args, **kwargs):
        """
        Formulaire Unique : Gère à la fois la modification managériale,
        le traitement par l'assigné, et le versioning automatique.
        """
        self.check_role_permission(request)
        tache = get_object_or_404(Tache, pk=pk)
        data = request.data
        fichier_nouvelle_version = request.FILES.get('fichier_version')
        commentaire_traitement = data.get('commentaire_traitement')
        nouveau_statut = data.get('statut')

        ancien_statut = tache.statut
        version_creee = None

        try:
            with transaction.atomic():
                # ─── CAS 1 : GESTION DU VERSIONING DU DOCUMENT ───
                if fichier_nouvelle_version:
                    document = tache.document

                    # 1. On récupère la dernière version pour incrémenter (si aucune, on commence à 1)
                    derniere_version = document.version_courante
                    prochain_numero = (derniere_version.numero_version + 1) if derniere_version else 1

                    # 2. On crée l'unique enregistrement de version (Zéro duplication de fichier !)
                    VersionDocument.objects.create(
                        titre=f"{document.titre} - {timezone.now().strftime('%Y-%m-%d')} - V{prochain_numero}",
                        document=document,
                        numero_version=prochain_numero,
                        fichier=fichier_nouvelle_version,
                        cree_par=request.user,
                        modifier_par=request.user
                    )

                    # 3. On met à jour uniquement les métadonnées de modification du document parent
                    document.modifier_par = request.user
                    document.save()  # Met à jour le timestamp Date_miseajour

                # ─── CAS 2 : HISTORIQUE ET COMMENTAIRE DE TRAITMENT ───
                # Si le statut change ou si l'assigné soumet un rapport/commentaire
                if commentaire_traitement or (nouveau_statut and nouveau_statut != ancien_statut):
                    CommentaireTache.objects.create(
                        tache=tache,
                        auteur=request.user,
                        contenu=commentaire_traitement or f"Statut mis à jour : {ancien_statut} → {nouveau_statut}",
                        ancien_statut=ancien_statut,
                        nouveau_statut=nouveau_statut or ancien_statut
                    )

                # ─── CAS 3 : MISE À JOUR VIA LE SERIALIZER (Données de base + Accès temporaire) ───
                # On laisse le sérialiseur traiter le reste des champs (titre, assignation, statut...)
                serializer = self.serializer_class(tache, data=data, partial=True, context={'request': request})
                if serializer.is_valid():
                    tache_mise_a_jour = serializer.save()

                    # Gestion de la date de clôture automatique
                    if tache_mise_a_jour.statut == StatutTache.TERMINEE and ancien_statut != StatutTache.TERMINEE:
                        tache_mise_a_jour.date_cloture = timezone.now()
                        tache_mise_a_jour.save()

                    # 🟢 AUDIT LOG : Modification et avancement réussis
                    AuditService.log(
                        request, action=ActionAudit.MODIFICATION, obj=tache_mise_a_jour, statut=StatutAudit.SUCCESS,
                        details={
                            "ancien_statut": ancien_statut,
                            "nouveau_statut": tache_mise_a_jour.statut,
                            "nouveau_commentaire_soumis": bool(commentaire_traitement),
                            "nouvelle_version_document": version_creee.numero_version if version_creee else None
                        }
                    )

                    return Response({
                        'success': True,
                        'message': 'Tâche mise à jour avec succès',
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)

                # 🟢 AUDIT LOG : Échec de validation des données
                AuditService.log(
                    request, action=ActionAudit.MODIFICATION, obj=tache, statut=StatutAudit.FAILED,
                    details={"erreurs_validation": serializer.errors}
                )

                return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 🟢 AUDIT LOG : Échec critique ou technique de l'opération
            AuditService.log(
                request, action=ActionAudit.MODIFICATION, obj=tache, statut=StatutAudit.FAILED,
                details={"erreur_systeme": str(e)}
            )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete_action(self, request, pk=None, *args, **kwargs):
        """Suppression unitaire d'une tâche."""
        self.check_role_permission(request)
        tache = get_object_or_404(Tache, pk=pk)
        label_sauvegarde = str(tache)
        tache_id = tache.id
        response = super().delete_action(request, pk, *args, **kwargs)
        # 🟢 AUDIT LOG : Log après exécution de la suppression définitive
        AuditService.log(
            request, action=ActionAudit.SUPPRESSION, label=label_sauvegarde, statut=StatutAudit.SUCCESS,
            details={"tache_id": tache_id}
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        """Surcharge du point d'accès Détail pour détecter la consultation de la tâche."""
        response = super().retrieve(request, *args, **kwargs)
        tache = self.get_object()

        # Si c'est l'assigné qui consulte la tâche pour la première fois (ou à chaque fois)
        if tache.assignee_a == request.user:
            # Optionnel : On peut ajouter un booléen 'consultee' sur le modèle Tache
            # pour n'envoyer cette notification de consultation QU'UNE seule fois.

            if tache.assignee_par and tache.assignee_par != request.user:
                # Créer une notification à l'attention de l'initiateur pour lui dire que sa tâche est vue
                Notification.objects.create(
                    destinataire=tache.assignee_par,
                    titre="Tâche consultée",
                    message=f"{request.user.get_full_name() or request.user.username} a ouvert et consulté la tâche : {tache.titre}.",
                    categorie=Notification.Category.TACHE,
                    content_object=tache,
                    url_action=f"/taches/detail/{tache.id}/"
                )

        # 🟢 AUDIT LOG : Consultation de la tâche
        AuditService.log(
            request, action=ActionAudit.CONSULTATION, obj=tache,
            statut=StatutAudit.SUCCESS if response.status_code == status.HTTP_200_OK else StatutAudit.FAILED,
            details={"contexte": "vue_detail_tache", "statut_tache": tache.statut}
        )

        return response

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS PERSONNALISÉES
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'bulk_delete': 'action_bulk_delete',
        'log_consultation': 'action_log_consultation',
    }

    def action_log_consultation(self, request, pk=None):
        """
        Horodate la consultation de la tâche UNIQUEMENT si l'utilisateur connecté
        est celui à qui la tâche a été assignée.
        """
        tache = self.get_object() # Récupère la tâche concernée
        user_connecte = request.user

        # 🟢 LA SÉCURITÉ ET L'ANTI-AMBIGUÏTÉ EST ICI :
        if tache.assignee_a == user_connecte:
            # On vérifie si c'est la TOUTE PREMIÈRE consultation
            if not tache.date_premiere_consultation:
                tache.date_premiere_consultation = timezone.now()

                # 🟢 CRÉATION DE LA NOTIFICATION DE LECTURE HIERARCHIQUE
                if tache.assignee_par and tache.assignee_par != user_connecte:
                    Notification.objects.create(
                        destinataire=tache.assignee_par,
                        titre="Tâche consultée",
                        message=f"{user_connecte.get_full_name() or user_connecte.username} a ouvert la tâche : '{tache.titre}'.",
                        categorie=Notification.Category.TACHE,
                        content_object=tache,
                        url_action=f"/taches/detail/{tache.id}/"
                    )

            if hasattr(tache, 'nb_consultations'):
                tache.nb_consultations += 1
            tache.save()

            # 🟢 AUDIT LOG : Consultation officielle (Assigné)
            AuditService.log(
                request, action=ActionAudit.CONSULTATION, obj=tache, statut=StatutAudit.SUCCESS,
                details={
                    "type_consultation": "officielle_assigne",
                    "nb_consultations": getattr(tache, 'nb_consultations', 1)
                }
            )

            return Response({
                'success': True,
                'message': 'Accusé de réception enregistré (Assigné confirmé).'
            }, status=status.HTTP_200_OK)

        # 🟢 AUDIT LOG : Lecture passive / Traçabilité de surveillance
        AuditService.log(
            request, action=ActionAudit.CONSULTATION, obj=tache, statut=StatutAudit.SUCCESS,
            details={
                "type_consultation": "lecture_tiers",
                "statut_tache_au_visionnage": tache.statut,
                "role_consultant": getattr(user_connecte, 'role', 'non_defini')
            }
        )

        return Response({
            'success': True,
            'message': 'Consultation anonyme (Manager/Admin/Tiers).'
        }, status=status.HTTP_200_OK)

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
        # 🟢 AUDIT LOG : Log de l'action de masse
        AuditService.log(
            request, action=ActionAudit.SUPPRESSION_MASSE, statut=StatutAudit.SUCCESS,
            details={
                "ids_demandes": ids,
                "quantite_supprimee": deleted_count
            }
        )
        return Response({
            'success': True,
            'message': f'{deleted_count} tâche(s) supprimée(s)',
            'deleted_count': deleted_count
        })
