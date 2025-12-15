"""
Management command pour envoyer automatiquement les rapports programmés.

Ce command doit être exécuté périodiquement (via cron ou un scheduler) pour vérifier
et envoyer les rapports dont la date/heure programmée est arrivée.

Usage:
    python manage.py send_scheduled_reports

Pour l'automatisation, ajoutez dans crontab (toutes les minutes):
    * * * * * cd /path/to/project && python manage.py send_scheduled_reports
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from pathlib import Path
from analytics.models import ReportSchedule
from analytics.recurrence import RecurrenceCalculator
from api.views import build_email_connection, generate_dashboard_report_pdf
from django.core.mail import EmailMessage
import logging
import shutil

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envoie automatiquement les rapports programmés dont la date/heure est arrivée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les rapports qui seraient envoyés sans les envoyer réellement',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        # Récupérer les rapports programmés non encore envoyés
        # Pour les rapports récurrents, on traite les occurrences (pas les parents si déjà envoyés)
        scheduled_reports = ReportSchedule.objects.filter(
            scheduled_at__lte=now,
            sent=False
        ).order_by('scheduled_at')
        
        if not scheduled_reports.exists():
            self.stdout.write(
                self.style.SUCCESS('Aucun rapport programmé à envoyer.')
            )
            return
        
        self.stdout.write(
            f'Nombre de rapports à envoyer: {scheduled_reports.count()}'
        )
        
        sent_count = 0
        failed_count = 0
        
        for report in scheduled_reports:
            try:
                self.stdout.write(f'\nTraitement du rapport: {report.name} (ID: {report.id})')
                self.stdout.write(f'  Programmé pour: {report.scheduled_at}')
                self.stdout.write(f'  Dashboards: {", ".join(report.get_dashboards_list())}')
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('  [DRY RUN] Ce rapport serait envoyé maintenant')
                    )
                    continue
                
                # Vérifier qu'il y a des destinataires
                recipients = [r.strip() for r in (report.recipients or '').split(',') if r.strip()]
                if not recipients:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠ Aucun destinataire défini pour le rapport {report.id}. Ignoré.'
                        )
                    )
                    continue
                
                # Préparer l'envoi
                dashboards_list = report.get_dashboards_list()
                mail_ctx = build_email_connection()
                
                try:
                    connection = mail_ctx['connection']
                    
                    # Fonction helper pour obtenir le PDF (stocké ou généré)
                    def get_pdf_bytes(dashboard_name):
                        """Récupère le PDF depuis le stockage ou le génère si absent"""
                        # Vérifier si le PDF est stocké
                        if report.pdfs_data and dashboard_name in report.pdfs_data:
                            pdf_path = report.pdfs_data[dashboard_name]
                            full_path = Path(settings.MEDIA_ROOT) / pdf_path
                            
                            if full_path.exists():
                                self.stdout.write(f'  → Utilisation du PDF stocké pour {dashboard_name}')
                                with open(full_path, 'rb') as f:
                                    return f.read()
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'  ⚠ PDF stocké introuvable pour {dashboard_name}, génération...'
                                    )
                                )
                        
                        # Fallback : générer le PDF
                        self.stdout.write(f'  → Génération du PDF pour {dashboard_name}')
                        return generate_dashboard_report_pdf(dashboard_name)
                    
                    # Générer les PDFs pour chaque dashboard
                    if len(dashboards_list) > 1:
                        # Plusieurs dashboards : envoyer plusieurs PDFs séparés
                        subject = f"SIGETI - Report: {report.name}"
                        body = f"Veuillez trouver ci-joints les rapports PDF pour les tableaux de bord suivants : {', '.join(dashboards_list)}."
                        
                        msg = EmailMessage(
                            subject=subject,
                            body=body,
                            from_email=mail_ctx['from_email'],
                            to=recipients,
                            connection=connection,
                        )
                        
                        # Attacher un PDF pour chaque dashboard
                        for dashboard in dashboards_list:
                            pdf_bytes = get_pdf_bytes(dashboard)
                            filename = f"report_{dashboard}_{report.id}.pdf"
                            msg.attach(
                                filename,
                                pdf_bytes,
                                'application/pdf',
                            )
                    else:
                        # Un seul dashboard : envoyer un seul PDF
                        dashboard = dashboards_list[0] if dashboards_list else report.dashboard
                        pdf_bytes = get_pdf_bytes(dashboard)
                        
                        subject = f"SIGETI - Report: {report.name}"
                        body = f"Veuillez trouver ci-joint le rapport PDF pour le tableau de bord '{dashboard}'."
                        
                        msg = EmailMessage(
                            subject=subject,
                            body=body,
                            from_email=mail_ctx['from_email'],
                            to=recipients,
                            connection=connection,
                        )
                        
                        filename = f"report_{dashboard}_{report.id}.pdf"
                        msg.attach(
                            filename,
                            pdf_bytes,
                            'application/pdf',
                        )
                    
                    # Envoyer l'email
                    msg.send()
                    email_status = 'sent'
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Email envoyé avec succès à {len(recipients)} destinataire(s)'
                        )
                    )
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi du rapport {report.id}: {str(e)}")
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Erreur lors de l\'envoi: {str(e)}')
                    )
                    email_status = 'failed'
                
                # Mettre à jour le statut du rapport
                if email_status == 'sent':
                    report.sent = True
                    report.sent_at = timezone.now()
                    if mail_ctx['instance']:
                        mail_ctx['instance'].mark_test_result(True)
                    sent_count += 1
                    
                    # Si c'est un rapport récurrent, créer la prochaine occurrence
                    if report.is_recurring and report.recurrence_type != 'none':
                        self._create_next_occurrence(report)
                else:
                    # En cas d'échec, on peut choisir de ne pas marquer comme envoyé
                    # pour permettre une nouvelle tentative plus tard
                    # Ou marquer comme envoyé avec un flag d'erreur
                    # Ici, on marque quand même comme envoyé pour éviter les tentatives infinies
                    report.sent = True
                    report.sent_at = timezone.now()
                    failed_count += 1
                
                report.save()
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement du rapport {report.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Erreur lors du traitement: {str(e)}')
                )
                failed_count += 1
        
        # Résumé
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Résumé:')
        self.stdout.write(f'  Rapports envoyés avec succès: {sent_count}')
        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING(f'  Rapports en échec: {failed_count}')
            )
        self.stdout.write('='*50)

    def _create_next_occurrence(self, report):
        """Crée la prochaine occurrence d'un rapport récurrent"""
        try:
            # Calculer la prochaine occurrence
            next_occurrence_dt = RecurrenceCalculator.calculate_next_occurrence(
                report,
                from_datetime=timezone.now()
            )
            
            if not next_occurrence_dt:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ Aucune prochaine occurrence pour le rapport récurrent {report.id} '
                        f'(date de fin atteinte ou configuration invalide)'
                    )
                )
                return
            
            # Déterminer le rapport parent (le premier de la série)
            parent = report.parent_schedule if report.parent_schedule else report
            
            # Créer le nouveau rapport
            next_report = ReportSchedule(
                name=report.name,
                dashboard=report.dashboard,
                dashboards=report.dashboards.copy() if report.dashboards else [],
                scheduled_at=next_occurrence_dt,
                recipients=report.recipients,
                created_by=report.created_by,
                is_recurring=True,
                recurrence_type=report.recurrence_type,
                recurrence_interval=report.recurrence_interval,
                recurrence_minute=report.recurrence_minute,
                recurrence_hour=report.recurrence_hour,
                recurrence_days_of_week=report.recurrence_days_of_week.copy() if report.recurrence_days_of_week else [],
                recurrence_day_of_month=report.recurrence_day_of_month,
                recurrence_week_of_month=report.recurrence_week_of_month,
                recurrence_month=report.recurrence_month,
                recurrence_workdays_only=report.recurrence_workdays_only,
                recurrence_hour_range_start=report.recurrence_hour_range_start,
                recurrence_hour_range_end=report.recurrence_hour_range_end,
                recurrence_hour_range_interval=report.recurrence_hour_range_interval,
                recurrence_end_date=report.recurrence_end_date,
                parent_schedule=parent,
                occurrence_number=report.occurrence_number + 1,
            )
            next_report.save()
            
            # Copier les PDFs du rapport actuel vers le nouveau (ils seront régénérés au moment de l'envoi si nécessaire)
            if report.pdfs_data:
                try:
                    source_dir = Path(settings.MEDIA_ROOT) / 'reports' / str(report.id)
                    target_dir = Path(settings.MEDIA_ROOT) / 'reports' / str(next_report.id)
                    
                    if source_dir.exists():
                        target_dir.mkdir(parents=True, exist_ok=True)
                        # Copier les fichiers PDF
                        pdfs_data_copy = {}
                        for dashboard_name, pdf_path in report.pdfs_data.items():
                            source_file = source_dir / f"{dashboard_name}.pdf"
                            if source_file.exists():
                                target_file = target_dir / f"{dashboard_name}.pdf"
                                shutil.copy2(source_file, target_file)
                                pdfs_data_copy[dashboard_name] = f"reports/{next_report.id}/{dashboard_name}.pdf"
                        
                        next_report.pdfs_data = pdfs_data_copy
                        next_report.save(update_fields=['pdfs_data'])
                except Exception as e:
                    logger.warning(f"Impossible de copier les PDFs pour l'occurrence suivante: {e}")
                    # Ce n'est pas bloquant, les PDFs seront régénérés au moment de l'envoi
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Prochaine occurrence créée: {next_occurrence_dt.strftime("%Y-%m-%d %H:%M:%S")} '
                    f'(Occurrence #{next_report.occurrence_number})'
                )
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la prochaine occurrence pour le rapport {report.id}: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'  ✗ Erreur lors de la création de la prochaine occurrence: {str(e)}')
            )

