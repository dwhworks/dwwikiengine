[home](/) /
[docs](/docs/) /
sql-blocks

SQL Blocks
===========

To make a database query and display it's results in some form,
you use markdown extensions that I called *SQL Blocks*.

An SQL block to display query results as a table looks like this:

<div class="colored-code">
<code>
 {sqltable}
 select ... from some_table
 {sqltable}
</code>
</div>

The block tag, or keyword - in this case `{sqltable}` must start at the beginning
of a line and must not have spaces before it.

Sometimes, you need to set additional parameters for a block.

Example: get a table from `dwh` database and don't show column headers:

<div class="colored-code">
<code>
 {sqltable: db=dwh | header=no}
 select ... from some_table
 {sqltable}
</code>
</div>

Block opening tag is followed by a colon ':', then a space ' ',
then the first parameter with value, then a space, then '|', a space,
the second parameter, and so forth. Newlines, extra spaces do not matter.
Parameter values are not enclosed in quotes.

SQL Query Text
--------------

Query text is written between the opening and closing block tag.
It goes directly to the database engine, so the query must
use the database SQL dialect.

You may run a query with variables, substituded by URL parameters.
Specify them in query text as `${param-name}`.

This is covered in more depth further, in [`{sqltable}`](sqltable) section.

Currently Implemented Blocks
---------------------------

The following SQL blocks are implemented at the moment:

1. [`{sqltable}`](sqltable) - display table
2. [`{sqlinline}`](sqlinline) - inline query results
3. [`{sqllinechart}`](sqllinechart) - line chart
4. [`{sqlbarchart}`](sqlbarchart) - bar chart

SQL blocks in development:

1. Pie chart
2. Horizontal bar chart
3. Combination bar + line chart
 
Next -> [`{sqltable}`](sqltable)

----------------------------------------------------------------------

[View page source](sql-blocks.markdown)

        
        
        