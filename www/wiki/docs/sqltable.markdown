[home](../) /
[docs](./) /
sqltable

SQL Table
==========

### `{sqltable}` ###

### Contents ###

- [Available params](#params)
- [Totals](#totals)
- [Using URL parameters in SQL](#urlparameters)
- [HTML in column values](#htmlformatting)
- [Table cell styling](#tablecellstyling)
- [Alternative table footer with totals](#altfooter)
- [Long tables](#longtables)
- [Slow queries](#slowqueries)
- [CSV and XLS download](#csvxls)


This is the most commonly used block. Renders a table out of SQL query.

Syntax:

<div class="colored-code">
<code>
 {sqltable}
 select * from currencies
 where curr_code in ('USD','CNY','AUD')
 {sqltable}
</code>
</div>

Syntax with additional params:

<div class="colored-code">
<code>
 {sqltable: db=dwh | header=no}
 select * from currencies
 where curr_code in ('USD','CNY','AUD')
 {sqltable}
</code>
</div>

<h2 id=params>Available params</h2>


Param         |  Description
--------------|-------------
`db`          | Database name or to be precise, database alias to use. When omitted, use default database
`header`      | `yes` or `no`. To show table header or not. Default - `yes`
`totals`      | Show totals beneath the table. See [totals](#totals)
`orientation` | `vertical` or `horizontal`. How to render the table - vertically as usual, or horizontally. Default - `vertical`. See [orientation](#orientation).
`style`       | Set of html classes used to render the table. See [style](#style)
`delay`       | Time to delay each row output in milliseconds. For debugging purposes mostly. Default - 0. Max value - 10000 (10 seconds)
`id`          | A string to use as a reference to the table in URLs, for example, for xls download. Common URL parameters naming convention allowed.

<h3 id="orientation">Orientation</h3>

You may transpose a table to extend left to right instead of top to bottom.
It's useful for displaying one row of a table with many columns.

Example:

<div class="colored-code">
<code>
 {sqltable: orientation=horizontal}
 select curr_code, curr_name_en, curr_symbol from currencies
 where curr_code in ('USD','CZK','GBP')
 {sqltable}
</code>
</div>

Result:

{sqltable: db=mydwh | orientation=horizontal}
 select curr_code, curr_name_en, curr_symbol from currencies
 where curr_code in ('USD','CZK','GBP')
{sqltable}


<h2 id="totals">Totals</h2>

Looks like this:

<div class="colored-code">
<code>
 {sqltable: totals=Total:,count}
 select curr_code, curr_name_en from currencies
 where curr_code in ('USD','CNY','AUD')
 {sqltable}
</code>
</div>

Result:

{sqltable: db=mydwh | totals=Total:,count}
 select curr_code, curr_name_en from currencies
 where curr_code in ('USD','CNY','AUD')
{sqltable}

The following calculations are implemented:

- `sum`
- `count` - counts non-null values
- `avg`
- `min`
- `max`

If anything else except the above keywords is used in `totals=` attribute,
it is output as is, like the string "Total" above, making it essentially 
a label in the table footer.
Totals are separated by commas in the order of column appearance.
Empty strings are allowed. Example:

```totals=Grand Total,sum,sum,,,count
```

If more totals than the number of query columns are specified,
the extra ones are ignored. If less than column count - all
subsequent columns will have empty footer cells.


You may also make up your own totals out of SQL as described [below](#altfooter).


<h3 id="style">Style</h3>

By default, a table is rendered using the folowing css classes:

- `standard-report-table` - for overall table style
- `standard-report-header` - for table header
- `standard-report-cell` - for table cell
- `standard-report-footer` - for table footer

If you define a different set of classes in a css file referenced from the page header,
you may use them to style the table. Use the common prefix. For above classes, use `standard-report` prefix.

For example, I have defined a `blue-report-...` set of classes in a css file.
Now let's render a table:

<div class="colored-code">
<code>
 {sqltable: style=blue-report}
 select curr_code, curr_name_en from currencies
 where curr_code in ('USD','CNY','AUD')
 {sqltable}
</code>
</div>

Here is what we get:

{sqltable: db=mydwh | style=blue-report}
select curr_code, curr_name_en from currencies
where curr_code in ('USD','CNY','AUD')
{sqltable}

<h2 id="urlparameters">Using URL parameters in SQL</h2>

Any URL parameters in page URL address may be used
in SQL with `${param_name}`. They will be substituted
by param value. See an example below.

<h2 id="htmlformatting">HTML in column values</h2>

When query results are parsed, any `markdown` syntax
used in column values is also parsed and translated into html.
This way it is less verbose to insert links, bold text, lists, etc.

Example:

<div class="colored-code">
<code>
 {sqltable}
 select 
    '**' || curr_code || '**' curr_code,
    '[' || curr_name_en || '](links-example?currcode=' || curr_code || ')' curr_name
 from
    currencies
 where
    curr_code in ('USD','CNY','AUD')
 {sqltable}
</code>
</div>

Result - bold text in `curr_code` column, links with URL params in `curr_name` column:


{sqltable: db=mydwh}
 select 
    '**' || curr_code || '**' curr_code,
    '[' || curr_name_en || '](links-example?currcode=' || curr_code || ')' curr_name
 from
    currencies
 where
    curr_code in ('USD','CNY','AUD')
{sqltable}


Any html in column values is output as is, without html escaping.
Potentially it may lead to javascript injection by malicious user,
or to some other harmful behaviour. The same applies to
using URL parameters directly in queries without parameterized queries.
The following measures generally counter the vulnerability:

1. Know thy users;
2. Limit database permissions for the user which is used by dwwiki engine
   for database queries.
   No updates, no inserts, select is allowed only
   from certain tables/views.
3. Disable javascript use on pages, except javascript from your own sources.
4. Restrict page editing for public users. See item 1.


<h2 id="tablecellstyling">Table cell styling</h2>

For example, I want to highlight some values in a table.
Or I want to right-align the column. I may add any
attributes to the beginning of the column value, as returned by SQL.
They will be added as html table cell attributes.

Syntax:

A space after the opening "`{:`" is mandatory.

<div class="colored-code">
<code>
{: style="background-color:#FFFACD;text-align:right;"}column_value
</code>
</div>

Example:

{sqltable: db=mydwh | orientation=horizontal}
select
    r.date_id,
    r.curr_code,
    r.current_rate,
    case
        when r.current_rate >= r.rate_minus_1 then
            '{:style="background-color:green;color:white;text-align:right"}**+' || round(r.current_rate - r.rate_minus_1, 2) || '**'
        when r.current_rate < r.rate_minus_1 then
            '{:style="background-color:red;color:white;text-align:right"}**' || round(r.current_rate - r.rate_minus_1, 2) || '**'
    end "1 day",
    case
        when r.current_rate >= r.rate_minus_360 then
            '{:style="background-color:green;color:white;text-align:right"}**+' || round(r.current_rate - r.rate_minus_360, 2) || '**'
        when r.current_rate < r.rate_minus_360 then
            '{:style="background-color:red;color:white;text-align:right"}**' || round(r.current_rate - r.rate_minus_360, 2) || '**'

    end "360 days"
from
    curr_rates r
where
    r.date_id = '2016-03-12'
    and r.curr_code = 'GBP'
{sqltable}


### Walkthrough ###

Now look at the query used to produce the above table:

<div class="colored-code">
<code>
 {sqltable: orientation=horizontal}
select
    r.date_id,
    r.curr_code,
    r.current_rate,
    case
        when r.current_rate >= r.rate_minus_1 then
            '{:style="background-color:green;color:white;text-align:right"}**+' ||
            round(r.current_rate - r.rate_minus_1, 2) || '**'
        when r.current_rate < r.rate_minus_1 then
            '{:style="background-color:red;color:white;text-align:right"}**' ||
            round(r.current_rate - r.rate_minus_1, 2) || '**'
    end "1 day",
    case
        when r.current_rate >= r.rate_minus_360 then
            '{:style="background-color:green;color:white;text-align:right"}**+' ||
            round(r.current_rate - r.rate_minus_360, 2) || '**'
        when r.current_rate < r.rate_minus_360 then
            '{:style="background-color:red;color:white;text-align:right"}**' ||
            round(r.current_rate - r.rate_minus_360, 2) || '**'
    end "360 days"
from
    curr_rates r
where
    r.date_id = '2016-03-12'
    and r.curr_code = 'GBP'
 {sqltable}
</code>
</div>

It may look rather complex, but actually it isn't. It just glues together a few small pieces.

First, a column value is taken as is: 

```round(r.current_rate - r.rate_minus_360, 2)
```

Which produces: `9.05`

Then it is wrapped up in double asterisks "**" to make it bold according to markdown syntax.

Now the query produces: `**9.05**`

Then a plus sign and a `style` cell attribute is added at the beginning.
And this is what the database server returns:

```{:style="background-color:red;color:white;text-align:right"}**+9.05**
```

DWWiki engine takes this string, cuts away attributes, converts them into
table cell attributes, then feeds `**+9.05**` to markdown parser.
The final html output now looks like this:

```<td class="standard-report-cell"  style="background-color:green;color:white;text-align:right" ><strong>+9.05</strong></td>
```

You may ask: Why do I need all these complications?
I could have glued up the entire html string from SQL in the first place.

Yes, you could. dwwiki doesn't stand in your way.
That's the whole point. You may start with simple
SQL, then add some coloring to some columns, then add some more
decoration, then more etc... As much as it is needed.
DWWiki was designed for simple users, not programmers.
After a while, simple users become advanced users, and
they still have the required tools.

This is the same way the markdown language was designed.

<h2 id="altfooter">Alternative table footer with totals</h2>

The possibilities of `totals` attribute may seem quite limited.
The idea is - it is a *quick and dirty* way, allowing you to run
a SQL query with aggregated totals in no time.

If you want to make a more sophisticated table footer, you may
combine two queries with `union all` and apply footer style
to the second one.

Example:

### Monthly rate Chinese Yuan (CNY) to Russian Ruble (RUB) for 2015###

{sqltable:  db=mydwh}
select
    z.month_name "Month",
    z.avg_rate "Avg.rate, RUB"
from
(
select
    d.year_num,
    d.month_num,
    d.month_name_en month_name,
    avg(r.current_rate / r.nomination) avg_rate
from
    curr_rates r
    join dates d on r.date_id = d.date_id
        and r.curr_code = 'CNY'
where
    1=1
    and d.year_num = 2015
group by
    d.year_num,
    d.month_num,
    d.month_name_en,
    d.month_num

union all

select
    d.year_num,
    13 month_num,
    '**Year average:**' month_name,
    '{: style="text-align:right;"}**' || round(avg(r.current_rate / r.nomination),2) || '**' avg_rate
from
    curr_rates r
    join dates d on r.date_id = d.date_id
        and r.curr_code = 'CNY'
where
    1=1
    and d.year_num = 2015
group by
    d.year_num
) z
order by
    z.year_num,
    z.month_num;

{sqltable}

Following is the query text. This one is quite long. Yet, it demonstrates
what a real data warehouse query may look like.
Note a `union all`; `select from select` with final sorting,
and artificial 13th month.

Here we are working alongside with our database engine (SQLite here).
Almost no unnecessary abstractions are imposed on us by a "Report Designer".
Still more control is available if we use [`{sqlinline}`](sqlinline) block.

<div class="colored-code">
<code>
 {sqltable}
select
    z.month_name "Month",
    z.avg_rate "Avg.rate, RUB"
from
(
select
    d.year_num,
    d.month_num,
    d.month_name_en month_name,
    avg(r.current_rate / r.nomination) avg_rate
from
    curr_rates r
    join dates d on r.date_id = d.date_id
        and r.curr_code = 'CNY'
where
    1=1
    and d.year_num = 2015
group by
    d.year_num,
    d.month_num,
    d.month_name_en,
    d.month_num

union all

select
    d.year_num,
    13 month_num,
    '**Year average:**' month_name,
    '{: style="text-align:right;"}**' ||
        round(avg(r.current_rate / r.nomination),2) || '**' avg_rate
from
    curr_rates r
    join dates d on r.date_id = d.date_id
        and r.curr_code = 'CNY'
where
    1=1
    and d.year_num = 2015
group by
    d.year_num
) z
order by
    z.year_num,
    z.month_num;

 {sqltable}
</code>
</div>

<a id="longtables"/>

Long tables
-----------

The maximum number of records that are allowed to be displayed
via `{sqltable}` block is limited by a setting `LIMIT_ROWS` in `settings.py`
configuration file for each database. For these examples the limit is set to 500 rows.

See what happens if there are more rows:

[Long table](long-table-example)


<a id="slowqueries"/>

Slow queries
------------

Each table is sent to browser row by row, as soon as the
database delivers it. If a query is slow, or connection is slow
you will see results appearing row by row as soon as they arrive
from database. As an additional safeguard, the query
execution time is limited to a value, specified in `settings.py`.
Here it is limited to 10 seconds.

See progressive loading in action:

[Slow query](slow-table-example)


<a id="csvxls"/>

CSV and XLS download
--------------------

A table may be downloaded in csv or xls format.

To do so, add an URL parameter `?csvdownload=n`
or `xlsdownload=n`, where `n` is a number of
`{sql...}` block on a page, starting from 1.

Download the 2nd table on this page as:

- [CSV](?csvdownload=2)
- [XLS](?xlsdownload=2)

I know that referencing tables by number on page was not 
a wise choice. We are going to change it to an `id` attribute,
but it's not done yet.

CSV format parameters are set in `settings.py` for each
supported language. Some nations are used to have comma as separator,
some semicolon. Date formats and number formats may be different.

XLS file keeps table totals, if they were specified, as Excel formulas.
The style and format of xls file does not mirror style and format
of the original html table. Maybe we will try to change
it in future, at least partly.

If you open an xls file in OpenOffice or Gnumeric, formulas
are not recalculated by default. Press F9.
MS Excel recalculates formulas on file open by default.

Maximum number of downloadable rows is set to 65000.
You may change it for each database in `settings.py`.
And therefore you may change this number per user or user group,
since different user groups may be configured to use different
database connection parameters.

Next -> [`{sqlinline}`](sqlinline)

-------------------------------------------------------------
[View source](sqltable.markdown)  
[Printable html](?action=printable)

        
