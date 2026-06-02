# apps/circulation/api/views/CirculationAPIView.py
from datetime import timezone
from rest_framework.response import Response
from rest_framework import status
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from config.api.base_api_view import BaseAPIView
from ...models import RoleUtilisateur
from django.shortcuts import get_object_or_404
from ..serializers import *
from django.db.models import Q
from ...models import *
from apps.documents.models import VersionDocument
from django.db import transaction
from datetime import timedelta
from apps.circulation.services.audit_service import AuditService

def est_superieur_hierarchique(user_courant, user_precedent):
    """
    Détermine si user_courant a un rôle strictement supérieur à user_precedent
    selon la hiérarchie de l'application.
    """
    # Cartographie de la hiérarchie (plus le score est élevé, plus le rôle est important)
    hierarchie_roles = {
        RoleUtilisateur.GESTIONNAIRE: 1,
        RoleUtilisateur.RESPONSABLE: 2,
        RoleUtilisateur.SUPERVISEUR: 3,
        RoleUtilisateur.ADMIN: 4,
        RoleUtilisateur.SUPERADMIN: 5,
    }

    # Récupération du rôle principal (ajustez selon votre implémentation réelle de récupération du rôle)
    role_courant = getattr(user_courant, 'role', None)
    role_precedent = getattr(user_precedent, 'role', None)

    score_courant = hierarchie_roles.get(role_courant, 0)
    score_precedent = hierarchie_roles.get(role_precedent, 0)

    return score_courant > score_precedent


class CirculationAPIView(DRFRoleRequiredMixin, BaseAPIView):
    """
    API pour la gestion de la circulation des documents.
    Gère le cycle de vie du circuit et le traitement des étapes.

    Endpoints :

        GET    /api/circulations/              → Liste (paginée, filtrée, recherchée)
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

    def delete_action(self, request, *args, **kwargs):
        circulation = self.get_object()
        if circulation.statut == StatutCirculation.CLOS:
            AuditService.log(
                request, action=ActionAudit.SUPPRESSION, obj=circulation,
                statut=StatutAudit.FAILED, details={"motif": "Tentative de suppression d'un circuit clôturé"}
            )
            return Response({'success': False, 'message': 'Suppression impossible : le circuit est déjà clôturé.'}, status=status.HTTP_403_FORBIDDEN)
        self.check_role_permission(request)
        label_document = str(circulation)
        AuditService.log(request, action=ActionAudit.SUPPRESSION, obj=circulation, statut=StatutAudit.FAILED, label=label_document, details={"id_supprime": circulation.id})
        return super().delete_action(request, *args, **kwargs)

    def update_action(self, request, *args, **kwargs):
        circulation = self.get_object()
        # AJOUT : Si la circulation est retournée à l'état initial, l'initiateur a le droit de la modifier
        # Même si elle était initialement verrouillée.
        is_initiateur = (circulation.initie_par == request.user)
        a_un_retour_initial = circulation.etapes.filter(ordre=1, statut=StatutCirculation.RETOURNE).exists()
        if circulation.statut in [StatutCirculation.CLOS, StatutCirculation.VALIDE]:
            AuditService.log(request, action=ActionAudit.MODIFICATION, obj=circulation, statut=StatutAudit.FAILED, details={"motif": "Circuit clôturé ou validé"})
            return Response({'success': False, 'message': 'Modification impossible : le circuit est déjà clôturé.'}, status=status.HTTP_403_FORBIDDEN)
        # Si le circuit est en cours mais qu'il a subi un retour à l'étape 1, l'initiateur peut réorganiser
        if circulation.statut == StatutCirculation.EN_COURS and a_un_retour_initial and is_initiateur:
            return super().update_action(request, *args, **kwargs)
        if circulation.statut == StatutCirculation.REJETE:
            # 🟢 AUDIT LOG : Modification echouée
            AuditService.log(request, action=ActionAudit.MODIFICATION, obj=circulation, statut=StatutAudit.FAILED, details={"motif": "Circuit rejeté"})
            return Response({'success': False, 'message': 'Modification impossible : le circuit est marqué comme rejeté.'}, status=status.HTTP_403_FORBIDDEN)
        self.check_role_permission(request)
        if PermissionService.can_update_circulation(request.user, circulation):
            return super().update_action(request, *args, **kwargs)
        # 🟢 AUDIT LOG : Modification réussie
        AuditService.log(request, action=ActionAudit.MODIFICATION, obj=circulation, statut=StatutAudit.SUCCESS, details={"methode": request.method})
        return super().update_action(request, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # ACTIONS CUSTOM
    # ─────────────────────────────────────────────────────────────────────────
    custom_actions = {
        'traiter_etape': 'action_traiter_etape',
        'initier_circuit': 'action_initier_circuit',
        'bulk_delete': 'action_bulk_delete',
        'log_consultation': 'action_log_consultation',
    }

    def action_log_consultation(self, request, pk=None):
        """
        Horodate la consultation de l'étape actuelle du circuit
        uniquement si l'utilisateur connecté en est le destinataire.
        """
        circulation = self.get_object()
        etape_actuelle = circulation.etape_actuelle  # Utilise ta property existante
        user_connecte = request.user

        # La traçabilité s'applique si le circuit est en cours et que l'utilisateur est le destinataire actif
        if etape_actuelle and etape_actuelle.destinataire == user_connecte:
            # On vérifie si c'est la TOUTE PREMIÈRE fois qu'il ouvre cette étape
            if not etape_actuelle.date_premiere_consultation:
                etape_actuelle.date_premiere_consultation = timezone.now()

                # 🟢 CRÉATION DE LA NOTIFICATION DE LECTURE HIERARCHIQUE
                # On notifie le créateur du circuit que l'acteur est en train de regarder le document
                if circulation.initie_par and circulation.initie_par != user_connecte:
                    Notification.objects.create(
                        destinataire=circulation.initie_par,
                        titre="Document en cours de lecture",
                        message=f"{user_connecte.get_full_name() or user_connecte.username} a pris connaissance du document pour l'étape {etape_actuelle.ordre}.",
                        categorie=Notification.Category.CIRCULATION,
                        content_object=circulation,
                        url_action=f"/circulations/detail/{circulation.id}/"
                    )

            etape_actuelle.nb_consultations += 1
            etape_actuelle.save()

            # 🟢 AUDIT LOG : Consultation tracée
            AuditService.log(
                request, action=ActionAudit.CONSULTATION, obj=circulation, statut=StatutAudit.SUCCESS,
                details={"type_consultation": "officielle_destinataire", "etape_ordre": etape_actuelle.ordre, "nb_consultations": etape_actuelle.nb_consultations}
            )

            return Response({
                'success': True,
                'message': 'Accusé de réception enregistré pour cette étape.'
            }, status=status.HTTP_200_OK)

        # 🟢 AUDIT LOG : Traçabilité de consultation passive/supervision
        AuditService.log(
            request, action=ActionAudit.CONSULTATION, obj=circulation, statut=StatutAudit.SUCCESS,
            details={
                "type_consultation": "lecture_tiers",
                "etape_ordre": etape_actuelle.ordre if etape_actuelle else None,
                "statut_circuit_au_visionnage": circulation.statut,
                "role_consultant": getattr(user_connecte, 'role', 'non_defini')
            }
        )
        return Response({
            'success': True,
            'message': 'Consultation sans impact enregistrée (Auteur/Admin/Tiers).'
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
        deleted_count, _ = CirculationDocument.objects.filter(id__in=ids).exclude(statut=StatutCirculation.CLOS).delete()
        # 🟢 AUDIT LOG : Suppression de masse
        AuditService.log(request, action=ActionAudit.SUPPRESSION_MASSE, obj=None, statut=StatutAudit.SUCCESS, details={"ids_soumis": ids, "quantite_supprimee": deleted_count})
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
                    statut=StatutCirculation.EN_COURS,
                    date_fin=data.get('date_fin')
                )

                # 2. Créer les étapes
                for i, etape in enumerate(etapes_data):
                    is_first = (i == 0)
                    EtapeCirculation.objects.create(
                        circulation=circulation,
                        titre_etape=etape.get('titre_etape'),
                        destinataire_id=etape.get('destinataire'),
                        ordre=etape.get('ordre', i + 1),
                        statut=StatutCirculation.EN_COURS if is_first else StatutCirculation.EN_ATTENTE,
                        est_actuelle=is_first,
                        date_reception=timezone.now() if is_first else None,
                        date_echeance=etape.get('date_echeance')
                    )

                # 🟢 AUDIT LOG : Initialisation réussie (Placé dans le bloc atomique)
                AuditService.log(
                    request, action=ActionAudit.CREATION, obj=circulation, statut=StatutAudit.SUCCESS, details={"nb_etapes": len(etapes_data), "document_id": data.get('document')}
                )
                return Response(CirculationDocumentSerializer(circulation, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 🟢 AUDIT LOG : Échec technique lors de la création
            AuditService.log(request, action=ActionAudit.CREATION, obj=circulation, statut=StatutAudit.FAILED, details={"erreur": str(e)})
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def action_traiter_etape(self, request, pk=None, *args, **kwargs):
        circulation = get_object_or_404(CirculationDocument, pk=pk)
        etape_actuelle = circulation.etapes.filter(est_actuelle=True).first()
        if circulation.statut in [StatutCirculation.CLOS, StatutCirculation.VALIDE]:
            return Response({
                'success': False,
                'message': 'Ce circuit est déjà clôturé et ne peut plus être traité.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not etape_actuelle:
            return Response({'success': False, 'message': 'Aucune étape active sur ce circuit'}, status=status.HTTP_400_BAD_REQUEST)

        if etape_actuelle.destinataire != request.user and not is_admin(request.user):
            return Response({'success': False, 'message': 'Vous n\'êtes pas le destinataire de cette étape'}, status=status.HTTP_403_FORBIDDEN)

        # Récupération des données
        decision = request.data.get('decision')
        commentaire = request.data.get('commentaire', '')
        delai_heures_soumis = request.data.get('delai_retour_heures')
        nouveau_fichier = request.FILES.get('fichier')

        if decision not in [StatutCirculation.VALIDE, StatutCirculation.REJETE, StatutCirculation.RETOURNE]:
            return Response({'success' : False, 'message': 'Décision invalide'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Mise à jour de l'étape actuelle
                etape_actuelle.statut = decision
                etape_actuelle.commentaire = commentaire
                etape_actuelle.date_traitement = timezone.now()
                etape_actuelle.traite_par = request.user
                etape_actuelle.est_actuelle = False

                # --- LOGIQUE DE VERSIONNEMENT ---
                if decision == StatutCirculation.VALIDE and nouveau_fichier:
                    # Calcul du prochain numéro de version
                    last_ver = etape_actuelle.circulation.document.versions.count()
                    nouvelle_version = VersionDocument.objects.create(
                        document=etape_actuelle.circulation.document,
                        titre=etape_actuelle.circulation.document.titre + " - " + timezone.now().strftime("%Y-%m-%d") + f" - V{last_ver + 1}",
                        fichier=nouveau_fichier,
                        numero_version=last_ver + 1,
                        cree_par=request.user
                    )
                    etape_actuelle.version_produite = nouvelle_version

                etape_actuelle.save()

                # --- LOGIQUE DE FLUX (REJET / RETOUR / VALIDE) ---

                if decision == StatutCirculation.VALIDE:
                    etape_suivante = circulation.etapes.filter(ordre__gt=etape_actuelle.ordre).first()
                    if etape_suivante:
                        self._activer_etape(etape_suivante)
                        circulation.statut = StatutCirculation.EN_COURS
                        circulation.save()
                    else:
                        circulation.statut = StatutCirculation.CLOS
                        circulation.date_fin = timezone.now()
                        circulation.save()

                elif decision in [StatutCirculation.REJETE, StatutCirculation.RETOURNE]:
                    # On cherche l'étape précédente
                    etape_precedente = circulation.etapes.filter(ordre__lt=etape_actuelle.ordre).last()

                    if etape_precedente:
                        nouvelle_date_limite = etape_precedente.date_echeance
                        if est_superieur_hierarchique(request.user, etape_precedente.destinataire):
                            if delai_heures_soumis:
                                nouvelle_date_limite = timezone.now() + timedelta(hours=int(delai_heures_soumis))
                            else:
                                nouvelle_date_limite = timezone.now() + timedelta(days=2)
                            if circulation.date_echeance and nouvelle_date_limite > circulation.date_echeance:
                                nouvelle_date_limite = circulation.date_echeance
                        else:
                            pass
                        self._activer_etape(etape_precedente, nouvelle_date_limite=nouvelle_date_limite)
                        circulation.statut = StatutCirculation.EN_COURS

                    else:
                        # On réactive l'étape 1 mais avec un tag spécifique, ou on permet la modification globale.
                        first_etape = circulation.etapes.filter(ordre=1).first()
                        if first_etape:
                            # On passe le statut à RETOURNE pour signifier à l'initiateur qu'il doit corriger le tir
                            first_etape.statut = StatutCirculation.RETOURNE
                            first_etape.est_actuelle = True # L'étape redevient active visuellement
                            first_etape.save()

                            circulation.statut = StatutCirculation.RETOURNE
                        else:
                            circulation.statut = StatutCirculation.REJETE
                            circulation.date_fin = timezone.now()

                    circulation.save()
                    # 🟢 AUDIT LOG : Décision métier majeure enregistrée
                    AuditService.log(
                        request, action=ActionAudit.TRAITEMENT, obj=circulation,
                        details={
                            "etape_ordre": etape_actuelle.ordre,
                            "decision": decision,
                            "commentaire_longueur": len(commentaire),
                            "nouvelle_version_produite": True if request.FILES.get('fichier') else False
                        }
                    )
                return Response({'success': True, 'message': 'Traitement effectué avec succès'}, status=status.HTTP_200_OK)

        except Exception as e:
            # 🟢 AUDIT LOG : Échec lors du traitement
            AuditService.log(request, action=ActionAudit.TRAITEMENT, obj=circulation, statut=StatutAudit.FAILED, details={"erreur": str(e), "decision_tentée": decision})
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _activer_etape(self, etape, nouvelle_date_limite=None):
        """Méthode utilitaire pour activer une étape"""
        etape.est_actuelle = True
        etape.statut = StatutCirculation.EN_COURS
        etape.date_reception = timezone.now()
        if nouvelle_date_limite:
            etape.date_echeance = nouvelle_date_limite
        etape.save()
