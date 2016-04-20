DWWiki
=======

DWWiki is a simple wiki-like system for database reporting.

It started as a set of utilities for embedding SQL queries
into markdown-formatted documents for creating documentation
and reports for my Data Warehousing projects.

It has grown into a SQL-reporting server that is simple,
extendable and easy to use for end users of Data Warehouses.

Most of desired features that were (are) lacking
in commercial BI and reporting solutions were included
in dwwiki. I designed it for myself, my colleagues, and
my poor users, who were mostly tied to visual drag-and-drop
bloated BI engines.

Design Concept
==============

1. Write a wiki-page in markdown, include sql queries into the text.

2. Display results of a query as table, graph, chart, map... etc.

3. Link query results together to drill down or drill across.

4. Download query results as csv or xls.

5. Download reports as printable html or as PDF.

6. Connect to several databases.

7. Fine-grained control of user access to database tables and reports.

8. Edit reports in your favourite text editor or through simple web text editor.

9. Track report versions with commonly used tools - git, svn, whatever you like.

10. Avoid abstraction layers between the user and the database engine.

11. Friendly to non-programmers, yet open for advanced users.

11. Keep away from hyper-interactive interface. Keep it simple.

Architecture & Dependencies
============================

Written in python.  
DWWiki engine is built on top of [CherryPy](http://www.cherrypy.org/).  
Charts are rendered using [Matplotlib](http://matplotlib.org/)  
PDF rendering is done with [PDFKit](https://pypi.python.org/pypi/pdfkit)  

Installation
============

1. Install Python 2.6..2.7.

2. Download dwwiki.

4. Run `python dwwikiserver.py` from installation directory.
   Check stdout if there are any errors or warnings. Ignore
   warnings.

5. Open `http://localhost:8087` in a browser.

References
==========

See http://dwworks.ru/ru/dwwiki

It's only in Russian at the moment, but not for long. 

