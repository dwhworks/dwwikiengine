#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings
import htmlconstants
import time
import re
import cherrypy
import markdown
import markdown.extensions
import urllib
import dwstreamer
from dwwiki.dwexceptions import DwException
from pyparsing import Word, Literal, Keyword, alphas, alphanums, delimitedList, oneOf, \
    Optional, Forward, ZeroOrMore, Empty, SkipTo, Group, Suppress, Dict, CharsNotIn
import traceback
# excel
import xlwt
#import dwwiki.connectors.pgconnector as pg
import dwwiki.utils as utils
import dwwiki.connectors


class SqlTableStreamer(dwstreamer.BaseDwStreamer):
    """Block streamer that creates a table out of sql query"""
    
    TAGNAME = 'sqltable'

    # re to find attributes for table cells
    ATTR_RE = re.compile('\{: *([ [a-z]+=\".+\" *]*)\}')

    # Attributes of {sqltable} tag
    ATTR_DB = u'db'
    ATTR_TOTALS = u'totals'
    ATTR_ORIENTATION = u'orientation'
    # available orientations
    ATTR_VAL_ORIENTATION_VERTICAL = u'vertical'
    ATTR_VAL_ORIENTATION_HORIZONTAL = u'horizontal'

    ATTR_DEFAULT_VAL_ORIENTATION = ATTR_VAL_ORIENTATION_VERTICAL

    # table style
    ATTR_STYLE = u'style'
    # available styles are there in css file
    ATTR_DEFAULT_VAL_STYLE = u'standard-report'

    # header or no header. Can be 'yes' or 'no'. Default - 'yes'
    ATTR_HEADER = u'header'
    ATTR_DEFAULT_VAL_HEADER = u'yes'
    ATTR_HEADER_VAL_YES = u'yes'
    ATTR_HEADER_VAL_NO = u'no'

    # debugging attribute for delaying rows output
    ATTR_DELAY = u'delay'
    ATTR_DELAY_DEFAULT_VAL = u'0'

    # value types that can be aggregated
    FIELD_TYPES_AGGREGATION = ['Decimal', 'int', 'long', 'float']

    def __init__(self):
        self.con = None
        self.sett = settings.CSV_DOWNLOAD_FORMAT['en']
        # separator for csv
        self.sep = unicode(self.sett.get('FIELD_SEPARATOR', ','))

    
    def factory(self):
        return SqlTableStreamer()


    def get_tagname(self):
        return self.TAGNAME

    def format_value(self, val, html=True):
        """default formatting of database values.
        returns <td>value</td> if html=True. Else returns just value"""

        #td_start = u'<td class='
        cell_style = self.table_css_class + '-cell'
        td_start = u'<td class="' + cell_style + u'"'
        td_align_left = ' '
        td_align_right = ' align="right" '
        align = td_align_left
        #res = td + unicode(val) + '</td>'
        tp = type(val).__name__

        #md = markdown.Markdown(extensions=['markdown.extensions.attr_list'])
        md = markdown.Markdown()
        #attr = markdown.extensions.attr_list
        #attr.extend(md, [])
        
        #md = markdown.Markdown(safe_mode='escape')
        attrs = ''
        if tp == 'str':
            res = val.decode('utf-8')
            match = self.ATTR_RE.search(res)
            if match != None:
                attrs = ' ' + match.group(1) + ' '
                res = re.sub(self.ATTR_RE, '', res)
            # markdown it
            res = md.convert(res)
            # remove <p></p>
            if res[:3] == '<p>':
                res = res[3:-4]
        elif tp == 'unicode':
            res = unicode(val)
            match = self.ATTR_RE.search(res)
            if match != None:
                attrs = ' ' + match.group(1) + ' '
                res = re.sub(self.ATTR_RE, '', res)
            # markdown it
            res = md.convert(res)
            # remove <p></p>
            if res[:3] == '<p>':
                res = res[3:-4]
        elif tp in ['Decimal', 'float']:
            res = "{0:0.2f}".format(val)
            align = td_align_right
        elif tp == 'date':
            res = val.strftime("%d.%m.%Y")
        elif tp in ['int', 'long']:
            res = "{0}".format(val)
            align = td_align_right
        elif tp in ['NoneType']:
            res = '&nbsp;'
        else:
            # unknown datatype
            res = unicode(val)
            match = self.ATTR_RE.search(res)
            if match != None:
                attrs = ' ' + match.group(1) + ' '
                res = re.sub(self.ATTR_RE, '', res)
            # markdown it
            res = md.convert(res)
            # remove <p></p>
            if res[:3] == '<p>':
                res = res[3:-4]

        if html:
            res = td_start + align + attrs + '>' + res + '</td>'
            

        # now we can possibly have a link in a column.
        # It may contain URL parameters with special characters.
        # Something like /myreport?name="Some long name in God knows what Language"
        # We should quote it
        return res

    def format_csv_value(self, val):
        """Format a value for csv output, according to standard csv rules
        (https://en.wikipedia.org/wiki/Comma-separated_values).
        Also settings are used. The value is returned as unicode.
        All html, attributes and markdown links are replaced by plain text"""

        def deal_with_str(strval):
            """Formats string as unicode with optional double quotes according
            to standard"""
            need_quotes = False
            result = strval
            # first commas or semicolons
            ind = result.find(self.sep)
            if ind >= 0:
                need_quotes = True
            # now double quotes
            # we need to add one to each occurence
            ind = result.find('"')
            if ind >= 0:
                need_quotes = True
                result = result.replace('"', '""')
            # newline characters.
            newline_repl = self.sett.get('NEWLINE_REPLACEMENT', None)
            if newline_repl is None:
                need_quotes = True
            else:
                # replace them
                result = result.replace("\r\n", newline_repl)
                result = result.replace("\n", newline_repl)
                result = result.replace("\r", newline_repl)
            # leading or trailing spaces require double quotes too
            if (result[0] == ' ') or (result[-1] == ' '):
                need_quotes = True
            # tabs require quotes or replacement
            ind = result.find("\t")
            if ind >= 0:
                tab_repl = self.sett.get('TAB_REPLACEMENT', None)
                if tab_repl is None:
                    need_quotes = True
                else:   
                    result = result.replace("\t", tab_repl)
            # finally
            if need_quotes:
                result = u'"' + result + u'"'
            return result


        sett = settings.CSV_DOWNLOAD_FORMAT['en']
        tp = type(val).__name__
        res = ''
        if tp == 'str':
            res = deal_with_str(val.decode('utf-8'))
        elif tp == 'unicode':
            res = deal_with_str(unicode(val))
        elif tp in ['Decimal', 'float', 'int', 'long']:
            # plain
            res = str(val)
        elif tp == 'date':
            res = val.strftime(sett['DATE_FORMAT'])
        elif tp in ['NoneType']:
            res = ''

        # attributes
        match = self.ATTR_RE.search(res)
        if match != None:
            attrs = ' ' + match.group(1) + ' '
            res = re.sub(self.ATTR_RE, '', res)

        return res
        

    # gets a database connection
    # it should work with several connections
    # throws a DWDatabaseError 
    def get_con(self):
        # TODO work around assigning a connection to a member var.
        # We really want to have a stateless object here
        self.con = dwwiki.connectors.get_connection(self.db)
#        #return con
#
#        #con = MySQLdb.connect(host=db['HOST'], user=db['USER'], passwd=db['PASSWORD'], db=db['DB'],
#        #    charset='utf8',
#        #    cursorclass = MySQLdb.cursors.SSCursor)
#        self.con = None
#        db = self.db
#        # TODO different connectors should live in different files
#        if db['ENGINE'] == 'mysql':
#            import mysql.connector
#            timeout = db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
#            self.con = mysql.connector.connect(
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
#            self.con = psycopg2.connect(
#                user=db['USER'],
#                password=db['PASSWORD'],
#                host=db['HOST'],
#                database=db['DB'],
#                port=db['PORT'],
#                options="-c statement_timeout=%d" % timeout
#            )
#            self.con.set_client_encoding('utf-8')
#        elif db['ENGINE'] == 'sqlite':
#            import sqlite3
#            timeout = db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
#            self.con = sqlite3.connect(
#                database=db['DB'],
#                timeout=timeout
#            )


    # returns sql block parsed into tokens
    def parse_block(self, block_text):
        # make a grammar
        block_start = Literal("{")
        sql_start = Keyword("sqltable", caseless=True)
        colon = Literal(":")
        sql_end = Literal("}")
        separator = Literal("|")
        block_end = Keyword("{sqltable}", caseless=True)

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


    def prepare_for_query(self, block_text, user, **params):
        self.tokens = self.parse_block(block_text)
        # set all required parameters
        self.db_name = self.tokens.get(self.ATTR_DB, settings.DATABASE_DEFAULT_ALIAS).strip()
        # check orientation
        self.orientation = self.tokens.get(self.ATTR_ORIENTATION, self.ATTR_DEFAULT_VAL_ORIENTATION).strip()
        # string for totals
        self.totals_str = self.tokens.get(self.ATTR_TOTALS, '')
        # array of required totals like ,,sum,crap,avg
        self.totals_array = []
        # array to calculate real totals if possible
        self.totals_values = []
        if self.totals_str <> '':
            # user requires totals
            self.totals_array = self.totals_str.split(',')

        # table, row, footer and cell styles
        self.table_css_class = self.tokens.get(self.ATTR_STYLE, self.ATTR_DEFAULT_VAL_STYLE).lower().strip()

        # header
        self.header = self.tokens.get(self.ATTR_HEADER, self.ATTR_DEFAULT_VAL_HEADER).lower().strip()
        # avoid gibberish
        if not self.header in [self.ATTR_HEADER_VAL_YES, self.ATTR_HEADER_VAL_NO]:
            self.header = self.ATTR_HEADER_VAL_YES

        # delay for rows. in milliseconds. for debugging
        self.delay = 0
        s = self.tokens.get(self.ATTR_DELAY, self.ATTR_DELAY_DEFAULT_VAL)
        try:
            self.delay = int(s)
        except ValueError, e:
            self.delay = 0
        # beware for max and min: 0 to 10,000 = 10 seconds
        if (self.delay < 0):
            self.delay = 0
        elif self.delay > 10000:
            self.delay = 10000
            
        
        # database. real one
        self.db = settings.DATABASES.get(self.db_name, None)
        if self.db == None:
            raise DwException(self.db_name, "Unknown database %s." % self.db_name)
        
        self.true_sql = self.tokens.sqltext
        # now that we have a sql, try to replace parameters in it.
        # Parameter looks like ${param_name}         
        p = re.compile(u'\$\{[a-z]+[0-9]*\}')
        # get the list of all mentioned params
        lst = p.findall(self.true_sql)
        # loop through all these variables and try to replace
        # them with params passed to us
        # test with sql with parameters

        for item in lst:
            stripped_item = item[2:-1]
            # TODO check for default value here
            value = 'None'
            if stripped_item in params:                
                value = params[stripped_item]
                value = urllib.unquote(value)
            # replace it
            self.true_sql = self.true_sql.replace(item, value)
        
        # get a connection from somewhere
        self.get_con()
        self.cur = self.con.cursor()
        self.cur.execute(self.true_sql)
        # okay. return now
        
    def make_horizontal_table(self):
        """ Makes horizontal table and yields it
        """
        # two lists. first - columns of query
        # each column contains a list of column values
        
        all_rows = self.cur.fetchall()
        # now make up columns
        columns = self.cur.description

        table_str = u"<table class=\"" + self.table_css_class + "-table\">" 
        # traverse all values
        row_count = len(columns)
        col_count = len(all_rows)+1
        for row_num in range(row_count):
            table_str += u'<tr>'
            for col_num in range(col_count):
                if col_num == 0:
                    if self.header == self.ATTR_HEADER_VAL_YES:
                        # headers
                        col = columns[row_num]
                        s = col[0]
                        if type(col[0]) is str:
                            s = col[0].decode('utf-8')
                        elif type(col[0]) is unicode:
                            s = col[0]
                        else:
                            print str(type(col[0]))
                        # use it with header class
                        td_start = u'<td class="' + self.table_css_class + u'-header">'
                        table_str += td_start + s + u'</td>'
                else:
                    val = all_rows[col_num-1][row_num]
                    table_str += self.format_value(val, html=True)
            table_str += u"</tr>\n"
        table_str += u"</table>\n"
        return table_str

    # tries to execute query and yields it's results
    # should be used as a generator
    # sql_block is an array of strings like
    # {sql:db=dwh | someparam='tratata'}
    def process_block(self, block_text, user, block_id, **params):
        try:
            self.prepare_for_query(block_text, user, **params)

            if (self.orientation == self.ATTR_VAL_ORIENTATION_HORIZONTAL):
                yield self.make_horizontal_table()
                return


            # fetch at least one row to check for datatypes
            row = self.cur.fetchone()
            # now make up columns
            columns = self.cur.description

            # make an array for columns if we have totals
            # at first it is filled with None's
            need_totals = False
            if len(self.totals_array) > 0:
                self.totals_values = [None] * len(self.totals_array)
                need_totals = True


            # TODO call for horizontal table here
            # now start to make table even if it doesn't have any data
            out_str = u"<table class=\"" + self.table_css_class + "-table\">\n" 
            if self.header == self.ATTR_HEADER_VAL_YES:
                header_line = u"<tr>\n"
                col_count = len(columns)
                for col in columns:
                    # we've sent the query in unicode, and yet, all our column
                    # names are returned as utf-8. this is with mysqldb
                    s = col[0]
                    if type(col[0]) is str:
                        s = col[0].decode('utf-8')
                    elif type(col[0]) is unicode:
                        s = col[0]
                    else:
                        print str(type(col[0]))
                    header_line += u'<td class="' + self.table_css_class + u'-header">{}</td>'.format(s)
                    # the query text was in utf8. Therefore the header is in utf8 too
                    # table_header += u'<td class="table-header">' + col[0].decode('utf-8') + '</td>'
                header_line += "</tr>\n"
                out_str += header_line
                
            # return header
            yield out_str


            if row is None:
                out_str = "<tr><td class=\"" + self.table_css_class + "-cell\" colspan=\"{}\">No data&nbsp;</td></tr>\n"
                yield out_str.format(len(columns))

            num_rows = 0
            # now data itself
            add_line = ''
            while row is not None:
                if num_rows == self.db.get('LIMIT_ROWS', 1000):
                    row_line = u'<tr>'
                    for val in row:
                        row_line += self.format_value('...')
                    row_line += u"</tr>\n"
                    yield row_line
                    # we are 1 row over limit
                    add_line = htmlconstants.SQL_OVER_LIMIT.format(num_rows)
                    row = None
                    need_totals = False
                    break
                else:
                    # ordinary lines
                    row_line = u'<tr>'
                    cnt = 0
                    for val in row:
                        row_line += self.format_value(val)
                        # try to calculate totals. if value is of
                        # numeric type, add it in case of sum
                        if len(self.totals_array) > (cnt):
                            agg_keyword = self.totals_array[cnt].strip().lower()
                            cur_val = None
                            # it may be one of: sum, avg, min, max, count
                            if agg_keyword in ['sum', 'avg']:
                                num_val = utils.try_to_make_number(val, 0)
                                # add up
                                cur_val = self.totals_values[cnt]
                                if (cur_val == None):
                                    # store the first value
                                    cur_val = num_val
                                else:
                                    cur_val += num_val

                            elif agg_keyword in ['min', 'max']:
                                if type(val).__name__ in self.FIELD_TYPES_AGGREGATION:
                                    cur_val = self.totals_values[cnt]
                                    if (cur_val == None):
                                        # store the first value
                                        cur_val = val
                                    else:
                                        if agg_keyword == 'max':
                                            if cur_val < val:
                                                cur_val = val
                                        elif agg_keyword == 'min':
                                            if cur_val > val:
                                                cur_val = val
                            elif agg_keyword == 'count':
                                # here we are only interested in non-null values
                                # data type does not matter
                                cur_val = self.totals_values[cnt]
                                if (cur_val is None) and (val is not None):
                                    cur_val = int(1)
                                elif (val is not None): 
                                    cur_val += 1
                            
                            self.totals_values[cnt] = cur_val
                        cnt += 1
                    row_line += "</tr>"
                    num_rows += 1
            
                    # debug
                    if self.delay > 0:
                        time.sleep(self.delay / 1000.00)

                    yield row_line
                    #time.sleep(1.0/6) 
                    row = self.cur.fetchone()
            
            # Now we have looped through all the rows.
            # We may output totals if needed
            if need_totals and (num_rows > 0):
                row_line = '<tr>'
                cell_class = self.table_css_class + "-footer"
                #print self.totals_values
                for i in range(len(columns)):
                    if i < len(self.totals_values):
                        val = self.totals_values[i]
                        if val == None:
                            # it can be that user showed not sum or avg,
                            # but some arbitary string in totals.
                            # in that case val will be None at this point
                            # but we copy it's heading
                            total_heading = self.totals_array[i].strip()
                            if total_heading.lower() not in ['sum', 'avg', 'count', 'min', 'max']:
                                val = total_heading
                        else:
                            cell_class = self.table_css_class + "-footer-numbers"
                            agg_keyword = self.totals_array[i].strip().lower()
                            if agg_keyword == 'avg':
                                val = val / num_rows
                            
                            tp = type(val).__name__
                            if tp == 'Decimal':
                                # check for scale
                                col = columns[i]
                                # scale
                                scale = col[5]
                                if scale is None:
                                    scale = 0
                                # when sums and averages are used in sql,
                                # it may return unpredictable value
                                # so we take a reasonable scale of up to ten
                                if scale > 10:
                                    scale = 2
                                if scale > 0:
                                    fmt_str = "{0:0." +  str(scale) + "f}"
                                else:
                                    fmt_str = "{0:0}"
                                val = fmt_str.format(val)
                            elif tp == 'float':
                                val = "{0:0.2f}".format(val)
                            elif tp in ['int', 'long']:
                                val = str(val)
                        if val == None:
                            val = '&nbsp;'
                        row_line += u"<td class=\"" + cell_class + "\">" + val + '</td>'
                    else:
                        row_line += u"<td class=\"" + cell_class + "\">&nbsp;</td>"
                row_line += '</tr>' + "\n"
                yield row_line
                    
            # with mysql at least, if we close cursor but at the moment
            # haven't read all it's rows, we get an error.
            #cur.close()
            # don't forget to close connection
            self.con.close()
            self.con = None
                
            closing_line = ''
            #closing_line = (u'<tr><td class="standard-report-download-links" colspan="{0}">download:<a href="' + \
            #        download_link + '">csv</a></td></tr>' + "\n").format(col_count)
            # close table tag
            closing_line += u"</table>\n" + add_line

            yield closing_line
        except DwException, e:
            if self.con is not None:
                self.con.close()
            raise e
            
        except Exception, e:
            if self.con is not None:
                self.con.close()
            traceback.print_exc()
            # reraise it wrapped in our class
            raise DwException(self.db_name, "Some source exception", e)
            

    def process_block_as_csv(self, tempfile, block_text, user, **params):

        #tokens = self.parse_block(block_text)
        #db_name = tokens.get(self.ATTR_DB, settings.DATABASE_DEFAULT_ALIAS).strip()
        #con = None
        sett = settings.CSV_DOWNLOAD_FORMAT['en']
        sep = unicode(sett.get('FIELD_SEPARATOR', ','))
        enc = unicode(sett.get('ENCODING', 'utf8'))
        nl = sett.get('NEWLINE', "\n")
        try:
            self.prepare_for_query(block_text, user, **params)
            
            # process columns first
            # fetch at least one row to check for datatypes
            row = self.cur.fetchone()
            # now make up columns
            columns = self.cur.description
            header_list = list()
            for col in columns:
                s = col[0]
                if type(col[0]) is str:
                    s = col[0].decode('utf-8')
                elif type(col[0]) is unicode:
                    s = col[0]
                else:
                    print str(type(col[0]))
                header_list.append(s)   
            tempfile.write((sep.join(header_list) + nl).encode(enc))
            #print sep.join(header_list) + "\n"

            while row is not None:
                rowstr = ''
                # Old trick for joining strings with comma or whatever.
                # instead of using arrays
                temp_sep = ''
                for val in row:
                    tempfile.write(temp_sep)
                    tempfile.write(self.format_csv_value(val).encode(enc))
                    temp_sep = sep
                tempfile.write(nl)
                row = self.cur.fetchone()
                    
            self.con.close()
            self.con = None
        except DwException, e:
            print e
            if self.con is not None:
                self.con.close()
            raise e
            
        except Exception, e:
            print e
            if self.con is not None:
                self.con.close()
            
            # reraise it wrapped in our class
            raise DwException(db_name, "Some source exception", e)
            

    def update_totals(self,row):
        #this stores all the totals in total_values
        #self.totals_values = list()
        print "totals_array+len=%d" %  len(self.totals_array)
        cnt = 0
        for val in row:
            if len(self.totals_array) > cnt:
                agg_keyword = self.totals_array[cnt].strip().lower()
                cur_val = None
                # it may be one of: sum, avg, min, max, count
                if agg_keyword in ['sum', 'avg']:
                    if type(val).__name__ in self.FIELD_TYPES_AGGREGATION:
                        # add up
                        cur_val = self.totals_values[cnt]
                        if (cur_val == None):
                            # store the first value
                            cur_val = val
                        else:
                            cur_val += val
                elif agg_keyword in ['min', 'max']:
                    if type(val).__name__ in self.FIELD_TYPES_AGGREGATION:
                        cur_val = self.totals_values[cnt]
                        if (cur_val == None):
                            # store the first value
                            cur_val = val
                        else:
                            if agg_keyword == 'max':
                                if cur_val < val:
                                    cur_val = val
                            elif agg_keyword == 'min':
                                if cur_val > val:
                                    cur_val = val
                elif agg_keyword == 'count':
                    # here we are only interested in non-null values
                    # data type does not matter
                    cur_val = self.totals_values[cnt]
                    if (cur_val is None) and (val is not None):
                        cur_val = int(1)
                    elif (val is not None): 
                        cur_val += 1
                            
                self.totals_values[cnt] = cur_val
            cnt += 1
                

    XLS_COL_NAMES = ['A','B','C','D','E','F','G','H','I','J','K','L','M', \
                 'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    def make_cell_address(self,row_num, col_num):
        group = col_num / 26
        rem = col_num % 26

        # allowed groups 0 to 8
        # in group 8 rem = 21 is max 256 cols A to IV
        if group == 0:
            ret_col = self.XLS_COL_NAMES[rem]
        else:
            ret_col = self.XLS_COL_NAMES[group-1] + self.XLS_COL_NAMES[rem]

        ret_row = str(row_num + 1)

        ret_val = ret_col + ret_row

        return ret_val

        
    def process_block_as_xls(self, tempfile, block_text, user, **params):
            
        try:
            # get a connector to deal with column types
            self.prepare_for_query(block_text, user, **params)
            connector = dwwiki.connectors.get_connector(self.db)
            # make an array for columns if we have totals
            # at first it is filled with None's
            need_totals = False
            if len(self.totals_array) > 0:
                self.totals_values = [None] * len(self.totals_array)
                need_totals = True
            # fetch at least one row to check for datatypes
            row = self.cur.fetchone()

            # workbook
            wb = xlwt.Workbook()
            ws = wb.add_sheet('test_sheet')

            # init basic styles
            header_font = xlwt.Font()
            header_font.name = 'Arial'
            # You set the font's height in "twips", which are 1/20 of a point
            header_font.height = 10*20
            header_font.bold = True
            # borders
            header_borders = xlwt.Borders()
            header_borders.left = xlwt.Borders.THIN
            header_borders.right = xlwt.Borders.THIN
            header_borders.top = xlwt.Borders.THIN
            header_borders.bottom = xlwt.Borders.THIN

            # font and borders
            header_style = xlwt.XFStyle()
            header_style.font = header_font
            header_style.borders = header_borders

            # bg colour
            header_pattern = xlwt.Pattern()
            header_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            # silver
            header_pattern.pattern_fore_colour = 0x16
            header_style.pattern = header_pattern

            # body style
            body_font = xlwt.Font()
            body_font.name = header_font.name
            # You set the font's height in "twips", which are 1/20 of a point
            body_font.height = header_font.height

            body_borders = header_borders
            body_pattern = xlwt.Pattern()
            body_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            # white
            body_pattern.pattern_fore_colour = 0x09

            body_style = xlwt.XFStyle()
            body_style.font = body_font
            body_style.borders = body_borders
            body_style.pattern = body_pattern


            # footer style
            footer_font = xlwt.Font()
            footer_font.name = header_font.name
            # You set the font's height in "twips", which are 1/20 of a point
            footer_font.height = header_font.height
            footer_font.bold = True
            # borders
            footer_borders = header_borders
            #bg colour
            footer_pattern = header_pattern

            # now make up columns
            columns = self.cur.description
            # list of excel formats for all columns
            col_formats = list()
            header_list = list()
            col_num = 0
            for col in columns:
                s = col[0]
                if type(col[0]) is str:
                    s = col[0].decode('utf-8')
                elif type(col[0]) is unicode:
                    s = col[0]
                else:
                    print "type:" + str(type(col[0]))
                header_list.append(s)
                
                col_data_type = connector.get_col_type(col)
                if col_data_type == 'date':
                    fmt_str = 'dd.mm.yyyy'
                elif col_data_type == 'Decimal':
                    scale = connector.get_scale(col)
                    if scale > 0:
                        fmt_str = '#,##0.' + '0'*scale
                    else:
                        fmt_str = '#,##0'
                else:
                    fmt_str = 'General'

                col_formats.append(fmt_str)
                # row col
                # header
                ws.write(0, col_num, s, header_style)
                col_num += 1


            #tempfile.write((sep.join(header_list) + nl).encode(enc))
            #print sep.join(header_list) + "\n"
            row_num = 1 # headers are done TODO what if no header?
            num_rows = 0
            while row is not None:
                col_num = 0
                for val in row:
                    if type(val) is str:
                        val = val.decode('utf-8')
                    #elif type(col[0]) is unicode:
                        #s = col[0]
                    # formats
                    body_style.num_format_str = col_formats[col_num]
                    ws.write(row_num, col_num, val, body_style)
                    col_num += 1
                # totals
                self.update_totals(row)

                row = self.cur.fetchone()
                row_num += 1
                num_rows += 1

            # deal with totals
            number_of_totals = len(self.totals_array)
            if need_totals and (num_rows > 0):
                for col_num in range(len(columns)):
                    cell_style = xlwt.XFStyle()
                    cell_style.font = footer_font
                    cell_style.borders = footer_borders
                    cell_style.pattern = footer_pattern

                    if number_of_totals > col_num:
                        # don't lower it. yet.
                        total_heading = self.totals_array[col_num].strip()
                        lower_total_heading = total_heading.lower()

                        # check no heading
                        heading_rows = 1
                        if self.header == self.ATTR_HEADER_VAL_NO:
                            heading_rows = 0

                        start_cell_address = self.make_cell_address(heading_rows, col_num)
                        end_cell_address = self.make_cell_address(heading_rows+num_rows-1, col_num)
                        formula_range = "%s:%s" % (start_cell_address, end_cell_address)

                        if lower_total_heading == 'sum':
                            formula = xlwt.Formula("SUM(%s)" % formula_range)
                            cell_style.num_format_str = col_formats[col_num]
                            ws.write(row_num, col_num, formula, cell_style)
                        elif lower_total_heading == 'avg':
                            cell_style.num_format_str = col_formats[col_num]
                            formula = xlwt.Formula("AVERAGE(%s)" % formula_range)
                            ws.write(row_num, col_num, formula, cell_style)
                        elif lower_total_heading == 'count':
                            cell_style.num_format_str = 'General'
                            formula = xlwt.Formula("ROWS(%s)-COUNTBLANK(%s)" % (formula_range, formula_range))
                            ws.write(row_num, col_num, formula, cell_style)
                        elif lower_total_heading == 'min':
                            cell_style.num_format_str = col_formats[col_num]
                            formula = xlwt.Formula("MIN(%s)" % formula_range)
                            ws.write(row_num, col_num, formula, cell_style)
                        elif lower_total_heading == 'max':
                            cell_style.num_format_str = col_formats[col_num]
                            formula = xlwt.Formula("MAX(%s)" % formula_range)
                            ws.write(row_num, col_num, formula, cell_style)
                        else:
                            # it's just a string. Maybe empty
                            cell_style.num_format_str = 'General'
                            ws.write(row_num, col_num, total_heading, cell_style)
                    else:
                        # we've run out of totals. just make cells empty
                            total_heading = ''
                            cell_style.num_format_str = 'General'
                            ws.write(row_num, col_num, total_heading, cell_style)
                        

            wb.save(tempfile)
                    
            self.con.close()
            self.con = None
        except DwException, e:
            print e
            if self.con is not None:
                self.con.close()
            raise e
            
#        except Exception, e:
#            print e
#            if self.con is not None:
#                self.con.close()
#            
#            # reraise it wrapped in our class
#            raise DwException(db_name, "Some source exception", e)
