#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

# a) Configuration of Python's code search path
#    If you already have set up the PYTHONPATH environment variable for the
#    stuff you see below, you don't need to do a1) and a2).

# a1) Path of the directory where the dwwiki code package is located.
#     Needed if you installed with --prefix=PREFIX or you didn't use setup.py.
#sys.path.insert(0, 'PREFIX/lib/python2.4/site-packages')

# a2) Path of the directory where settings.py is located.
serverpath = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))
sys.path.insert(0, serverpath)
os.chdir(serverpath)

# This is needed to properly import cherrypy and other dependencies
# that are stored in support subdir
from dwwiki import web


if __name__ == '__main__':
    import dwwiki.engine
    import cherrypy

    # make up absolute path to required directories

    # where all the pages are stored
    wiki_path = os.path.join(serverpath, 'www', 'wiki')

    # path for temporary files
    temp_path = os.path.join(serverpath, 'tempfiles')

    # path for session files
    session_path = os.path.join(serverpath, 'sessions')

    # path for page templates
    templates_path = os.path.join(serverpath, 'www', 'templates')

    # static files path
    static_path = os.path.join(serverpath,'www', 'static')

    # css path
    css_path = os.path.join(serverpath,'www', 'static', 'css')
    
    # img path
    img_path = os.path.join(serverpath,'www', 'static', 'img')
    
    # favicon
    favicon_path = os.path.join(serverpath,'www', 'static', 'img', 'favicon-32x32.png')

    # This is global config for cherrypy server
    global_config = {
            'server.socket_host': "0.0.0.0",
            # we are not using proxy here actually. The following param
            # is used to generate full urls
            'tools.proxy.base': "http://localhost:8087",
            'tools.proxy.on' : False,
            'server.socket_port': 8087,
            'tools.gzip.on': False,
            'log.screen': True,
            'request.show_tracebacks' : False,
            'tools.secureheaders.on' : True,
            # dwwiki specific settings
            'dwwiki.wikidir' : wiki_path,
            'dwwiki.htmltemplatesdir' : templates_path,
            'dwwiki.tempfiledir' : temp_path
            # when True means redirect to language path like /en/ or /ru/
            # otherwise it is not done. maybe apache does it
            #'dwwiki.langredirect' : True
    }

    # This is config for dwwiki engine
    dwwiki_config = { '/':
        {
            'tools.staticdir.root' : static_path,
            'tools.trailing_slash.on': False,
            'tools.sessions.on' : True,
            'tools.sessions.storage_type' : 'file',
            'tools.sessions.storage_path' : session_path,
            'tools.sessions.timeout' : 43200
        },
        '/css': {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : "css"
        },
        '/img': {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : "img"
        },
        '/favicon.ico' : {
            'tools.staticfile.on' : True,
            'tools.staticfile.filename' : favicon_path
        }
    }


    cherrypy.config.update(global_config)

    # Now register all the streamers we know of.
    dwengine = dwwiki.engine.DWWikiEngine()
    
    # Try to load all our streamers, i.e. components for rendering
    # sql or whatever else
    try:
        # table streamer
        from dwwiki.streamers.sqltablestreamer import SqlTableStreamer
        ts = SqlTableStreamer()
        dwengine.register_block_streamer(ts)
    except Exception, e:
        msg = "WARNING: SqlTableStreamer is not loaded. Error:"
        print msg
        print e

    try:
        # inline streamer
        from dwwiki.streamers.sqlinlinestreamer import SqlInlineStreamer
        ts = SqlInlineStreamer()
        dwengine.register_inline_streamer(ts)
    except Exception, e:
        msg = "WARNING: SqlInlineStreamer is not loaded. Error:"
        print msg
        print e

    try:
        # sql line chart streamer
        from dwwiki.streamers.sqllinechartstreamer import SqlLineChartStreamer
        ts = SqlLineChartStreamer()
        dwengine.register_block_streamer(ts)
    except Exception, e:
        msg = "WARNING: SqlLineChartStreamer is not loaded. Check if matplotlib module is installed. Error:"
        print msg
        print e

    try:
        # sql bar chart streamer
        from dwwiki.streamers.sqlbarchartstreamer import SqlBarChartStreamer
        ts = SqlBarChartStreamer()
        dwengine.register_block_streamer(ts)
    except Exception, e:
        msg = "WARNING: SqlBarChartStreamer is not loaded. Check if matplotlib module is installed. Error:"
        print msg
        print e

    # Now register all our sql connectors

    # Not all libraries may be installed. So we will inform the user instead of
    # just throwing about exceptions

    # Postgres
    try:
        import dwwiki.connectors.pgconnector
        postgres_connector = dwwiki.connectors.pgconnector.DWPostgreSQLConnector()
        dwwiki.connectors.add_engine('postgresql', postgres_connector)

    except Exception, e:
        msg = "WARNING: Postgre SQL connector is not loaded. Check if psycopg2 module is installed."
        print msg
        print e

    # MySQL
    try:
        import dwwiki.connectors.mysqlconnector
        mysql_connector = dwwiki.connectors.mysqlconnector.DWMySqlConnector()
        dwwiki.connectors.add_engine('mysql', mysql_connector)
    except Exception, e:
        msg = "WARNING: MySql connector is not loaded. Check if mysql.connector module is installed."
        print msg
        print e

    # SQLite
    try:
        import dwwiki.connectors.sqliteconnector
        sqlite_connector = dwwiki.connectors.sqliteconnector.DWSQLiteConnector()
        dwwiki.connectors.add_engine('sqlite', sqlite_connector)
    except Exception, e:
        msg = "WARNING: SQLite connector is not loaded. Check if sqlite module is installed."
        print msg
        print e

    # Oracle
    try:
        import dwwiki.connectors.oracleconnector
        oracle_connector = dwwiki.connectors.sqliteconnector.DWOracleConnector()
        dwwiki.connectors.add_engine('oracle', oracle_connector)
    except Exception, e:
        msg = "WARNING: Oracle connector is not loaded. Check if cx_Oracle module is installed."
        print msg
        print e

    print "Database connectors installed:"
    print dwwiki.connectors._connectors.keys()


    # call cherrypy to run and mount our application object
    cherrypy.quickstart(dwengine, '/', dwwiki_config)

