[home](../) /
[docs](./) /
sqllinechart

SQL Line Chart
==============

### `{sqllinechart}` ###

Used to output line graph, or a series of line
graphs out of sql query results.

### Contents ###

- [Introduction](#intro)
- [Parameters](#parameters)
- [Chart Limits](#limits)
- [Markers](#markers)
- [Colors](#colors)
- [Rendering of chart images](#rendering)


<h2 id=intro>Introduction</h2>

Simple example (rather ugly):

{sqllinechart: db=mydwh}
select
    r.date_id,
    r.current_rate "CNY"
from
    curr_rates r
where
    r.date_id between '2016-02-01' and '2016-02-10'
    and r.curr_code = 'CNY'
{sqllinechart}

Look at the code:

<div class="colored-code">
<code>
 {sqllinechart}
select
    r.date_id,
    r.current_rate "CNY"
from
    curr_rates r
where
    r.date_id between '2016-02-01' and '2016-02-10'
    and r.curr_code = 'CNY'
 {sqllinechart}
</code>
</div>

The first column contains x-axis marks, the second (and subsequent)
columns contain y-axis values. The line label is the 2nd column heading.
Look at the query results as is:

{sqltable: db=mydwh}
select
    r.date_id,
    r.current_rate "CNY"
from
    curr_rates r
where
    r.date_id between '2016-02-01' and '2016-02-10'
    and r.curr_code = 'CNY'
{sqltable}

Now let's add the second line, add color to both,
add y-axis label and the chart title.

The second line is the third column in SQL.

{sqllinechart: db=mydwh | linecolor=green,blue | ylabel=RUB | title=Exchange rates}
select
    r.date_id,
    r.current_rate "USD",
    eur.current_rate "EUR"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id
where
    r.date_id between '2016-02-01' and '2016-02-10'
    and r.curr_code = 'USD'
    and eur.curr_code = 'EUR'
order by r.date_id;
{sqllinechart}

The code:

<div class="colored-code">
<code>
 {sqllinechart: linecolor=green,blue | ylabel=RUB | title=Exchange rates}
select
    r.date_id,
    r.current_rate "USD",
    eur.current_rate "EUR"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id
where
    r.date_id between '2016-02-01' and '2016-02-10'
    and r.curr_code = 'USD'
    and eur.curr_code = 'EUR'
order by r.date_id;
 {sqllinechart}
</code>
</div>

Now let's deal with x-axis marks. I would like to
make a time span a little longer, say, 6 months.
In which case, I would see a lot of lables for
dates below x-axis, obscuring each other.
So I want to output only the first day of each month as an x-axis mark.

At the same time, let's make the chart image a bit smaller
in size.

And add both grid lines to the chart canvas.

{sqllinechart: db=mydwh | linecolor=blue,green |
ylabel=RUB | title=Exchange rates
| width=400 | height=320 | grid=both | miny=50
}
select
    case 
        when d.month_day_num = 1 then
            d.month_name_short_en
        -- just marks without a label
        when d.month_day_num = 15 then
            ""
        else null
    end xmark,
    eur.current_rate "EUR",
    r.current_rate "USD"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id
    -- get mondays from dates dimension
    join dates d on r.date_id = d.date_id
where
    r.date_id between '2015-10-01' and '2016-04-01'
    and r.curr_code = 'USD'
    and eur.curr_code = 'EUR'
order by r.date_id;
{sqllinechart}

The code:

<div class="colored-code">
<code>
{sqllinechart: linecolor=green,blue |
ylabel=RUB | title=Exchange rates
| width=400 | height=320 | grid=both
}
select
    -- x-marks:
    case 
        -- mark the first day of month
        when d.month_day_num = 1 then
            d.month_name_short_en
        -- just marks without a label for 15th of every month
        when d.month_day_num = 15 then
            ""
        -- no marks for other days
        else null
    end xmark,
    r.current_rate "USD",
    eur.current_rate "EUR"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id
    -- get mondays from dates dimension
    join dates d on r.date_id = d.date_id
where
    r.date_id between '2015-10-01' and '2016-04-01'
    and r.curr_code = 'USD'
    and eur.curr_code = 'EUR'
order by r.date_id;
{sqllinechart}
</code>
</div>

Note, that if you specify NULL in the first SQL column,
the x-axis mark will not appear. Yet, if you specify
a space or an empty string, the mark will appear,
but you won't see any label to it.


### Fills ###

We may also fill the area with colors by specifying `fillcolor` parameter:

{sqllinechart: db=mydwh | linecolor=red,blue,green | fillcolor=#f9966b,#99ccff,#99ff99 |
ylabel=RUB | title=Exchange rates
| width=500 | height=320 | grid=both | miny=0
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

*Note:*  

All lines and all filled areas are drawn according to the column order.
So the second filled area may completely obscure the first one. Yet the
line itself is still visible. See below:

{sqllinechart: db=mydwh | linecolor=red,blue,green | fillcolor=#f9966b,#99ccff,#99ff99 |
ylabel=RUB | title=Exchange rates
| width=400 | height=320 | grid=both | miny=50
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
    ,r.current_rate "USD"
    ,eur.current_rate "EUR"
from
    curr_rates r
    join curr_rates eur
      on r.date_id = eur.date_id and eur.curr_code = 'EUR'
    -- get mondays from dates dimension
    join dates d on r.date_id = d.date_id
where
    r.date_id between '2015-10-01' and '2016-04-01'
    and r.curr_code = 'USD'
order by r.date_id;
{sqllinechart}


The following shows all the available parameters:

<h2 id="parameters">Parameters</h2>

<table>
    <tr>
        <th>Parameter</th>
        <th>Comments</th>
    </tr>
    <tr>
        <td><code>db</code></td>
        <td>The database to connect to. Specified in <code>settings.py</code>
        configuration file.<br/>
        All available databases should be published
        by administrators as part of database documentation.
        </td>
    </tr>
    <tr>
        <td><code>title</code></td>
        <td>The chart title which is shown above the chart.
        </td>
    </tr>
    <tr>
        <td><code>xlabel</code></td>
        <td>x-axis label, shown beneath x-axis</td>
    </tr>
    <tr>
        <td><code>ylabel</code></td>
        <td>y-axis label, shown to the left of y-axis</td>
    </tr>
    <tr>
        <td><code>width</code></td>
        <td>Chart width in pixels</td>
    </tr>
    <tr>
        <td><code>height</code></td>
        <td>Chart height in pixels</td>
    </tr>
    <tr>
        <td><code>linecolor</code></td>
        <td>Colors for all lines, separated by comma.
        E.g.: <code>linecolor=green,red,yellow</code>.<br/>
        Default line color is black. If the engine doesn't
        understand the specified color, the color will be gray.
        </td>
    </tr>
    <tr>
        <td><code>fillcolor</code></td>
        <td>Fill colors for all lines, separated by comma.
        E.g.: <code>fillcolor=green,red,yellow</code>.<br/>
        Default fill color is 'none'. If the engine doesn't
        understand the specified color, the area will not be filled.
        </td>
    </tr>
    <tr>
        <td><code>linewidth</code></td>
        <td>Widths for all lines in pixels, separated by comma.
        E.g.: <code>linewidth=1,1,2</code>
        </td>
    </tr>
    <tr>
        <td><code>legend</code></td>
        <td>Show legend on chart. Can be <code>yes</code> or <code>no</code>.
        Default - <code>yes</code>. Line labels are column names from SQL.<br/>
        Legend position on chart canvas is automatic. E.g.: <code>legend=no</code>
        </td>
    </tr>
    <tr>
        <td><code>fontsize</code></td>
        <td>Font size in pixels for all chart text. Default: 10
        </td>
    </tr>
    <tr>
        <td><code>miny</code></td>
        <td>Minimum y value to display. Default: automatic.
        </td>
    </tr>
    <tr>
        <td><code>maxy</code></td>
        <td>Maximum y value to display. Default: automatic.
        </td>
    </tr>
    <tr>
        <td><code>grid</code></td>
        <td>Display grid on chart. Allowed values: <code>x,y,both</code>.
        If the parameter is not specified, there will be no grid lines,<br/>
        which is the default behaviour.
        </td>
    </tr>
    <tr>
        <td><code>marker</code></td>
        <td>Show markers for each point on a line for each line.
        Separated by commas. Example: <code>marker=o,,^</code>
        See <a href="#markers">markers</a>.
        </td>
    </tr>
</table>

<h2 id="limits">Chart Limits</h2>

The maximum number of points per line, which means
the maximum number of rows per query is limited to 20000.
All rows exceeding this value will be silently ignored.
This value may be changed in library source code.
Maybe, we will move this limitation to database connection
parameters in `settings.py` if there will be such a requirement.

The maximum number of lines per chart, which means the
columns in SQL query is limited to 20. This is also
currently hardcoded in the library source code. Extra query
columns will be silently ignored.

<h2 id="markers">Markers</h2>

As we are using [matplotlib] [1] python library to draw charts,
the available markers are the same as fully documented [here] [2].

[1]: http://matplotlib.org
[2]: http://matplotlib.org/api/markers_api.html 

Here is a short table of commonly used markers:

marker   |  description
---------|-----------------
”.”	     | point
“o”      | circle
“v”      | triangle_down
“^”      | triangle_up
“<”      | triangle_left
“>”      | triangle_right
"*"      | star
"d"      | thin diamond

{sqllinechart: db=mydwh | linecolor=green,0.75,#DC143C,orange,y,brown,lime,black
| miny=-20 | maxy=100 | marker=.,o,v,^,<,>,*,d | title=Markers example
| linewidth=,,3,,,,0}
select
    strftime("%d", z.date_id) date_id,
    sum(z.usd) "USD as .",
    sum(z.aud) "AUD as o",
    sum(z.dkk) "DKK as v",
    sum(z.nok) "NOK as ^",
    sum(z.sek) "SEK as <",
    sum(z.sgd) "SGD as >",
    sum(z.kzt) "KZT as *",
    sum(z.krw) "KRW as d"
from
(
select
    r.date_id,
    case
        when r.curr_code = 'USD' then r.current_rate 
        else 0
    end usd,
    case
        when r.curr_code = 'AUD' then r.current_rate 
        else 0
    end aud,
    case
        when r.curr_code = 'DKK' then r.current_rate 
        else 0
    end dkk,
    case
        when r.curr_code = 'NOK' then r.current_rate 
        else 0
    end nok,
    case
        when r.curr_code = 'SEK' then r.current_rate 
        else 0
    end sek,
    case
        when r.curr_code = 'SGD' then r.current_rate 
        else 0
    end sgd,
    case
        when r.curr_code = 'KZT' then r.current_rate 
        else 0
    end kzt,
    case
        when r.curr_code = 'KRW' then r.current_rate 
        else 0
    end krw
from
    curr_rates r
where
    r.date_id between '2016-03-10' and '2016-03-18'
    and r.curr_code in ('USD','AUD','DKK','NOK','SEK','SGD','KZT','KRW')
) z
group by
    z.date_id
;
{sqllinechart}

Note, how the 'KZT' line is not shown, because I have set linewidth to zero.

<div class="colored-code">
<code>
{sqllinechart: title=Markers example
|linecolor=green,0.75,#DC143C,orange,y,brown,lime,black
| miny=-20 | maxy=100 
| marker=.,o,v,^,<,>,*,d
| linewidth=,,3,,,,0}
...
long sql. See <a href="sqllinechart.markdown">page source</a> for full view.
...
 {sqllinechart}
</code>
</div>

<h2 id="colors">Colors</h2>

Line colors can be specified in different ways:

1. As a basic color name, like green, red, blue, etc...
2. As a shade of black: 0.75, 0.5, etc...
3. As html color code: #dc143c, etc...
4. Basic color names may also be specified as one-letter code:
    - b: blue
    - g: green
    - r: red
    - c: cyan
    - m: magenta
    - y: yellow
    - k: black
    - w: white

See example above, where all 4 options were used.

For full description see [matplotlib colors](http://matplotlib.org/api/colors_api.html).


<h2 id="rendering">Rendering of chart images</h2>

A chart is represented on a page as a PNG image.
No javascript is used, nor any dynamic rendering techniques,
like SVG or flash.

More than that, any graph image is **embedded** into HTML page,
encoded as base64 string. This is quite useful, if you
have a long page with multiple graphs, a long SQL table,
and a heavy SQL query into the bargain.

This way, the page is always rendered sequentially from top
to bottom. The server uses only one database connection at any
given moment while processing the page.

Graph images appear as soon as they are ready.
All of this combined:

1. gives smooth loading of resource-intensive pages
2. saves on database server resources and processing time.

Don't forget, we give direct database access
to all users, some of whom may be not as profficient at SQL
as we would have wished. See also [slow queries](tables#slowqueries)

### Direct links to graphs ###

A useful feature would have been if we could link
from another web page directly to graph image. It is on
our short list of requirements, but not yet quite ready for release.

With direct links we must also implement some kind of caching of images, since
the server load may grow unexpectedly having requests from all over the globe.

Next -> [`{sqlbarchart}`](sqlbarchart)

-------------------------------------------------------------
[View source](sqllinechart.markdown)  
[Printable html](?action=printable)
