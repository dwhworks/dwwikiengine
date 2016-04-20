home /


Welcome
========

dw wiki is a simple wiki-like system for
database reporting.

If you see this, it means dwwiki is up and running on your system.

Before you begin
===============

This package comes with a sample SQLite database. This database
is used in examples, you may use it, make your own reports,
add your own tables, data, whatever you like.
The database should work out of the box, because it is
installed with python by default.

You may connect to your own databases. The system can work
with any database that has python connection libraries.
These libraries you have to install on your system yourself,
they are not bundled with dwwiki engine.

Now we need to make sure everything is working properly.
Some dwwiki features depend on these python libraries:

1. [matplotlib] [1] - the most powerful library to draw charts.
2. [pdfkit] [2] - the library to render your pages as PDF.

[1]: http://matplotlib.org/
[2]: https://pypi.python.org/pypi/pdfkit

If these libraries are not installed, dwwiki will still work,
but you will not be able to see charts or download your reports
in PDF format.

Installing Matplotlib
---------------------

For instructions please visit the [official installation guide] [3].


After you have matplotlib installed, restart dwwiki server
and see if you have any warnings of missing matplotlib on startup.

Now go to [this page](chart-test) to check if you can see any charts.

[3]: http://matplotlib.org/users/installing.html

Installing pdfkit
-----------------

PDFKit is python wrapper to convert html to PDF.
For instructions, visit [pdfkit installation page] [4].

To make sure pdfkit is working, restart the server and
try to download [this page as PDF](?action=pdf).

Now the engine should be working as intended.

[4]: https://pypi.python.org/pypi/pdfkit

Other Libraries
--------------

DWWiki also depends on these libraries, but they are
included with the downloaded package. You don't have
to install them separately, but you can if you want to
try a newer version.

1. [CherryPy] [5] - A Python Web Framework dwwiki is built on.
2. [Python Markdown] [6] - A wiki markup language used in dwwiki to make reports.
3. [xlwt] [7] - A library to create XLS files from Python code.

[5]: http://www.cherrypy.org/
[6]: https://pythonhosted.org/Markdown/index.html
[7]: https://github.com/python-excel/xlwt

Now we may proceed to a [Getting started](docs/getting-started) page.

----------------------------------------------------------------------

[View page source](index.markdown)

