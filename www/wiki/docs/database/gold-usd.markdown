[home](../../) /
[docs](../) /
[database](./) /
currencies

`gold_usd`
----------

London Gold Fixing prices in USD for every date since 1978 without gaps.

### Fields ###


name              | type	      | null | pk  | fk | comments 
------------------|---------------|------|-----|----|----------------------
`date_id`         | date          | NO   | YES | [`dates`](dates)`.date_id` |       Price date
`final_price`     | numeric(18,2) | NO   |     |  
`final_price_type`| varchar(20)   | NO   |     |    | Can be either `am`, `pm`, or `previous`

### Data Summary ###

See [wikipedia](https://en.wikipedia.org/wiki/Gold_fixing) for what 'AM', or 'PM' price means.
'previous' means there was no fixing on this date, so the previous fixing is carried forward.

Dates loaded:

{sqltable}
select
    min(date_id) "min date",
    max(date_id) "max date",
    count(date_id) "days count"
from
    gold_usd;
{sqltable}


----------------------------------------------------------------------

[View page source](curr-rates.markdown)
