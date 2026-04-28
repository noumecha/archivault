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

        # IMPORTANT : On ne met pas le atomic() ici pour que chaque fichier
        # soit indépendant.
        for f in files:
            try:
                # On ouvre une transaction atomique pour CHAQUE fichier (Savepoint)
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

                    # --- LOGIQUE DES CAS ---

                    # CAS A — Nouvelle version
                    if action == "version" and doc_exist:
                        last_v = doc_exist.versions.order_by("-numero_version").first()
                        next_v = (last_v.numero_version + 1) if last_v else 1

                        VersionDocument.objects.create(
                            titre=f"{doc_exist.titre}-v{next_v}",
                            document=doc_exist,
                            numero_version=next_v,
                            fichier=f,
                            cree_par=user,
                            responsable_version_id=data.get("responsable_document_id"),
                        )
                        results['versioned'] += 1

                    # CAS B — Écrasement
                    elif action == "overwrite" and doc_exist:
                        doc_exist.fichier = f
                        doc_exist.modifier_par = user
                        doc_exist.save()
                        results['overwritten'] += 1

                    # CAS C — Création (si n'existe pas OU forcé)
                    else:
                        # Si doc_exist est trouvé mais l'action est "create",
                        # l'IntegrityError sera levée par la DB et capturée plus bas.
                        doc = Document.objects.create(
                            titre=titre,
                            fichier=f,
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
                        results['created'] += 1

            except IntegrityError:
                # Erreur spécifique de doublon SQL (Unique Constraint)
                results['errors'].append({
                    'file': f.name,
                    'error': f"Un document nommé '{titre}' existe déjà (conflit d'unicité)."
                })
            except Exception as e:
                # Autres erreurs (permissions, système de fichiers, etc.)
                results['errors'].append({'file': f.name, 'error': str(e)})

        return results
