[home](../../) /
[docs](../) /
database / 

Sample Database
================

DWWiki comes with a simple SQLite database.
The database file is:

```<dwiki_installation>/db/examples.db
```

It contains a few tables dealing with currencies,
currency rates and gold prices, as a good example
of real numeric data with history.

Tables
------

{sqltable: db=mydwh}
select 
    '[`' || name || '`](' || replace(name,'_','-') || ')' "Table name",
    case
        when name = 'curr_rates' then 'fact'
        when name = 'currencies' then 'dimension'
        when name = 'dates' then 'dimension'
        when name = 'gold_usd' then 'fact'
        else null
    end "Type",
    case
        when name = 'curr_rates' then 'Currency rates to RUB for each currency  
            rated by the Central Bank of Russia for each date from 1992 to April 2016'
        when name = 'currencies' then 'A list of world currencies'
        when name = 'dates' then 'Dates dimension'
        when name = 'gold_usd' then 'London Gold Fixing in USD  
            for each date from 1978 to April 2016'
        else null
    end "Description"
from
    sqlite_master 
where
    type='table'
order by
    name;
{sqltable}

Data Model Diagram
-----------------

Check out my cutting edge, agile, and extremely flexible data model diagram:

<div class="colored-code">
<code>
 +------------+     ==============     +-------+
 | currencies | <---| curr_rates |---> | dates |
 +------------+     ==============     +-------+
                                           ^
                    ==============         |
                    |  gold_usd  |---------+
                    ==============
</code>             
</div>


Next -> [Online Editing](/docs/online-editing)

----------------------------------------------------------------------

[View page source](index.markdown)

        
        
