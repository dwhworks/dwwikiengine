#!/usr/bin/python
# -*- coding: utf-8 -*-

# Report editor template
# This file is deprecated. Now we use tamplates.
# It will be removed.

PAGE_HEADER = """<html>
    <head>
      <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
      <meta name="viewport" content="with-device-width,initial-scale=1.0,user-scalable=yes"/>
      <link rel="icon" type="image/png" href="/favicon-96x96.png">
      <link rel="stylesheet" type="text/css" href="{base}/css/styles.css"/>
      <title>dw works</title>
    </head>
    <body class="report-editor">
"""

PAGE_INFO_MSG = """<div class="notice">{message_str}</div>
"""

PAGE_BODY_START = """
<h3>Editing:</h3>
<p>File: <code style="color:red;font-weight:bold;font-size:12pt;">{file_name}</code></p>
<p>Full web path: <code style="color:red;font-size:10pt;">{full_path}</code></p>
<form method="POST">
"""

TEXT_AREA = """
<textarea tabindex="1" cols="80" rows="25" style="" name="editor">{report_text}</textarea>
"""

SAVE_BUTTONS = """<input type="submit" name="save" value="{save_str}" class="submit-button"/>
<input type="submit" name="saveandclose" value="{save_and_close_str}" class="submit-button"/>
"""

CANCEL_LINK = """<a href="{cancel_link}">{cancel_str}</a>
"""

PAGE_BODY_END = """ 
</form>
"""

PAGE_FOOTER = """
    </body>
</html>
"""
