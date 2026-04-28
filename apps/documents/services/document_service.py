# apps/documents/services/document_service.py
import os
from django.db import transaction
from django.utils import timezone
from apps.documents.models import Document, VersionDocument
from config.roles import is_admin, is_superadmin

class DocumentService:

    @staticmethod
    # check document conflict logic
    def check_conflict(filename, user):
        pass

    @staticmethod
    def process_upload(user, files, actions, data):
        created_documents = []
        created_versions = []
        skipped = []

        with transaction.atomic():
            for f in files:

                name, _ = os.path.splitext(f.name)
                titre = name.replace("_", " ").replace("-", " ").strip()

                action_info = actions.get(f.name)
                action = action_info['action'] if action_info else "create"

                if action == "skip":
                    skipped.append(titre)
                    continue

                # Résolution de la cellule
                cellule = data.get("cellule")
                if not is_admin(user) and not is_superadmin(user):
                    cellule = user.cellule

                doc_exist = Document.objects.filter(titre__iexact=titre).first()

                # CAS A — Création
                if not doc_exist and action == "create":
                    doc = Document.objects.create(
                        titre=titre,
                        fichier=f,
                        type_document=data.get("type_document"),
                        sous_type=data.get("sous_type"),
                        theme=data.get("theme"),
                        cellule=cellule,
                        etat=data.get("etat") or Document._meta.get_field('etat').default,
                        niveau_acces=data.get("niveau_acces"),
                        profil_document=data.get("profil_document") or Document._meta.get_field('profil_document').default,
                        cree_par=user,
                        metadonnees=data.get("metadonnees") or None,
                        responsable_document=data.get("responsable_document"),
                    )
                    if data.get("regles_classement"):
                        doc.regles_classement.set(data.get("regles_classement"))
                    created_documents.append(doc)

                # CAS B — Nouvelle version
                elif doc_exist and action == "version":
                    last_version = doc_exist.versions.order_by("-numero_version").first()
                    next_version = (last_version.numero_version + 1) if last_version else 1

                    version = VersionDocument.objects.create(
                        titre=f"{doc_exist.titre}-{timezone.now().strftime('%d-%m-%Y_%H-%M-%S')}",
                        document=doc_exist,
                        numero_version=next_version,
                        fichier=f,
                        cree_par=user,
                        responsable_version=data.get("responsable_document"),
                    )
                    created_versions.append(version)

                # CAS C — Écrasement
                elif doc_exist and action == "overwrite":
                    doc_exist.fichier = f
                    doc_exist.modifier_par = user
                    doc_exist.save()
                    created_documents.append(doc_exist)

        return {
            "documents": created_documents,
            "versions": created_versions,
            "skipped": skipped
        }
