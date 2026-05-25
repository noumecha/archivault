# apps/documents/migrations/XXXX_migrate_files_to_versions.py
from django.db import migrations
from django.utils import timezone

def migrer_fichiers_vers_versions(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')
    VersionDocument = apps.get_model('documents', 'VersionDocument')

    documents = Document.objects.all()
    versions_a_creer = []

    for doc in documents:
        # Si le document a un fichier physique et n'a pas encore de versions
        if doc.fichier and not doc.versions.exists():
            versions_a_creer.append(
                VersionDocument(
                    titre=f"{doc.titre} - V1 (Initiale)",
                    document=doc,
                    numero_version=1,
                    fichier=doc.fichier,
                    cree_par=doc.cree_par,
                    modifier_par=doc.modifier_par,
                    responsable_version=doc.responsable_document,
                    Date_creation=doc.Date_creation,
                    Date_miseajour=doc.Date_miseajour
                )
            )

    if versions_a_creer:
        VersionDocument.objects.bulk_create(versions_a_creer)
        print(f"\n[MIGRATION] SUCCESS : {len(versions_a_creer)} documents ont été convertis vers l'architecture V1.")

def reverse_migration(apps, schema_editor):
    # Optionnel : logique inverse si on annule la migration (rollback)
    VersionDocument = apps.get_model('documents', 'VersionDocument')
    VersionDocument.objects.filter(numero_version=1).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0020_alter_document_theme'),
    ]

    operations = [
    ]
