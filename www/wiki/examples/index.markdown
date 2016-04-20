[home](../) /
examples / 


This is simple query

*
{sqlinline}
select
      d.weekday_name_en || ', ' ||
      d.month_name_en || ' ' ||
      d.month_day_num || ', ' ||
      d.year_num
from
    dates d
where
    d.date_id = (select max(date_id) from curr_rates)
{sqlinline}
*

{sqltable}
select
  '**' || r.curr_code || '**' Валюта,
  r.current_rate "RUB",
  case
    when (r.current_rate - r.rate_minus_1) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_1, 2)
    when (r.current_rate - r.rate_minus_1) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_1, 2)
    else
      -- изменений нет
    '-'
  end "1 day",
  case
    when (r.current_rate - r.rate_minus_30) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_30, 2)
    when (r.current_rate - r.rate_minus_30) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_30, 2)
    else
      -- изменений нет
    '-'
  end "30 days",
  case
    when (r.current_rate - r.rate_minus_90) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_90, 2)
    when (r.current_rate - r.rate_minus_90) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_90, 2)
    else
      -- изменений нет
    '-'
  end "90 days",
  case
    when (r.current_rate - r.rate_minus_180) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_180, 2)
    when (r.current_rate - r.rate_minus_180) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_180, 2)
    else
      -- изменений нет
    '-'
  end "180 days",
  case
    when (r.current_rate - r.rate_minus_360) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_360, 2)
    when (r.current_rate - r.rate_minus_360) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_360, 2)
    else
      -- изменений нет
    '-'
  end "360 days",
  case
    when (r.current_rate - r.rate_minus_360) > 0 then
      '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
      cast(round((r.current_rate - r.rate_minus_360)/r.rate_minus_360 * 100,0) as integer) || '%'
    when (r.current_rate - r.rate_minus_360) < 0 then
      '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
      cast(round((r.current_rate - r.rate_minus_360)/r.rate_minus_360 * 100,0) as integer) || '%'
    else
      -- изменений нет
    '-'
  end "360 days,%",
  case
    when (r.current_rate - r.rate_minus_720) > 0 then
      '{: style="color:green;text-align:right;"}+' || round(r.current_rate - r.rate_minus_720, 2)
    when (r.current_rate - r.rate_minus_720) < 0 then
      '{: style="color:red;text-align:right;"}' || round(r.current_rate - r.rate_minus_720, 2)
    else
      -- изменений нет
    '-'
  end "720 days",
  case
    when (r.current_rate - r.rate_minus_720) > 0 then
      '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
      cast(round((r.current_rate - r.rate_minus_720)/r.rate_minus_720 * 100,0) as integer) || '%'
    when (r.current_rate - r.rate_minus_720) < 0 then
      '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
      cast(round((r.current_rate - r.rate_minus_720)/r.rate_minus_720 * 100,0) as integer) || '%'
    else
      -- изменений нет
    '-'
  end "720 days,%"
from
  curr_rates r
where
  1=1
  and r.curr_code in ('USD','GBP','EUR', 'CNY', 'TRY')
  and r.date_id = (
    select max(date_id)
    from curr_rates
  )
order by
  case r.curr_code
    when 'USD' then 1
    when 'GBP' then 2
    when 'EUR' then 3
    else 4
  end
{sqltable}

{sqllinechart: linecolor=green,red,blue,orange,black | grid=both | title=720 days
| ylabel=RUB | height=400 | width=600}
-- transpose curr_code from rows to columns
select
    case
        when d.week_num_mon = 1 then d.year_num
        else null
    end year_mark,
    avg(
    case
        when t.curr_code = 'USD' then t.current_rate / t.nomination
        else null
    end 
    ) "USD",
    avg(
    case
        when t.curr_code = 'GBP' then t.current_rate / t.nomination
        else null
    end 
    ) "GBP",
    avg(
    case
        when t.curr_code = 'EUR' then t.current_rate / t.nomination
        else null
    end 
    ) "EUR",
    avg(
    case
        when t.curr_code = 'CNY' then t.current_rate / t.nomination
        else null
    end 
    ) "CNY",
    avg(
    case
        when t.curr_code = 'TRY' then t.current_rate / t.nomination
        else null
    end 
    ) "TRY"
from
    curr_rates t
    join dates d on t.date_id = d.date_id
where
    1=1
    and d.date_id between date('now', '-720 days') and date('now')
    and t.curr_code in ('USD','GBP','EUR', 'CNY', 'TRY')
group by
    d.year_num,
    d.week_num_mon
order by
    d.year_num,
    d.week_num_mon;
{sqllinechart}

### Gold Fix ###

{sqltable}
select
    '**USD**' currency,
    cast(g.final_price as integer) "current",
    case
        when (g.final_price - g1.final_price) >= 0 then
            '{: style="color:green;text-align:right;"}+' ||
            cast(g.final_price - g1.final_price as integer)
        when (g.final_price - g1.final_price) < 0 then
            '{: style="color:red;text-align:right;"}' ||
            cast(g.final_price - g1.final_price as integer)
    end "1 day",
    case
        when (g.final_price - g360.final_price) >= 0 then
            '{: style="color:green;text-align:right;"}+' ||
            cast(g.final_price - g360.final_price as integer)
        when (g.final_price - g360.final_price) < 0 then
            '{: style="color:red;text-align:right;"}' ||
            cast(g.final_price - g360.final_price as integer)
    end "1 year",
    case
        when (g.final_price - g720.final_price) >= 0 then
            '{: style="color:green;text-align:right;"}+' ||
            cast(g.final_price - g720.final_price as integer)
        when (g.final_price - g720.final_price) < 0 then
            '{: style="color:red;text-align:right;"}' ||
            cast(g.final_price - g720.final_price as integer)
    end "2 years",
    case
        when (g.final_price - g1800.final_price) >= 0 then
            '{: style="color:green;text-align:right;"}+' ||
            cast(g.final_price - g1800.final_price as integer)
        when (g.final_price - g1800.final_price) < 0 then
            '{: style="color:red;text-align:right;"}' ||
            cast(g.final_price - g1800.final_price as integer)
    end "5 years",
    case
        when (g.final_price - g1800.final_price) >= 0 then
            '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
            cast((g.final_price - g1800.final_price) / g1800.final_price * 100 as integer) || '%'
        when (g.final_price - g1800.final_price) < 0 then
            '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
            cast((g.final_price - g1800.final_price) / g1800.final_price * 100 as integer) || '%'
    end "5 years,%",
    case
        when (g.final_price - g3600.final_price) >= 0 then
            '{: style="color:green;text-align:right;"}+' ||
            cast(g.final_price - g3600.final_price as integer)
        when (g.final_price - g3600.final_price) < 0 then
            '{: style="color:red;text-align:right;"}' ||
            cast(g.final_price - g3600.final_price as integer)
    end "10 years",
    case
        when (g.final_price - g3600.final_price) >= 0 then
            '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
            cast((g.final_price - g3600.final_price) / g3600.final_price * 100 as integer) || '%'
        when (g.final_price - g3600.final_price) < 0 then
            '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
            cast((g.final_price - g3600.final_price) / g3600.final_price * 100 as integer) || '%'
    end "10 years,%"
from
  gold_usd g
  join gold_usd g1
    on date(g.date_id, '-1 day') = g1.date_id
  join gold_usd g360
    on date(g.date_id, '-360 days') = g360.date_id
  join gold_usd g720
    on date(g.date_id, '-720 days') = g720.date_id
  join gold_usd g1800
    on date(g.date_id, '-1800 days') = g1800.date_id
  join gold_usd g3600
    on date(g.date_id, '-3600 days') = g3600.date_id
where
  1=1
  and g.date_id = (select max(date_id) from gold_usd)
    
union all

select
    '**RUB**' currency,
    cast(z.rub_price as integer) "current",
    case
        when (z.rub_price - z.rub_price_1) > 0 then
            '{: style="color:green;text-align:right;"}+' || cast(z.rub_price-z.rub_price_1 as integer)
        when (z.rub_price - z.rub_price_1) < 0 then
            '{: style="color:red;text-align:right;"}' || cast(z.rub_price-z.rub_price_1 as integer)
    end "1 day",
    case
        when (z.rub_price - z.rub_price_360) > 0 then
            '{: style="color:green;text-align:right;"}+' || cast(z.rub_price-z.rub_price_360 as integer)
        when (z.rub_price - z.rub_price_360) < 0 then
            '{: style="color:red;text-align:right;"}' || cast(z.rub_price-z.rub_price_360 as integer)
    end "1 year",
    case
        when (z.rub_price - z.rub_price_720) > 0 then
            '{: style="color:green;text-align:right;"}+' || cast(z.rub_price-z.rub_price_720 as integer)
        when (z.rub_price - z.rub_price_720) < 0 then
            '{: style="color:red;text-align:right;"}' || cast(z.rub_price-z.rub_price_720 as integer)
    end "2 years",
    case
        when (z.rub_price - z.rub_price_1800) > 0 then
            '{: style="color:green;text-align:right;"}+' || cast(z.rub_price-z.rub_price_1800 as integer)
        when (z.rub_price - z.rub_price_1800) < 0 then
            '{: style="color:red;text-align:right;"}' || cast(z.rub_price-z.rub_price_1800 as integer)
    end "5 years",
    case
        when (z.rub_price - z.rub_price_1800) > 0 then
            '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
            cast((z.rub_price-z.rub_price_1800) / z.rub_price_1800 * 100 as integer) || '%'
        when (z.rub_price - z.rub_price_1800) < 0 then
            '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
            cast((z.rub_price-z.rub_price_1800) / z.rub_price_1800 * 100 as integer) || '%'
    end "5 years,%",
    case
        when (z.rub_price - z.rub_price_3600) > 0 then
            '{: style="color:green;text-align:right;"}+' || cast(z.rub_price-z.rub_price_3600 as integer)
        when (z.rub_price - z.rub_price_3600) < 0 then
            '{: style="color:red;text-align:right;"}' || cast(z.rub_price-z.rub_price_3600 as integer)
    end "10 years",
    case
        when (z.rub_price - z.rub_price_3600) > 0 then
            '{: style="color:green;text-align:right;background-color:#FFFACD;"}+' ||
            cast((z.rub_price-z.rub_price_3600) / z.rub_price_3600 * 100 as integer) || '%'
        when (z.rub_price - z.rub_price_3600) < 0 then
            '{: style="color:red;text-align:right;background-color:#FFFACD;"}' ||
            cast((z.rub_price-z.rub_price_3600) / z.rub_price_3600 * 100 as integer) || '%'
    end "10 years,%"
from
(
select
    strftime("%d.%m.%Y", gp.date_id) "date",
    cb.current_rate,
    gp.final_price * cb.current_rate rub_price,
    gp1.final_price * cb1.current_rate rub_price_1,
    gp360.final_price * cb360.current_rate rub_price_360,
    gp720.final_price * cb720.current_rate rub_price_720,
    gp1800.final_price * cb1800.current_rate rub_price_1800,
    gp3600.final_price * cb3600.current_rate rub_price_3600
from
    gold_usd gp
    join curr_rates cb on gp.date_id = cb.date_id
        and cb.curr_code = 'USD'

    -- minus 1 day
    join gold_usd gp1 on date(gp.date_id, '-1 day') = gp1.date_id
    join curr_rates cb1 on gp1.date_id = cb1.date_id and cb1.curr_code = 'USD'

    -- minus 360 days
    join gold_usd gp360 on date(gp.date_id, '-360 days') = gp360.date_id
    join curr_rates cb360 on gp360.date_id = cb360.date_id and cb360.curr_code = 'USD'

    -- minus 720 days
    join gold_usd gp720 on date(gp.date_id, '-720 days') = gp720.date_id
    join curr_rates cb720 on gp720.date_id = cb720.date_id and cb720.curr_code = 'USD'

    -- minus 1800 days
    join gold_usd gp1800 on date(gp.date_id, '-1800 days') = gp1800.date_id
    join curr_rates cb1800 on gp1800.date_id = cb1800.date_id and cb1800.curr_code = 'USD'

    -- minus 3600 days
    join gold_usd gp3600 on date(gp.date_id, '-3600 days') = gp3600.date_id
    join curr_rates cb3600 on gp3600.date_id = cb3600.date_id and cb3600.curr_code = 'USD'
where
    1=1
    and gp.date_id = (select max(date_id) from gold_usd)
) z;
{sqltable}


### Average USD monthly gold fixing for the last 10 years, (3600 days) ###

{sqllinechart: linecolor=red | width=600 | height=400 | legend=no | grid=both
| ylabel=USD / oz | title=Gold Fixing 10 years}
select
    case
        when d.month_num = 1 then d.year_num
        else null
    end x_mark,
    avg(final_price) avg_month_price
from
    gold_usd t
    join dates d on t.date_id = d.date_id
where
    1=1
    and d.date_id >= date('now', '-3600 days')
group by
    d.year_num,
    d.month_num
order by
    d.year_num,
    d.month_num
{sqllinechart}


### Table information ###

-{sqltable}
pragma table_info(curr_rates);
-{sqltable}

