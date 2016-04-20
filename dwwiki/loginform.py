#!/usr/bin/python
# -*- coding: utf-8 -*-

LOGIN_PAGE_HEADER = """<html>
    <head>
      <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="with-device-width,initial-scale=1.0,user-scalable=yes"/>
      <link rel="stylesheet" type="text/css" href="{base}/css/styles.css"/>
      <title>dw wiki</title>
    </head>
    <body class="login">
"""

#PAGE_LOGO = """
#        <div class="logo">ad initium
#        </div>
#"""

LOGIN_FORM_BODY = """
<form class="vertical-form" method="POST">
  <legend>{lc_login_to_dw_wiki}</legend>
  <input placeholder="{lc_user_name}" type="text" name="user" autocomplete="off"/>
  <input placeholder="{lc_password}" type="password" name="psswrd"/>
  <input placeholder="{lc_navigate_to}" type="text" name="target" value="{target_report}"/>
  <input type="submit" value="{lc_log_in}" class="submit-button"/>
</form>
"""

LOGIN_INCORRECT = """<ul class="notice errors">
<li>{invalid_username}</li>
</ul>
"""

PAGE_FOOTER = """
    </body>
</html>
"""
