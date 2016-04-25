[home](../../) /
[docs](../) /
[database](./) /
currencies

`currencies`
-------------

The list of world currencies. Not every currency may be listed, but most of them are.

### Fields: ###

name              | type	      | null | pk  | comments 
------------------|---------------|------|-----|----------------------
curr_code         | text          | NO   | YES | Currency code - USD, GBP, etc.
iso_code          | text          | YES  |     | Numeric IDO code - 840,810 etc.
curr_name_en      | text          | YES  |     | Currency name in English
curr_name_ru      | text          | YES  |     | Currency name in Russian
curr_symbol       | text          | YES  |     | Currency symbol - £, ¥ etc.

### Data Summary: ###

{sqltable: db=mydwh}
select
    case
        when c.curr_code = 'XDR' then
            c.curr_code || ' [[1]](specialcurr)'
        else c.curr_code
    end curr_code,
    c.iso_code,
    c.curr_name_en,
    c.curr_symbol
from
    currencies c
order by
    c.curr_code;
{sqltable}

<a id="specialcurr"/>
### Special Currencies ###

**XDR** is a special currency code - *Special Drawing Rights*.
See [wikipedia](https://en.wikipedia.org/wiki/Special_drawing_rights)

----------------------------------------------------------------------

[View page source](currencies.markdown)
