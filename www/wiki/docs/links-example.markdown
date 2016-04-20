### URL parameters and links ###

URL param `currcode` is used in query below.
You may also use it in page text directly the same way.

Example:

Currency code is ${currcode}.


{sqltable: orientation=horizontal}
select
    r.*
from
    curr_rates r
where
    r.curr_code = '${currcode}'
    and r.date_id = (select max(date_id) 
        from curr_rates 
        where curr_code = '${currcode}'
    )
{sqltable}
