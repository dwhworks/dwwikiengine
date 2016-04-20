[home](../) /
[docs](./) /
connecting-to-your-database

Connecting to your database
===========================

All database connection parameters are stored in
`settings.py` file. See comments there. Here I will try
to explain the concept.

Connectors
----------

DWWiki connects to databases via python libraries for these
databases. You may connect to as many databases as you specify
in `settings.py`. Of course, you must have your python module,
or *driver* installed on dwwiki server box.

As each database and it's driver has it's quirks, the database
connection is done using a wrapper, or *connector*.

A wrapper is a thin python module which specifies how to
properly use connection parameters from `settings.py`. For
example, a query timeout is specified differently. Text encoding
may be specified differently.

Currently implemented connectors are:

- mysqlconnector.DWMySQLConnector
- pgconnector.DWPostgreSQLConnector
- sqliteconnector.DWSQLiteConnector
- oracleconnector.DWOracleConnector - may need some adjustments

All connector modules are in `dwwiki/connectors` directory.

All connectors are loaded on server startup. 
See how it's done in `dwwikiserver.py`.

If you need to connect to MSSQL, you need to write your own
connector and load it at startup in a similar way.

It's not hard, only a couple of lines of code.

Connectors are only needed to eliminate dependencies
on actual database connection libraries and make dwwiki
run even if no database libraries are installed at all.

Connectors may offer a few extra services, for example
mapping SQL query column data types to python types.

Database Connection Parameters
-------------------------------

If your connector successfully loads at startup, it means
that database connection module is installed.
Now you must specify database connection parameters in
`settings.py`. They are explained there quite clearly.

Connection Aliases
------------------

Aliases used to abstract the real database connection from user.
User may specify database name in SQL block, and it is a reference
to an alias. Aliases are mapped to user groups and to databases.
Aliases are specified in `settings.py`. See comments there.

So for different users the same query may use a different connection.
This may be useful to restrict access to sensitive data, to load balance
user queries between servers, to make smooth transitions to a new server
and for testing purposes.

So what you need to do to connect to your database:

1. Make sure a python library is installed.
2. Make sure a connector loads or make one yourself.
3. Specify connection parameters in `DATABASE` section in `settings.py`
4. Specify connection aliases for user groups.


Next -> [File Access Security](file-access-security)

----------------------------------------------------------------------

[View page source](connecting-to-your-database.markdown)



