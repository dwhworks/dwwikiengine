# -*- coding: utf-8 -*-

""" HTML constants used (hardcoded) in dwwiki engine.
The content of this file is a bit out of date, most of
the constants are not used anymore. Only error messages
and warnings are actually used, and this not for long.
See www/templates directory for actual templates used.
"""

PAGE_HEADER = """<html>
    <head>
      <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
      <!-- meta name="viewport" content="with-device-width,initial-scale=1.0,user-scalable=yes"/-->
      <meta name="viewport" content="with-device-width"/>
      <link rel="icon" type="image/png" href="/favicon-96x96.png">
      <link rel="stylesheet" type="text/css" href="{base}/css/styles-khaki.css"/>
      <title>{title}</title>
    </head>
    <body>
"""


PAGE_LOGO = """
        <div class="logo">
            <div style="float:left;">
                <a href="{base}"><img src="{base}/img/dwworks-logo-bw-98x24.png" alt="dwworks.ru"/></a>
            </div>
            <div style="float:left;padding-left:6px;">
                <a href="{base}/dwwiki/">dwwiki</a> | 
                <a href="etl/">etl</a> | 
                <a href="contacts/">контакты</a>
            </div>
        </div>
        <div style="clear:both"/>
"""

#PAGE_SUB_HEADER_OLD = """
#        <div class="menu">
#            <!-- a href="{edit_url}">edit</a>&nbsp;|
#             a href="{source_url}" target="_blank">source |
#            &nbsp;&nbsp;&nbsp;&nbsp; -->
#            User:&nbsp;{user}&nbsp;&nbsp;<a href="{logout_url}">Log&nbsp;out</a> 
#        </div>
#        <hr/>
#"""

# this with edit url
PAGE_SUB_HEADER = """
        <div class="menu">
            <div style="float:left;">
                <a href="{edit_url}">{edit_str}</a>&nbsp;
            </div>
            <div style="float:right">
                {user}&nbsp;&nbsp;<a href="{logout_url}">{login_logout}</a>&nbsp;&nbsp;{en_ru_link}
            </div>
            <div style="clear:both;">
            </div>
        </div>
"""

# no edit link
PAGE_SUB_HEADER_EDITOR = """<div class="menu">
            <div style="float:right">
                {user}&nbsp;&nbsp;<a href="{logout_url}">{login_logout}</a>&nbsp;&nbsp;{en_ru_link}
            </div>
            <div style="clear:both;">
            </div>
        </div>
"""

PAGE_INFO_MSG = """<div class="notice">{message_str}</div>
"""

PAGE_SUB_FOOTER = """
        <br/>
        <div class="bottom-menu">
            <a href="{edit_url}">{edit_str}</a>&nbsp;|
            <!-- a href="{source_url}" target="_blank">source</a -->
        </div>
        <div class="bottom">&copy; 2014-2016 DW Works LLC</div>
"""

PAGE_FOOTER = """
    </body>
</html>
"""

SQL_ERROR_MSG = """
<div class="errorblock">
    <h3>Database error</h3>
    <p class="sqlerrormessage">
        An error occured during database query. Please contact
        administrator. Error details:
    </p>
    <p class="sqlerrorcode">
        URL: {error_path}<br/>
        Error type: {error_type}<br/>
        Error message: {error_msg}<br/>
        Database: {error_db}<br/>
        User: {error_user}<br/>
    </p>
</div>
"""

# sql table constants

SQL_TABLE_TABLE = """
    
"""

SQL_OVER_LIMIT = """
<br/>
<div class="warningblock">
    <h3>Too many results</h3>
    <p class="sqlerrormessage">
        The above query returned more rows than the set limit - {0} rows.
        Only this number is displayed.<br/>
        If you really need all rows, you may try to download
        query results as csv.<br/>
        But even in this case the number
        of rows is limited to 65000.
    </p>
</div>
<br/>
"""
