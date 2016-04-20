[home](../) /
[docs](./) /
sqlbarchart

SQL Bar Chart
==============

### `{sqlbarchart}` ###

Outputs SQL query as a vertical bar chart.

### Contents ###

- [Introduction](#intro)
- [Grouped Bars](#groupedbars)
- [Stacked Bars](#stackedbars)
- [Parameters](#parameters)
- [Limits](#limits)
- [Other details](#other)


<h2 id="intro">Introduction</h2>

A bare query example (ugly):

{sqlbarchart}
select
    date_id,
    current_rate
from
    curr_rates
where
    curr_code = 'UAH'
    and date_id between '2014-02-03' and '2014-02-13'
order by
    date_id;
{sqlbarchart}

Source code:

<div class="colored-code">
<code>
 {sqlbarchart}
select
    date_id,
    current_rate
from
    curr_rates
where
    curr_code = 'UAH'
    and date_id between '2015-12-03' and '2015-12-13'
order by
    date_id;
 {sqlbarchart}
</code>
</div>

The first column is the x-axis bar label, the second - bar height.
By default bar color is gray. You may specify bar color for each bar
in the third column. Example:

{sqlbarchart: title=USD to RUB in 2015
| ylabel=RUB
| width=500 | height=320
| xtickrotation=0
}
select
    d.month_name_short_en,
    avg(r.current_rate),
    case
        when avg(r.current_rate) < 52 then 'green'
        when avg(r.current_rate between 52 and 53.99) then 'lime'
        when avg(r.current_rate between 54 and 57.99) then 'yellow'
        when avg(r.current_rate between 58 and 59.99) then '#FFD801'
        when avg(r.current_rate between 60 and 62.99) then 'orange'
        when avg(r.current_rate between 63 and 65.99) then '#F88017'
        when avg(r.current_rate between 66 and 66.99) then '#ff3333'
        else 'red'
    end color
from
    curr_rates r
    join dates d on r.date_id = d.date_id
where
    r.curr_code = 'USD'
    and d.year_num = 2015
group by
    d.month_num,
    d.month_name_short_en
order by
    d.month_num;
{sqlbarchart}

Look how this query results look as a table:

{sqltable}
select
    '`' || d.month_name_short_en || '`' "month",
    '`' || round(avg(r.current_rate),2) || '`' avg_rate,
    case
        when avg(r.current_rate) < 52 then '`green`'
        when avg(r.current_rate between 52 and 53.99) then '`lime`'
        when avg(r.current_rate between 54 and 57.99) then '`yellow`'
        when avg(r.current_rate between 58 and 59.99) then '`#FFD801`'
        when avg(r.current_rate between 60 and 62.99) then '`orange`'
        when avg(r.current_rate between 63 and 65.99) then '`#F88017`'
        when avg(r.current_rate between 66 and 66.99) then '`#ff3333`'
        else 'red'
    end color
from
    curr_rates r
    join dates d on r.date_id = d.date_id
where
    r.curr_code = 'USD'
    and d.year_num = 2015
group by
    d.month_num,
    d.month_name_short_en
order by
    d.month_num;
{sqltable}

Column names do not matter (yet). What matters is the order of columns.
For naming bar colors see explanation on [sql line chart colors](sqllinechart#colors).

<h2 id="groupedbars">Grouped Bars</h2>

If you specify more than three columns in a query, the engine
will try to produce a group of bars for each position (query row).

In this case the order of query columns remains the same:

1. x labels;
2. first bar value
3. first bar color
4. second bar value
5. second bar color
6. etc...

In this case column names may matter, if you want to display a legend.
See an example:

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

Column names are used as legend labels.

See the above chart as a table:

{sqltable}
select
    d.month_name_short_en,
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
{sqltable}

<h2 id="stackedbars">Stacked Bars</h2>

Bars in bar groups may be displayed not side by side, but on top of one another.
To do it, you must specify `stacked=yes` in parameters.

See an example below. This is the same query as the previous one.

{sqlbarchart: title=USD,GBP,EUR to RUB in 2015
| ylabel=RUB
| xlabel=month
| width=400 | height=380
| xtickrotation=30
| legend=yes
| legendlocation=lower left
| fontsize=10
| barwidth=0.8
| stacked=yes
}
select
    d.month_name_short_en,
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

Bars are drawn literally one over the other, not one on top of the other.
So if the second bar column in a query is greater than the first one,
it will obscure the second completely.

Here is what the previous chart will look like if we change the
order of USD and EUR columns.

{sqlbarchart: title=USD,GBP,EUR to RUB in 2015
| ylabel=RUB
| xlabel=month
| width=400 | height=380
| xtickrotation=30
| legend=yes
| legendlocation=lower left
| fontsize=10
| barwidth=0.8
| stacked=yes
}
select
    d.month_name_short_en,
    avg(
        case
            when r.curr_code = 'GBP' then r.current_rate
            else null
        end
    ) "GBP",
    'red' color_gbp,
    avg(
        case
            when r.curr_code = 'USD' then r.current_rate
            else null
        end
    ) "USD",
    'green' color_usd,
    avg(
        case
            when r.curr_code = 'EUR' then r.current_rate
            else null
        end
    ) "EUR",
    'blue' color_eur
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

This approach may not seem very common, yet it is much more flexible.
After all, you can always simulate a stack of values by adjusting SQL,
which is the way of dwwiki philosophy.

<h2 id="parameters">Parameters</h2>

All the parameters used in `{sqlbarchart}` block:

<table>
    <tr>
        <th>Parameter</th>
        <th>Comments</th>
    </tr>
    <tr>
        <td><code>barwidth</code></td>
        <td>Bar width of each bar or a bar group. Specified in fractions from 0.2 to 1.0.<br/>
        Think of it this way: Each bar or bar group occupies exactly one unit on x-axis.<br/>
        To leave gaps between bars or bar groups on chart, each bar should take less space than one.<br/>
        And here it is specified. Default value is 0.8
        </td>
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
        <td><code>grid</code></td>
        <td>Display grid on chart. If not specified, the grid is not displayed.
        Allowed values:
        <ul>
            <li>x - vertical lines</li>
            <li>y - horizontal lines</li>
            <li>both - both x and y</li>
            <li>none - no grid. Same as when the parameter is absent. Default.</li>
        </ul>
        </td>
    </tr>
    <tr>
        <td><code>legend</code></td>
        <td>Show legend for bar colors. Can be useful with
        multiple bar groups. Can be either `yes` or `no`. Default - `no`.
        </td>
    </tr>
    <tr>
        <td><code>legendlocation</code></td>
        <td>Where to place the legend on the chart.
        The following values may be used:
        <ul>
            <li>right</li>
            <li>center left</li>
            <li>upper right</li>
            <li>lower right</li>
            <li>best</li>
            <li>center</li>
            <li>lower left</li>
            <li>center right</li>
            <li>upper left</li>
            <li>upper center</li>
            <li>lower center</li>
        </ul>
        Default is `best` which means the library tries to figure out where to place it,<br/>
        so as not to interfere too much. It may not be where you would like it to be.
        </td>
    </tr>
    <tr>
        <td><code>stacked</code></td>
        <td>If the chart is a series of bar groups, do not show the bars side by side,<br/>
        but stack them together, giving a "stacked bar chart". See below...
        </td>
    </tr>
    <tr>
        <td><code>title</code></td>
        <td>The chart title which is shown above the chart.
        </td>
    </tr>
    <tr>
        <td><code>xlabel</code></td>
        <td>x-axis label, shown below y-axis</td>
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
        <td><code>fontsize</code></td>
        <td>Font size in pixels for all chart text. Default: 10
        </td>
    </tr>
    <tr>
        <td><code>xtickrotation</code></td>
        <td>Rotation of x-axis marks text which goes below the axis in degrees.<br/>
        Can be any number between -90 to 90 degrees. Default: 45 degrees.
        </td>
    </tr>
</table>

<h2 id="limits">Limits</h2>

The total number of bars, that is, the total number of
query records is limited to 100. It is hardcoded in the component code (`sqlbarchartstreamer.py`).

<h2 id="other">Other details</h2>

All in all, bar chart works pretty much the same as `{sqllinechart}` does.
For any details see [`{sqllinechart}`](sqllinechart).

Next -> [Sample Database](/docs/database/)

-------------------------------------------------------------
[View source](sqlbarchart.markdown)  
[Printable html](?action=printable)

        
        
        
        
        

        