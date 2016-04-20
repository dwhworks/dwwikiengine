[home](/) /
chart-test

Charts test
===========

Bar Chart
---------

{sqlbarchart: title=USD,GBP,EUR to RUB in 2015
| ylabel=RUB
| xlabel=month
| width=600 | height=380
| xtickrotation=0
| legend=yes
| legendlocation=lower left
| fontsize=10
| barwidth=0.9
| stacked=no
| grid=y
}
select
    d.month_name_short_en || x'0a' || '''' || substr(d.year_num,3,2) xlabel,
    avg(
        case
            when r.curr_code = 'GBP' then r.current_rate
            else null
        end
    ) "GBP",
    'red' color_gbp,
    avg(
        case
            when r.curr_code = 'EUR' then r.current_rate
            else null
        end
    ) "EUR",
    'blue' color_eur,
    avg(
        case
            when r.curr_code = 'USD' then r.current_rate
            else null
        end
    ) "USD",
    'green' color_usd
from
    curr_rates r
    join dates d on r.date_id = d.date_id
where
    r.curr_code in ('USD','GBP','EUR')
    and d.year_num = 2015
group by
    d.month_num,
    d.month_name_short_en
order by
    d.month_num;
{sqlbarchart}


Line Chart
----------

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
