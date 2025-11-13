

with date_spine as (
    





with rawdata as (

    

    

    with p as (
        select 0 as generated_number union all select 1
    ), unioned as (

    select

    
    p0.generated_number * power(2, 0)
     + 
    
    p1.generated_number * power(2, 1)
     + 
    
    p2.generated_number * power(2, 2)
     + 
    
    p3.generated_number * power(2, 3)
     + 
    
    p4.generated_number * power(2, 4)
     + 
    
    p5.generated_number * power(2, 5)
     + 
    
    p6.generated_number * power(2, 6)
     + 
    
    p7.generated_number * power(2, 7)
     + 
    
    p8.generated_number * power(2, 8)
     + 
    
    p9.generated_number * power(2, 9)
     + 
    
    p10.generated_number * power(2, 10)
     + 
    
    p11.generated_number * power(2, 11)
    
    
    + 1
    as generated_number

    from

    
    p as p0
     cross join 
    
    p as p1
     cross join 
    
    p as p2
     cross join 
    
    p as p3
     cross join 
    
    p as p4
     cross join 
    
    p as p5
     cross join 
    
    p as p6
     cross join 
    
    p as p7
     cross join 
    
    p as p8
     cross join 
    
    p as p9
     cross join 
    
    p as p10
     cross join 
    
    p as p11
    
    

    )

    select *
    from unioned
    where generated_number <= 4017
    order by generated_number



),

all_periods as (

    select (
        

    cast('2020-01-01' as date) + ((interval '1 day') * (row_number() over (order by 1) - 1))


    ) as date_day
    from rawdata

),

filtered as (

    select *
    from all_periods
    where date_day <= cast('2030-12-31' as date)

)

select * from filtered


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