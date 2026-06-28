# apps/documents/api/views/DocumentAPIView.py
from rest_framework import status
from rest_framework.response import Response
from config.api.base_api_view import BaseAPIView
from config.mixins.drf_permissions import DRFRoleRequiredMixin
from ...models import *
from ...services.permissions import DocumentPermissionService
from ...services.document_service import DocumentService as DocBusinessService
from ..serializers import *
import json
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from apps.administration.models import Cellule
from apps.users.models import RoleUtilisateur
from apps.circulation.services.audit_service import AuditService
from apps.circulation.models import ActionAudit, StatutAudit

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
        type_document = params.get('type_document')
        if type_document:
            qs = qs.filter(type_document__id=type_document)
        if date_debut:
            qs = qs.filter(Date_creation__date__gte=date_debut)
        if date_fin:
            qs = qs.filter(Date_creation__date__lte=date_fin)
        if extension:
            qs = qs.filter(versions__fichier__iendswith='.' + extension.lstrip('.')).distinct()
        return super().get_queryset(queryset=qs)

    def retrieve_action(self, request, pk=None, *args, **kwargs):
        instance = get_object_or_404(Document, pk=pk)

        # Vérification permissions via le service mis à jour
        if not DocumentPermissionService.can_view(request.user, instance):
            # 🟢 AUDIT LOG : Tentative de consultation refusée
            AuditService.log(
                request, action=ActionAudit.CONSULTATION, obj=instance,
                statut=StatutAudit.FAILED, details={"motif": "Permission refusée / Niveau d'accès insuffisant"}
            )
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

        # 🟢 AUDIT LOG : Consultation réussie
        AuditService.log(
            request, action=ActionAudit.CONSULTATION, obj=instance,
            details={"etat_au_visionnage": instance.etat, "profil": instance.profil_document}
        )

        return Response({
            'success': True,
            'data': context_data
        })

    def update_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_edit(request.user, instance):
            AuditService.log(
                request, action=ActionAudit.MODIFICATION, obj=instance,
                statut=StatutAudit.FAILED, details={"motif": "Permission de modification refusée"}
            )
            return Response({ "success" : False, "message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        nouveau_fichier = request.FILES.get('fichier') or request.FILES.get('fichiers')
        try:
            with transaction.atomic():
                request.data['modifier_par'] = request.user.id
                serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
                serializer.is_valid(raise_exception=True)
                document_mis_a_jour = serializer.save()

                details_audit = {
                    "type_modification": "metadonnees_fiche",
                    "champs_modifies": list(request.data.keys())
                }
                if nouveau_fichier:
                    last_v = document_mis_a_jour.versions.order_by("-numero_version").first()
                    next_v = (last_v.numero_version + 1) if last_v else 1
                    resp_id = request.data.get("responsable_document") or document_mis_a_jour.responsable_document_id

                    version = VersionDocument.objects.create(
                        titre=f"{document_mis_a_jour.titre} - V{next_v}",
                        document=document_mis_a_jour,
                        numero_version=next_v,
                        fichier=nouveau_fichier,
                        cree_par=request.user,
                        modifier_par=request.user,
                        responsable_version_id=resp_id
                    )
                    details_audit["type_modification"] = "metadonnees_et_fichier"
                    details_audit["nouvelle_version"] = next_v
                    details_audit["nom_fichier"] = nouveau_fichier.name
                AuditService.log(
                    request,
                    action=ActionAudit.MODIFICATION,
                    obj=document_mis_a_jour,
                    details=details_audit
                )
                return Response({
                    "success": True,
                    "message": "Document mis à jour avec succès" if not nouveau_fichier else f"Document mis à jour (Version {next_v} générée)",
                    "data": self.get_serializer(document_mis_a_jour).data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            AuditService.log(
                request, action=ActionAudit.MODIFICATION, obj=instance,
                statut=StatutAudit.FAILED, details={"erreur": str(e)}
            )
            return Response({
                "success": False,
                "message": f"Erreur lors de la mise à jour : {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not DocumentPermissionService.can_delete(request.user, instance):
            return Response({ "success" : False, "message": "Permission refusée"}, status=status.HTTP_403_FORBIDDEN)
        titre_sauvegardé = instance.titre
        response = super().delete_action(request, pk, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_202_ACCEPTED]:
            # 🟢 AUDIT LOG : Document supprimé (On utilise label car l'instance SQL n'existe plus)
            AuditService.log(
                request, action=ActionAudit.SUPPRESSION,
                label=f"[Document] {titre_sauvegardé}",
                details={"document_id": pk, "statut_a_la_suppression": instance.etat}
            )
        return response

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
        results = DocBusinessService.process_upload(request.user, files, actions_map, metadata, request=request)

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

    # 4. Ajouter une tâche (Action rapide)
    def add_tache_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # 🟢 AUDIT LOG : Déclenchement de la création de tâche depuis ce document
        AuditService.log(
            request,
            action=ActionAudit.TACHE,
            obj=instance,
            details={
                "contexte_action": "initiation_tache_via_document",
                "document_titre": instance.titre
            }
        )
        return Response({
            'success': True,
            'message': 'Prêt à ajouter une tâche',
            'document_id': instance.id,
            'titre': instance.titre
        })

    # 5. Ajouter une circulation (Action rapide)
    def add_circulation_action(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # 🟢 AUDIT LOG : Déclenchement d'une mise en circulation depuis ce document
        AuditService.log(
            request,
            action=ActionAudit.CIRCULATION,
            obj=instance,
            details={
                "contexte_action": "initiation_circulation_via_document",
                "document_titre": instance.titre
            }
        )
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
        # Récupération des titres pour documenter précisément l'audit avant destruction
        titres_supprimes = list(Document.objects.filter(id__in=ids).values_list('titre', flat=True))
        deleted_count, _ = Document.objects.filter(id__in=ids).delete()

        # 🟢 AUDIT LOG : Suppression de masse
        AuditService.log(
            request, action=ActionAudit.SUPPRESSION_MASSE,
            label=f"Suppression en masse de {deleted_count} document(s)",
            details={"ids_demandes": ids, "titres_cibles": titres_supprimes}
        )
        deleted_count, _ = Document.objects.filter(id__in=ids).delete()
        return Response({
            'success': True,
            'message': f'{deleted_count} document(s) supprimé(s)',
            'deleted_count': deleted_count
        })
