# apps/documents/services/document_service.py
import os
from django.db import transaction, IntegrityError
from django.utils import timezone
from apps.documents.models import Document, VersionDocument
from config.roles import is_admin, is_superadmin

class DocumentService:

    @staticmethod
    def check_conflict(filename, user):
        name_without_ext, _ = os.path.splitext(filename)
        titre = name_without_ext.replace("_", " ").replace("-", " ").strip()

        # Recherche d'un document existant avec le même titre (insensible à la casse)
        doc_exist = Document.objects.filter(titre__iexact=titre).first()
        return doc_exist, titre

    @staticmethod
    def process_upload(user, files, actions, data):
        results = {
            'created': 0,
            'versioned': 0,
            'overwritten': 0,
            'skipped': 0,
            'errors': []
        }

        # IMPORTANT : Chaque fichier est traité de manière autonome
        for f in files:
            try:
                # Une transaction atomique pour CHAQUE fichier (Savepoint)
                with transaction.atomic():
                    filename = f.name
                    name_without_ext, _ = os.path.splitext(filename)
                    titre = name_without_ext.replace("_", " ").replace("-", " ").strip()

                    action_info = actions.get(filename)
                    action = action_info['action'] if action_info else "create"

                    if action == "skip":
                        results['skipped'] += 1
                        continue

                    # Résolution de la cellule
                    cellule = data.get("cellule")
                    if not (user.is_superuser or getattr(user, 'is_staff', False)):
                        cellule = getattr(user, 'cellule', cellule)

                    # Sécurité pour l'ID de la cellule
                    cell_id = cellule.id if hasattr(cellule, 'id') else cellule

                    # Recherche d'un document existant
                    doc_exist = Document.objects.filter(titre__iexact=titre).first()

                    # ─── LOGIQUE DES CAS MIS À JOUR (GED OPTIMALE) ───

                    # CAS A — Nouvelle version
                    if action == "version" and doc_exist:
                        last_v = doc_exist.versions.order_by("-numero_version").first()
                        next_v = (last_v.numero_version + 1) if last_v else 1

                        VersionDocument.objects.create(
                            titre=f"{doc_exist.titre} - V{next_v}",
                            document=doc_exist,
                            numero_version=next_v,
                            fichier=f,
                            cree_par=user,
                            modifier_par=user,
                            responsable_version_id=data.get("responsable_document_id"),
                        )

                        doc_exist.modifier_par = user
                        doc_exist.save() # Pour mettre à jour Date_miseajour du parent
                        results['versioned'] += 1

                    # CAS B — Écrasement (Mise à jour du fichier de la version actuelle)
                    elif action == "overwrite" and doc_exist:
                        last_v = doc_exist.versions.order_by("-numero_version").first()

                        if last_v:
                            # On écrase le fichier de la version courante (Ex: la V2 existante reçoit le nouveau fichier)
                            last_v.fichier = f
                            last_v.modifier_par = user
                            last_v.save()
                        else:
                            # Système de secours au cas où le document n'avait étonnamment aucune version liée
                            VersionDocument.objects.create(
                                titre=f"{doc_exist.titre} - V1",
                                document=doc_exist,
                                numero_version=1,
                                fichier=f,
                                cree_par=user,
                                modifier_par=user,
                                responsable_version_id=data.get("responsable_document_id"),
                            )

                        doc_exist.modifier_par = user
                        doc_exist.save()
                        results['overwritten'] += 1

                    # CAS C — Création initiale (Document Coquille + Version 1 simultanées)
                    else:
                        # 1. Création de la coquille Document (SANS le champ fichier !)
                        doc = Document.objects.create(
                            titre=titre,
                            type_document_id=data.get("type_document_id"),
                            sous_type_id=data.get("sous_type_id"),
                            theme_id=data.get("theme_id"),
                            cellule_id=cell_id,
                            etat=data.get("etat") or "en attente",
                            niveau_acces=data.get("niveau_acces", "interne"),
                            profil_document=data.get("profil_document") or "consultatif",
                            cree_par=user,
                            metadonnees=data.get("metadonnees"),
                            responsable_document_id=data.get("responsable_document_id"),
                        )

                        if data.get("regles_classement"):
                            doc.regles_classement.set(data.get("regles_classement"))

                        # 2. Création immédiate et obligatoire de la V1 liée
                        VersionDocument.objects.create(
                            titre=f"{doc.titre} - V1",
                            document=doc,
                            numero_version=1,
                            fichier=f,
                            cree_par=user,
                            modifier_par=user,
                            responsable_version_id=data.get("responsable_document_id"),
                        )
                        results['created'] += 1

            except IntegrityError:
                results['errors'].append({
                    'file': f.name,
                    'error': f"Un document nommé '{titre}' existe déjà (conflit d'unicité)."
                })
            except Exception as e:
                results['errors'].append({'file': f.name, 'error': str(e)})

        return results
