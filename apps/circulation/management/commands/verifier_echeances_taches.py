# apps/circulation/management/commands/verifier_echeances_taches.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.circulation.models import Tache, StatutTache
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = "Vérifie les tâches dont l'échéance est dépassée et envoie des notifications."

    def handle(self, *args, **options):
        maintenant = timezone.now()

        # On cible uniquement les tâches actives qui ont dépassé la date limite
        taches_en_retard = Tache.objects.filter(
            date_echeance__lt=maintenant,
            statut__in=[StatutTache.A_FAIRE, StatutTache.EN_COURS, StatutTache.EN_REVISION]
        ).select_related('assignee_a', 'assignee_par')

        count = 0
        for tache in taches_en_retard:
            deja_notifie = Notification.objects.filter(
                content_type__model='tache',
                object_id=tache.id,
                titre__icontains="Échéance dépassée",
                created_at__date=maintenant.date()
            ).exists()

            if deja_notifie:
                continue

            if tache.statut != StatutTache.EN_RETARD:
                tache.statut = StatutTache.EN_RETARD
                tache.save(update_fields=["statut"])

            if tache.assignee_a:
                Notification.objects.create(
                    destinataire=tache.assignee_a,
                    titre="⚠️ Échéance dépassée - Action requise",
                    message=f"La date limite de la tâche '{tache.titre}' est dépassée depuis le {tache.date_echeance.strftime('%d/%m/%Y à %H:%M')}.",
                    categorie=Notification.Category.TACHE,
                    content_object=tache,
                    url_action=f"/taches/detail/{tache.id}/"
                )

            if tache.assignee_par and tache.assignee_par != tache.assignee_a:
                Notification.objects.create(
                    destinataire=tache.assignee_par,
                    titre="🚨 Alerte Retard : Tâche non traitée",
                    message=f"La tâche '{tache.titre}' assignée à {tache.assignee_a.get_full_name() or tache.assignee_a.username} a dépassé son échéance.",
                    categorie=Notification.Category.TACHE,
                    content_object=tache,
                    url_action=f"/taches/detail/{tache.id}/"
                )

            count += 1

        self.stdout.write(self.style.SUCCESS(f"Traitement terminé : {count} tâche(s) en retard notifiée(s)."))
