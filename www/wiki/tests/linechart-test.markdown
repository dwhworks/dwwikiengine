Fill Test
=========


{sqllinechart: linecolor=red,blue,green | fillcolor=#f9966b,#99ccff,#99ff99 |
ylabel=RUB | title=Exchange rates
| width=400 | height=320 | grid=both | miny=0
}
select
    case 
        when d.month_day_num = 1 then
            d.month_name_short_en
        -- just marks without a label
        when d.month_day_num = 15 then
            ""
        else null
    end xmark
    ,gbp.current_rate "GBP"
    ,eur.current_rate "EUR"
    ,r.current_rate "USD"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id and eur.curr_code = 'EUR'
    join curr_rates gbp
      on r.date_id = gbp.date_id and gbp.curr_code = 'GBP'
    -- get mondays from dates dimension
    join dates d on r.date_id = d.date_id
where
    r.date_id between '2015-10-01' and '2016-04-01'
    and r.curr_code = 'USD'
order by r.date_id;
{sqllinechart}

