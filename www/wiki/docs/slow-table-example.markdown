Slow query
----------

A delay of 0.5 seconds per row
is actually simulated here by using `delay=500`
attribute in `{sqltable}` block.

In real life rows are usually coming up in chunks
after initial delay. What is good about it is
that the text and charts preceeding the slow query
will be already displayed.

Not all browsers always start displaying the page
immediately. Sometimes the same browser may
open the page immediately for the first time,
but wait for a while for the second time. 
It may depend on memory usage, connection speed or God knows
what else.

Generally, however, all browsers work as expected.

{sqltable: db=mydwh | delay=500}
select
   * 
from 
    gold_usd
order by
    date_id
limit 20;
{sqltable}

        
