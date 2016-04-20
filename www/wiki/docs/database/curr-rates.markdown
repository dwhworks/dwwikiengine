[home](../../) /
[docs](../) /
[database](./) /
curr-rates

## `curr_rates` ##

Foreign currencies rates as set by the Central Bank of Russia.
Exchange rates are in Russian Rubles per `nomination` units of foreign currency. 

### Fields: ###


name              | type	      | null | pk  | fk                        | comments 
------------------|---------------|------|-----|---------------------------|----------------------
date_id           | date 1	 	  | NO   | YES | [`dates`](dates)`.date_id`| Rate date
curr_code         | varchar(10)	  | NO   | YES | [`currencies`](currencies)`.curr_code` | Currency code
nomination        |	integer       | NO   |     |             | Nomination 1, 10, 100 etc. For this day
current_rate      | numeric(18,4) | NO   |     |             | Current rate in Rubles (RUB) for `nomination` units of currency
current_rate_type |	varchar(40)   | NO   |     |             | 'current' if rated for this date, 'previous' if not rated, but taken from previous rated date
rate_minus_1      | numeric(18,4) |	YES  |     |             | Rate for minus 1 day [[1]](#nomchange)
rate_minus_30     | numeric(18,4) |	YES  |     |             | ... 30 days
rate_minus_60     | numeric(18,4) |	YES  |     |             | ... 60 days
rate_minus_90     | numeric(18,4) |	YES  |     |             | ... 90 days
rate_minus_180    | numeric(18,4) |	YES  |     |             | ... 180 days
rate_minus_360    | numeric(18,4) |	YES  |     |             | ... 360 days
rate_minus_720    | numeric(18,4) |	YES  |     |             | ... 720 days

### Continuous dates ###

For each rated currency there are no date gaps, even so as Central Bank
sets exchange rate only from Tuesday to Saturday, except national holidays.
If the currency was not rated on certain date, the previous known
rate is carried forward and the field `current_rate_type` is set to 'previous'.

<a id="nomchange"/>
### Nomination changes ###

When calculating `rate_minus...` fields, the rated nominations
between different dates may change. The rate shown is adjusted for current `date_id` nomination.

### Data Summary ###

{sqltable: totals=Records,sum}
select
    r.curr_code "currency",
    count(r.curr_code) "total days",
    sum(
        case 
            when current_rate_type = 'current' then 1
            else 0
        end
    ) "rated days",
    min(r.date_id) "first date",
    max(r.date_id) "last date",
    min(nomination) "min nomination",
    max(nomination) "max nomination"
from
    curr_rates r
group by
    r.curr_code
order by
    r.curr_code;
{sqltable}

----------------------------------------------------------------------

[View page source](curr-rates.markdown)
