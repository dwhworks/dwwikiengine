[home](../) /
[docs](./) /
sqlinline

SQL Inline
==========

### `{sqlinline}` ###

Inserts SQL results as is.

Syntax:

<div class="colored-code">
<code>
 {sqlinline}
select
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id between date('now', '-1 day') and date('now')
 {sqlinline}
</code>
</div>

Result:

{sqlinline: db=mydwh}
select
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id between date('now', '-1 day') and date('now')
{sqlinline}

Column values are separated by spaces. Rows are separated by linefeed character (unix style end of line).
See above - the browser replaces linefeed with space.

The text returned by SQL is inserted into the page text,
and then the whole page is passed to markdown for formatting.

This way it's quite easy to get a list, for example:

<div class="colored-code">
<code>
{sqlinline}
select
    '- ' list_mark,
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id between date('now', '-1 day') and date('now')
{sqlinline}
</code>
</div>

Returns

{sqlinline: db=mydwh}
select
    '- ' list_mark,
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id between date('now', '-1 day') and date('now')
{sqlinline}

Column name `list_mark` does not matter, neither do other column names.

Links, headers, bold, italic, lists and anything that markdown understands
works.

Plain HTML also works, since markdown processor doesn't touch it either.

Row limit is the same as with [`{sqltable}`](sqltable#longtables)

The only caveat is that opening and closing tags `{sqlinline}`
must start at the beginning of line. So you cannot
insert a query in the middle of a paragraph.
Still, usually it's not a big problem,
since HTML does not care about line ends.

Example. Header:

<div class="colored-code">
<code>
 &lt;h2&gt;Today: 
{sqlinline: db=mydwh}
select
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id = date('now')
{sqlinline}
 &lt;/h2&gt;
</code>
</div>


<h2>Today: 
{sqlinline: db=mydwh}
select
    d.weekday_name_en,
    d.month_day_num,
    d.month_name_en,
    d.year_num
from
    dates d
where
    d.date_id = date('now')
{sqlinline}
</h2>

<h2 id=params>Params</h2>


Param         |  Description
--------------|-------------
`db`          | Database name or to be precise, database alias to use. When omitted, use default database

<h2 id="urlparams">URL Parameters</h2>

URL parameters may be used the same way as in all other `{sql...}` blocks.
See [`{sqltable}`](sqltable#urlparameters) for details.

<h2 id="longtables">Long Tables</h2>

Note that before being processed by markdown, the whole query results
are read, unlike `{sqltable}` [slow queries](sqltable#slowqueries).

<h2 id="tableexample">Table example</h2>

On the other hand, you are completely in control of displayed results.

Complex table example:

<table>
<tr>
    <th rowspan="2">N</td>
    <th colspan="3">Week</td>
</tr>
<tr>
    <th>Month</th>
    <th>Month day</th>
    <th>Week day</th>
</tr>
{sqlinline: db=mydwh}
select
    '<tr><td>' || d.weekday_num_sun || '</td>',
    '<td>' || d.month_name_en || '</td>',
    '<td>' || d.month_day_num || '</td>',
    '<td>' || d.weekday_name_en || '</td></tr>'
from
    dates d
where
    d.year_num = 2016
    and d.week_num_sun = 14
order by
    d.weekday_num_sun
{sqlinline}
</table>

Well, as you may have noticed, we are getting close to PHP-style
page processing here. But no, we are not making up yet another
programming language. The idea is to use SQL as is,
just add some extra settings to display results in different ways.
Still, here we are using only SQL as a *programming* language,
and then html, markdown, and plain text as *markup* language.

Another example: a plain-text horizontal bar chart:

<div class="colored-code">
 <code>
 RUB    0    10   20   30   40   50   60   70   80   90   100  110  120
 -------+----+----+----+----+----+----+----+----+----+----+----+----+--
{sqlinline: db=mydwh}
-- how to repeat a string in sqlite
-- X - string
-- Y - number of repetitions
-- replace(substr(quote(zeroblob((Y + 1) / 2)), 3, Y), '0', 'X')
select
  curr_code || '    I' || replace(substr(quote(zeroblob((round(current_rate / 2) + 1) / 2)), 3, round(current_rate / 2)), '0', 'I')
from
  curr_rates
where
  date_id = (select max(date_id) from curr_rates)
  and curr_code in ('AUD','CNY','GBP','EUR','USD','TRY')
{sqlinline}
--------+----+----+----+----+----+----+----+----+----+----+----+----+--
 </code>
</div>

I just happen to like plain-text pseudo-graphics for some reason :)

**TODO:** Make a horizontal, i.e. transposed `{sqlinline}`, to produce a vertical bar chart.

Next -> [`{sqllinechart}`](sqllinechart)

-------------------------------------------------------------
[View source](sqlinline.markdown)  
[Printable html](?action=printable)

