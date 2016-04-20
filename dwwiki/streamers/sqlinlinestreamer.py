#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import dwstreamer
import settings
from dwwiki.dwexceptions import DwException
from pyparsing import Literal, Word, Keyword, Suppress, CharsNotIn, \
        Group, delimitedList, Dict, SkipTo, Forward, alphanums, Optional
import dwwiki.connectors

class SqlInlineStreamer(dwstreamer.BaseDwStreamer):
    """Returns query results just as string separated by spaces"""
    
    ATTR_DB = 'db'

    TAGNAME = 'sqlinline'

    
    def factory(self):
        return SqlInlineStreamer()

    def get_tagname(self):
        return self.TAGNAME
    
    def get_con(self, db):
        con = dwwiki.connectors.get_connection(db)
        return con
#        # TODO work around if connection does not exist
#        #db = settings.DATABASES[dbname]
#
#        #con = MySQLdb.connect(host=db['HOST'], user=db['USER'], passwd=db['PASSWORD'], db=db['DB'],
#        #    charset='utf8',
#        #    cursorclass = MySQLdb.cursors.SSCursor)
#        con = None
#        # TODO different connectors should live in different files
#        if db['ENGINE'] == 'mysql':
#            import mysql.connector
#            timeout = db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
#            con = mysql.connector.connect(
#                user=db['USER'],
#                passwd=db['PASSWORD'],
#                host=db['HOST'],
#                database=db['DB'],
#                connection_timeout=timeout
#            )
#        elif db['ENGINE'] == 'postgresql':
#            import psycopg2
#            # set query timeout as options to psycopg
#            timeout = db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
#            con = psycopg2.connect(
#                user=db['USER'],
#                password=db['PASSWORD'],
#                host=db['HOST'],
#                database=db['DB'],
#                port=db['PORT'],
#                options="-c statement_timeout=%d" % timeout
#            )
#            con.set_client_encoding('utf-8')
#        elif db['ENGINE'] == 'sqlite':
#            import sqlite3
#            timeout = db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
#            con = sqlite3.connect(
#                database=db['DB'],
#                timeout=timeout
#            )
#                
#
#            #con.set_client_encoding('unicode')
#
#        return con

    # returns sql block parsed into tokens
    def parse_block(self, block_text):
        # make a grammar
        block_start = Literal("{")
        sql_start = Keyword("sqlinline", caseless=True)
        colon = Literal(":")
        sql_end = Literal("}")
        separator = Literal("|")
        block_end = Keyword("{sqlinline}", caseless=True)

        # params
        field_name = Word(alphanums)
        equal_sign = Suppress(Literal("="))

        # whatever value
        field_value = (CharsNotIn("|}"))

        # param name and value
        param_group = Group(field_name + equal_sign + field_value)

        # list of all params
        param_list = delimitedList(param_group, '|')

        # helper
        param_dict = Dict(param_list)

        # sql text
        sql_text = SkipTo(block_end)

        sqldecl = Forward()

        sqldecl << (block_start +
                    sql_start + 
                    Optional(colon) +
                    Optional(param_dict) +
                    sql_end +
                    sql_text.setResultsName('sqltext') +
                    block_end)

        block_str = "".join(block_text) 
        tokens = sqldecl.parseString( block_str )
        return tokens

    def format_value(self, val):
        tp = type(val).__name__

        if tp == 'str':
            res = val.decode('utf-8')
        elif tp == 'unicode':
            res = unicode(val)
        elif tp in ['Decimal', 'float']:
            res = "{0:0.2f}".format(val)
        elif tp == 'date':
            res = val.strftime("%d.%m.%Y")
        elif tp in ['int', 'long']:
            res = "{0}".format(val)
        else:
            # unknown datatype
            res = unicode(val)

        return res
    
    def process_block(self, block_text, user, **params):
        """ Yields all query results at once. Only once.
        May return an exception.
        """
        try:
            tokens = self.parse_block(block_text)
            db_name = tokens.get(self.ATTR_DB, settings.DATABASE_DEFAULT_ALIAS).strip()
            con = None

            db = settings.DATABASES.get(db_name, None)
            if db == None:
                raise DwException(db_name, "Unknown database %s." % db_name)
            true_sql = tokens.sqltext
            p = re.compile(u'\$\{[a-z]+[0-9]*\}')
            lst = p.findall(true_sql)

            for item in lst:
                stripped_item = item[2:-1]
                # TODO check for default value here
                value = 'None'
                if stripped_item in params:                
                    value = params[stripped_item]
                    value = urllib.unquote(value)
                # replace it
                true_sql = true_sql.replace(item, value)
            
            # get a connection from somewhere
            con = self.get_con(db)
            cur = con.cursor()
            cur.execute(true_sql)
            
            row = cur.fetchone()
            num_rows = 0
            while row is not None:
                if num_rows == db.get('LIMIT_ROWS', 1000):
                    # we are 1 row over limit
                    add_line = htmlconstants.SQL_OVER_LIMIT.format(num_rows)
                    row = None
                    break
                else:
                    retstr = u''
                    for val in row:
                        retstr = retstr + ' ' + self.format_value(val)
                    retstr += "\n"
                    yield retstr
                    num_rows += 1
                    row = cur.fetchone()
            con.close()
            con = None


        except DwException, e:
            if con is not None:
                con.close()
            raise e
            
        except Exception, e:
            if con is not None:
                con.close()
            
            # reraise it wrapped in our class
            raise DwException(db_name, "Some source exception", e)
