# Generated migration for multiple dashboards support

from django.db import migrations, models


def migrate_dashboard_to_dashboards(apps, schema_editor):
    """Migre les valeurs de dashboard vers dashboards"""
    ReportSchedule = apps.get_model('analytics', 'ReportSchedule')
    for schedule in ReportSchedule.objects.all():
        if schedule.dashboard and (not schedule.dashboards or len(schedule.dashboards) == 0):
            schedule.dashboards = [schedule.dashboard]
            schedule.save(update_fields=['dashboards'])


def migrate_dashboards_to_dashboard(apps, schema_editor):
    """Migration inverse : copie le premier élément de dashboards vers dashboard"""
    ReportSchedule = apps.get_model('analytics', 'ReportSchedule')
    for schedule in ReportSchedule.objects.all():
        if schedule.dashboards and len(schedule.dashboards) > 0 and not schedule.dashboard:
            schedule.dashboard = schedule.dashboards[0]
            schedule.save(update_fields=['dashboard'])


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_userdashboardpermission'),
    ]

    operations = [
        # Ajouter le champ dashboards (JSONField)
        migrations.AddField(
            model_name='reportschedule',
            name='dashboards',
            field=models.JSONField(default=list, blank=True, help_text='Liste des dashboards à inclure dans le rapport'),
        ),
        # Rendre le champ dashboard nullable pour la compatibilité ascendante
        migrations.AlterField(
            model_name='reportschedule',
            name='dashboard',
            field=models.CharField(
                choices=[
                    ('dashboard', 'Tableau de bord'),
                    ('financier', 'Performance Financière'),
                    ('occupation', 'Occupation Zones'),
                    ('clients', 'Portefeuille Clients'),
                    ('operationnel', 'KPI Opérationnels'),
                    ('alerts', 'Alerts Analytics')
                ],
                max_length=50,
                null=True,
                blank=True
            ),
        ),
        # Migration de données : copier les valeurs existantes de dashboard vers dashboards
        migrations.RunPython(
            code=migrate_dashboard_to_dashboards,
            reverse_code=migrate_dashboards_to_dashboard,
        ),
    ]



