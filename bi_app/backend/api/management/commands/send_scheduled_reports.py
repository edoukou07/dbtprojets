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
from analytics.models import ReportSchedule
from api.views import build_email_connection, generate_dashboard_report_pdf
from django.core.mail import EmailMessage
import logging

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
                            pdf_bytes = generate_dashboard_report_pdf(dashboard)
                            filename = f"report_{dashboard}_{report.id}.pdf"
                            msg.attach(
                                filename,
                                pdf_bytes,
                                'application/pdf',
                            )
                    else:
                        # Un seul dashboard : envoyer un seul PDF
                        dashboard = dashboards_list[0] if dashboards_list else report.dashboard
                        pdf_bytes = generate_dashboard_report_pdf(dashboard)
                        
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

