{{
    config(
        materialized='table',
        unique_key='date_key'
    )
}}

with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2030-12-31' as date)"
       )
    }}
),

dates as (
    select
        cast(date_day as date) as date_full,
        cast(to_char(date_day, 'YYYYMMDD') as integer) as date_key,
        extract(year from date_day) as annee,
        extract(month from date_day) as mois,
        extract(day from date_day) as jour,
        extract(quarter from date_day) as trimestre,
        extract(week from date_day) as semaine,
        extract(dow from date_day) as jour_semaine,
        to_char(date_day, 'Month') as nom_mois,
        to_char(date_day, 'Day') as nom_jour,
        case 
            when extract(month from date_day) between 1 and 3 then 'T1'
            when extract(month from date_day) between 4 and 6 then 'T2'
            when extract(month from date_day) between 7 and 9 then 'T3'
            else 'T4'
        end as libelle_trimestre,
        case 
            when extract(dow from date_day) in (0, 6) then true
            else false
        end as est_weekend,
        case 
            when extract(month from date_day) = 1 and extract(day from date_day) = 1 then 'Jour de l''An'
            when extract(month from date_day) = 5 and extract(day from date_day) = 1 then 'Fête du Travail'
            when extract(month from date_day) = 8 and extract(day from date_day) = 7 then 'Fête de l''Indépendance'
            when extract(month from date_day) = 12 and extract(day from date_day) = 25 then 'Noël'
            else null
        end as jour_ferie
    from date_spine
)

select * from dates
