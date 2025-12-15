"""
Module pour le calcul des récurrences de rapports programmés
"""
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
import calendar
from django.utils import timezone


def ensure_timezone_aware(dt):
    """S'assure qu'une datetime est timezone-aware"""
    if dt is None:
        return None
    if timezone.is_aware(dt):
        return dt
    return timezone.make_aware(dt)


class RecurrenceCalculator:
    """Classe pour calculer la prochaine occurrence d'un rapport récurrent"""

    DAYS_OF_WEEK = {
        0: MO,  # Lundi
        1: TU,  # Mardi
        2: WE,  # Mercredi
        3: TH,  # Jeudi
        4: FR,  # Vendredi
        5: SA,  # Samedi
        6: SU,  # Dimanche
    }

    @staticmethod
    def is_workday(dt):
        """Vérifie si une date est un jour ouvrable (lundi-vendredi)"""
        return dt.weekday() < 5  # 0-4 = lundi-vendredi

    @staticmethod
    def get_next_workday(dt):
        """Retourne le prochain jour ouvrable"""
        next_day = dt
        while not RecurrenceCalculator.is_workday(next_day):
            next_day += timedelta(days=1)
        return next_day

    @staticmethod
    def get_last_day_of_month(year, month):
        """Retourne le dernier jour d'un mois donné"""
        return calendar.monthrange(year, month)[1]

    @classmethod
    def calculate_next_occurrence(cls, report_schedule, from_datetime=None):
        """
        Calcule la prochaine occurrence basée sur la configuration de récurrence
        
        Args:
            report_schedule: Instance de ReportSchedule
            from_datetime: DateTime à partir duquel calculer (défaut: maintenant)
        
        Returns:
            datetime ou None si aucune occurrence future possible
        """
        if not report_schedule.is_recurring or report_schedule.recurrence_type == 'none':
            return None

        if from_datetime is None:
            from_datetime = timezone.now()
        elif isinstance(from_datetime, datetime):
            # S'assurer que la datetime est timezone-aware
            from_datetime = ensure_timezone_aware(from_datetime)
        else:
            from_datetime = datetime.fromisoformat(str(from_datetime))
            from_datetime = ensure_timezone_aware(from_datetime)

        # Vérifier la date de fin
        if report_schedule.recurrence_end_date:
            end_date = report_schedule.recurrence_end_date
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                end_date = ensure_timezone_aware(end_date)
            if from_datetime >= end_date:
                return None

        # Calculer selon le type
        recurrence_type = report_schedule.recurrence_type

        result = None
        if recurrence_type == 'minute':
            result = cls._calculate_minute_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'hour':
            result = cls._calculate_hour_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'daily':
            result = cls._calculate_daily_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'weekly':
            result = cls._calculate_weekly_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'monthly':
            result = cls._calculate_monthly_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'yearly':
            result = cls._calculate_yearly_recurrence(report_schedule, from_datetime)
        elif recurrence_type == 'custom':
            result = cls._calculate_custom_recurrence(report_schedule, from_datetime)

        # S'assurer que le résultat est timezone-aware
        return ensure_timezone_aware(result)

    @classmethod
    def _calculate_minute_recurrence(cls, report, from_dt):
        """Calcule la récurrence par minute"""
        interval = report.recurrence_interval or 1
        
        # Arrondir à la minute (enlever secondes et microsecondes)
        next_dt = from_dt.replace(second=0, microsecond=0)
        
        # Ajouter directement l'intervalle
        next_dt = next_dt + timedelta(minutes=interval)
        
        # Si la datetime calculée est dans le passé ou maintenant, ajouter encore l'intervalle
        if next_dt <= from_dt:
            next_dt = next_dt + timedelta(minutes=interval)
        
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_hour_recurrence(cls, report, from_dt):
        """Calcule la récurrence par heure"""
        interval = report.recurrence_interval or 1
        
        # Plage horaire
        if report.recurrence_hour_range_start and report.recurrence_hour_range_end:
            return cls._calculate_hour_range_recurrence(report, from_dt)
        
        # Heure fixe avec minute précise
        if report.recurrence_hour is not None:
            minute = report.recurrence_minute or 0
            # Construire la datetime cible avec l'heure et minute spécifiées
            next_dt = from_dt.replace(hour=report.recurrence_hour, minute=minute, second=0, microsecond=0)
            
            # Si la datetime calculée est dans le passé ou maintenant, ajouter l'intervalle
            if next_dt <= from_dt:
                next_dt = next_dt + timedelta(hours=interval)
            
            return ensure_timezone_aware(next_dt)
        
        # Intervalle simple
        next_dt = from_dt.replace(minute=0, second=0, microsecond=0)
        hours_to_add = interval - (next_dt.hour % interval)
        if hours_to_add == interval:
            hours_to_add = 0
        if hours_to_add == 0:
            hours_to_add = interval
        next_dt = next_dt + timedelta(hours=hours_to_add)
        
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_hour_range_recurrence(cls, report, from_dt):
        """Calcule la récurrence dans une plage horaire"""
        start_time = report.recurrence_hour_range_start
        end_time = report.recurrence_hour_range_end
        interval_minutes = report.recurrence_hour_range_interval or 60
        
        current_time = from_dt.time()
        current_date = from_dt.date()
        
        # Si on est avant la plage, commencer au début
        if current_time < start_time:
            next_dt = datetime.combine(current_date, start_time)
        elif current_time >= end_time:
            # Passer au jour suivant
            next_dt = datetime.combine(current_date + timedelta(days=1), start_time)
        else:
            # Dans la plage, calculer la prochaine occurrence
            current_minutes = current_time.hour * 60 + current_time.minute
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            
            minutes_since_start = current_minutes - start_minutes
            intervals_passed = minutes_since_start // interval_minutes
            next_interval = intervals_passed + 1
            next_minutes = start_minutes + (next_interval * interval_minutes)
            
            if next_minutes > end_minutes:
                # Passer au jour suivant
                next_dt = datetime.combine(current_date + timedelta(days=1), start_time)
            else:
                next_hour = next_minutes // 60
                next_minute = next_minutes % 60
                next_dt = datetime.combine(current_date, time(next_hour, next_minute))
        
        # Convertir en timezone-aware en préservant le fuseau horaire de from_dt
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_daily_recurrence(cls, report, from_dt):
        """Calcule la récurrence quotidienne"""
        # Plusieurs heures spécifiques
        if report.recurrence_hour is None and report.recurrence_days_of_week:
            # Plage horaire quotidienne
            if report.recurrence_hour_range_start and report.recurrence_hour_range_end:
                return cls._calculate_hour_range_recurrence(report, from_dt)
            return None
        
        # Heure fixe
        hour = report.recurrence_hour or 0
        minute = report.recurrence_minute or 0
        
        next_dt = from_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_dt <= from_dt:
            next_dt += timedelta(days=1)
        
        # Jours ouvrables uniquement
        if report.recurrence_workdays_only:
            while not cls.is_workday(next_dt):
                next_dt += timedelta(days=1)
        
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_weekly_recurrence(cls, report, from_dt):
        """Calcule la récurrence hebdomadaire"""
        days_of_week = report.recurrence_days_of_week or []
        
        if not days_of_week:
            # Par défaut, même jour de la semaine
            days_of_week = [from_dt.weekday()]
        
        hour = report.recurrence_hour or 0
        minute = report.recurrence_minute or 0
        
        # Convertir les jours en objets dateutil
        byweekday = [cls.DAYS_OF_WEEK.get(day) for day in days_of_week if day in cls.DAYS_OF_WEEK]
        
        if not byweekday:
            return None
        
        # Utiliser rrule pour trouver la prochaine occurrence
        rule = rrule(
            freq=WEEKLY,
            byweekday=byweekday,
            byhour=hour,
            byminute=minute,
            dtstart=from_dt.replace(hour=hour, minute=minute, second=0, microsecond=0),
            count=1
        )
        
        occurrences = list(rule)
        if occurrences and occurrences[0] <= from_dt:
            # Si la première occurrence est passée, prendre la suivante
            rule = rrule(
                freq=WEEKLY,
                byweekday=byweekday,
                byhour=hour,
                byminute=minute,
                dtstart=from_dt + timedelta(days=1),
                count=1
            )
            occurrences = list(rule)
        
        result = occurrences[0] if occurrences else None
        return ensure_timezone_aware(result)

    @classmethod
    def _calculate_monthly_recurrence(cls, report, from_dt):
        """Calcule la récurrence mensuelle"""
        hour = report.recurrence_hour or 0
        minute = report.recurrence_minute or 0
        
        # Jour relatif (ex: 1er lundi, 2ème mercredi)
        if report.recurrence_week_of_month and report.recurrence_days_of_week:
            day_of_week = report.recurrence_days_of_week[0] if report.recurrence_days_of_week else from_dt.weekday()
            week_num = report.recurrence_week_of_month
            
            # Calculer pour le mois courant
            current_month = from_dt.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            first_day = current_month.replace(day=1)
            # Trouver le premier jour de la semaine cible
            target_weekday = cls.DAYS_OF_WEEK.get(day_of_week)
            if target_weekday:
                first_occurrence = first_day + relativedelta(weekday=target_weekday(week_num))
                if first_occurrence < from_dt:
                    # Passer au mois suivant
                    next_month = (current_month + relativedelta(months=1)).replace(day=1)
                    first_occurrence = next_month + relativedelta(weekday=target_weekday(week_num))
                return ensure_timezone_aware(first_occurrence)
        
        # Jour fixe du mois
        day_of_month = report.recurrence_day_of_month
        if day_of_month == -1:
            # Dernier jour du mois
            next_month = from_dt + relativedelta(months=1)
            last_day = cls.get_last_day_of_month(next_month.year, next_month.month)
            next_dt = next_month.replace(day=last_day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_dt <= from_dt:
                next_month = from_dt + relativedelta(months=2)
                last_day = cls.get_last_day_of_month(next_month.year, next_month.month)
                next_dt = next_month.replace(day=last_day, hour=hour, minute=minute, second=0, microsecond=0)
        elif day_of_month:
            # Jour spécifique
            next_dt = from_dt.replace(day=min(day_of_month, 28), hour=hour, minute=minute, second=0, microsecond=0)
            if next_dt <= from_dt:
                next_dt = next_dt + relativedelta(months=1)
            
            # Ajuster si le jour n'existe pas dans le mois (ex: 31)
            last_day = cls.get_last_day_of_month(next_dt.year, next_dt.month)
            if day_of_month > last_day:
                next_dt = next_dt.replace(day=last_day)
        else:
            # Premier jour ouvrable du mois
            if report.recurrence_workdays_only:
                next_month = (from_dt + relativedelta(months=1)).replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
                next_dt = cls.get_next_workday(next_month)
                if next_dt <= from_dt:
                    next_month = (from_dt + relativedelta(months=2)).replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
                    next_dt = cls.get_next_workday(next_month)
            else:
                # Même jour du mois suivant
                next_dt = from_dt + relativedelta(months=1)
                next_dt = next_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_yearly_recurrence(cls, report, from_dt):
        """Calcule la récurrence annuelle"""
        month = report.recurrence_month or from_dt.month
        day = report.recurrence_day_of_month or from_dt.day
        hour = report.recurrence_hour or 0
        minute = report.recurrence_minute or 0
        
        next_dt = from_dt.replace(month=month, day=min(day, 28), hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_dt <= from_dt:
            next_dt = next_dt + relativedelta(years=1)
        
        # Ajuster si le jour n'existe pas (ex: 29 février)
        try:
            next_dt.replace(day=day)
        except ValueError:
            # Si le jour n'existe pas, prendre le dernier jour du mois
            last_day = cls.get_last_day_of_month(next_dt.year, next_dt.month)
            next_dt = next_dt.replace(day=last_day)
        
        return ensure_timezone_aware(next_dt)

    @classmethod
    def _calculate_custom_recurrence(cls, report, from_dt):
        """Calcule la récurrence personnalisée (tous les X jours/semaines)"""
        interval = report.recurrence_interval or 1
        
        # Toutes les X semaines
        if report.recurrence_type == 'custom' and report.recurrence_days_of_week:
            # Toutes les X semaines le même jour
            days = report.recurrence_days_of_week
            if days:
                day_of_week = days[0]
                hour = report.recurrence_hour or 0
                minute = report.recurrence_minute or 0
                
                current_weekday = from_dt.weekday()
                days_until_next = (day_of_week - current_weekday) % (7 * interval)
                if days_until_next == 0 and from_dt.time() >= time(hour, minute):
                    days_until_next = 7 * interval
                
                next_dt = from_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                next_dt += timedelta(days=days_until_next)
                return ensure_timezone_aware(next_dt)
        
        # Tous les X jours
        hour = report.recurrence_hour or 0
        minute = report.recurrence_minute or 0
        next_dt = from_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_dt <= from_dt:
            next_dt += timedelta(days=interval)
        else:
            # Calculer combien de jours ajouter
            days_passed = (from_dt.date() - next_dt.date()).days
            weeks_passed = days_passed // (7 * interval) if interval > 7 else 0
            if weeks_passed == 0:
                next_dt += timedelta(days=interval)
            else:
                next_dt += timedelta(days=(weeks_passed + 1) * (7 * interval))
        
        # Jours ouvrables uniquement
        if report.recurrence_workdays_only:
            while not cls.is_workday(next_dt):
                next_dt += timedelta(days=1)
        
        return ensure_timezone_aware(next_dt)

