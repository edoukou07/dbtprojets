# Generated migration for recurrence support in ReportSchedule

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0005_martcreancesagees_martemploiscrees_and_more'),
    ]

    operations = [
        # Add recurrence fields
        migrations.AddField(
            model_name='reportschedule',
            name='is_recurring',
            field=models.BooleanField(default=False, help_text='Indique si le rapport est récurrent'),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_type',
            field=models.CharField(
                choices=[
                    ('none', 'Aucune (envoi unique)'),
                    ('minute', 'Par minute'),
                    ('hour', 'Par heure'),
                    ('daily', 'Quotidien'),
                    ('weekly', 'Hebdomadaire'),
                    ('monthly', 'Mensuel'),
                    ('yearly', 'Annuel'),
                    ('custom', 'Personnalisé'),
                ],
                default='none',
                help_text='Type de récurrence',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_interval',
            field=models.IntegerField(blank=True, help_text='Intervalle (ex: toutes les 5 minutes, toutes les 3 heures)', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_minute',
            field=models.IntegerField(blank=True, help_text='Minute précise (0-59) pour certaines récurrences', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_hour',
            field=models.IntegerField(blank=True, help_text='Heure précise (0-23)', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_days_of_week',
            field=models.JSONField(blank=True, default=list, help_text="Jours de la semaine [0-6] où 0=lundi pour récurrence hebdomadaire"),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_day_of_month',
            field=models.IntegerField(blank=True, help_text='Jour du mois (1-31) ou -1 pour dernier jour', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_week_of_month',
            field=models.IntegerField(blank=True, help_text="Semaine du mois (1-4) pour 'premier lundi'", null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_month',
            field=models.IntegerField(blank=True, help_text='Mois (1-12) pour récurrence annuelle', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_workdays_only',
            field=models.BooleanField(default=False, help_text='Uniquement jours ouvrables'),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_hour_range_start',
            field=models.TimeField(blank=True, help_text='Début de plage horaire', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_hour_range_end',
            field=models.TimeField(blank=True, help_text='Fin de plage horaire', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_hour_range_interval',
            field=models.IntegerField(blank=True, help_text='Intervalle dans la plage (en minutes)', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='recurrence_end_date',
            field=models.DateTimeField(blank=True, help_text='Date de fin optionnelle', null=True),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='parent_schedule',
            field=models.ForeignKey(
                blank=True,
                help_text='Référence au rapport parent pour les occurrences',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='occurrences',
                to='analytics.reportschedule'
            ),
        ),
        migrations.AddField(
            model_name='reportschedule',
            name='occurrence_number',
            field=models.IntegerField(default=1, help_text="Numéro d'occurrence dans la série"),
        ),
    ]

