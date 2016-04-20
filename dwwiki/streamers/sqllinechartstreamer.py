#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings
import re
import os
import cherrypy
import dwstreamer
from dwwiki.dwexceptions import DwException
from pyparsing import Word, Literal, Keyword, alphas, alphanums, delimitedList, oneOf, \
    Optional, Forward, ZeroOrMore, Empty, SkipTo, Group, Suppress, Dict, CharsNotIn
import traceback
# plot
import matplotlib

# need this in order to escape graphical desktop backends
matplotlib.use('Agg')
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import ColorConverter
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
import tempfile
import base64
import cStringIO
import urllib
import dwwiki.connectors



class SqlLineChartStreamer(dwstreamer.BaseDwStreamer):
    """Creates a simple line chart
    A query should return columns in a given order:
    1st - An x-axis tick marks
    2nd - y value
    3rd - etc. other lines if there is more than one
    """

    TAGNAME = 'sqllinechart'
    
    # === Attributes that can be used with tagname sqllinechart ===

    # this is as usual
    ATTR_DB = 'db'

    ATTR_TITLE = 'title'
    ATTR_WIDTH = 'width'
    ATTR_HEIGHT = 'height'
    ATTR_XLABEL = 'xlabel'
    ATTR_YLABEL = 'ylabel'
    ATTR_FONT_SIZE = 'fontsize'
    # grid lines to draw. Can be 'x', 'y', and 'both'
    ATTR_GRID = 'grid'
    # min and max y values. In floats or integers. Otherwise ignored.
    ATTR_MINY = 'miny'
    ATTR_MAXY = 'maxy'

    # Here we may specify several colors delimited by commas
    # Like green, red, black separated by commas
    ATTR_LINE_COLOR = 'linecolor'

    # line width in pixels
    ATTR_LINE_WIDTH = 'linewidth'

    # the line color if user hasn't specified one
    DEFAULT_LINE_COLOR = 'black'

    ATTR_MARKER = 'marker'
    ATTR_MARKER_DEFAULT = ''

    # the line color if user has specified it,
    # but made an error
    USER_ERROR_LINE_COLOR = 'grey'

    ATTR_LEGEND = 'legend'
    ATTR_VALUE_YES = 'yes'
    ATTR_VALUE_NO = 'no'
    ATTR_LEGEND_DEFAULT_VALUE = ATTR_VALUE_YES
            
    # maximum number of line points allowed
    # if there is more, just don't draw them
    MAX_X_POINTS = 20000

    # maximum number of parallel lines that can be shown
    # simultaneously.
    MAX_LINE_SETS = 20

    # default top margin over the top of the maximum y value
    # measured in fractions of the difference between min and max
    # values
    DEFAULT_TOP_Y_AXIS_MARGIN = 0.1

    # font size for text and tick marks
    DEFAULT_FONT_SIZE = 10
    
    def factory(self):
        return SqlLineChartStreamer()

    def make_unicode_or_none(self,val):
        """ Given a value try to make a unicode string
        out of it, transforming strings, numbers and dates.
        Or make it None. Assume non-unicode strings
        are in utf-8
        """
        ret = None
        if type(val) is str:
            ret = val.decode('utf-8')
        elif type(val) is unicode:
            ret = val
        else:
            ret = unicode(val)

        return ret
        
    def get_tagname(self):
            return self.TAGNAME

    # gets a database connection
    # it should work with several connections
    # throws a DWDatabaseError 
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

    def parse_block(self, block_text):
        """Parses sql block into tokens
        """

        # Valid grammar looks like this:
        #   {sqllinechart: title='Some string' | colors=green, yellow}

        # make a grammar
        block_start = Literal("{")
        sql_start = Keyword(self.TAGNAME, caseless=True)
        colon = Literal(":")
        sql_end = Literal("}")
        separator = Literal("|")
        block_end = Keyword("{" + self.TAGNAME + "}", caseless=True)
        
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
        
    
    def process_block(self, block_text, user, block_id, **params):

        def int_or_none(val):
            """Returns an integer or none. May pass anything
            """
            try:
                ret = int(val)
            except ValueError:
                ret = None
            return ret
        
        def float_or_none(val):
            """Returns a float or none. May pass anything
            """
            if val is None:
                return val
            else:
                try:
                    ret = float(val)
                except ValueError:
                    ret = None
                return ret

        def int_or_default(val, default=0):
            """ Returns int or a given default
            """
            try:
                ret = int(val)
            except ValueError:
                ret = default

            return ret

        try:
            tokens = self.parse_block(block_text)
        except Exception, e:
            traceback.print_exc()
            # reraise it wrapped in our class
            raise DwException('', "Errpr in graph definition", e)

        # get our tokens
        db_name = tokens.get(self.ATTR_DB, settings.DATABASE_DEFAULT_ALIAS).strip()

        # chart title. empty by default
        chart_title = tokens.get(self.ATTR_TITLE, '').strip()

        # line colors
        line_color_str = tokens.get(self.ATTR_LINE_COLOR, self.DEFAULT_LINE_COLOR).strip()
        line_color_str = line_color_str.encode('utf-8')
        # separate into array
        # this is not final. Probably there are errors here.
        # We'll deal with it later, when we read the columns
        line_color_list = line_color_str.split(',')

        # line style.
        marker_str = tokens.get(self.ATTR_MARKER, self.ATTR_MARKER_DEFAULT).strip()
        #line_style_list = line_style_str.split(',')
        # TODO check line styles

        # chart width and height in pixels. Beware, the user
        # inevitably will write anything but valid numbers
        chart_width = int_or_none(tokens.get(self.ATTR_WIDTH, '').strip())
        chart_height = int_or_none(tokens.get(self.ATTR_HEIGHT, '').strip())
        xlabel = tokens.get(self.ATTR_XLABEL, '').strip()
        ylabel = tokens.get(self.ATTR_YLABEL, '').strip()
        font_size = int_or_default(tokens.get(self.ATTR_FONT_SIZE, self.DEFAULT_FONT_SIZE))
        if font_size <= 0:
            font_size = self.DEFAULT_FONT_SIZE

        # max and min y
        miny = float_or_none(tokens.get(self.ATTR_MINY, None))
        maxy = float_or_none(tokens.get(self.ATTR_MAXY, None))

        # legend
        legend_str = tokens.get(self.ATTR_LEGEND, self.ATTR_LEGEND_DEFAULT_VALUE).strip()
        # check for errors
        if legend_str not in (self.ATTR_VALUE_YES, self.ATTR_VALUE_NO):
            legend_str = self.ATTR_LEGEND_DEFAULT_VALUE

        # grid
        grid = tokens.get(self.ATTR_GRID, None)
        if grid is not None:
            grid = grid.strip()
            if grid not in ['x', 'y', 'both']:
                grid = None

        # line widths for all the lines in pixels separated by commas
        line_width_str = tokens.get(self.ATTR_LINE_WIDTH, '').strip()

        # also check for negative numbers or zeroes
        if (chart_width is not None) and (chart_height is not None):
            if (chart_width <= 0): 
                chart_width = None
            if (chart_height <= 0):
                chart_height = None
        else:
            # some of them are none
            # set both to none
            chart_width = None
            chart_height = None
        
        con = None
        # if anything, we rethrow the exception
        try:
            db = settings.DATABASES.get(db_name, None)
            # non-existent database - exception
            if db == None:
                raise DwException(db_name, "Unknown database %s." % db_name)
            
            true_sql = tokens.sqltext
            
            # now that we have a sql, try to replace parameters in it.
            # Parameter looks like ${param_name}         
            p = re.compile(u'\$\{[a-z]+[0-9]*\}')
            # get the list of all mentioned params
            lst = p.findall(true_sql)
            # loop through all these variables and try to replace
            # them with params passed to us
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
            #print true_sql
            cur.execute(true_sql)
            row = cur.fetchone()

            
            # TODO Now if row is None it means the set is empty
            # in this case we have to generate a stub
            # for now assume the data is present

            # Get columns for labels
            # We need at least two columns
            # first one is x axis, column heading does not matter
            # the second is y axis values, so are 3rd and subsequent ones
            # their headings are the legend if we have to show it
            columns = cur.description
            col_count = len(columns)
            if col_count < 2:
                raise Exception("There should be at least two columns")

            # Now we can have multiple lines here.
            # col 0 is x axis marks. x axis values we count from zero to 1,2 etc.
            # always. If some rows have nulls in this column, it means
            # there will be no points here.
            # But the x value will be counted anyway.
            # The line will continue as usual.
            # on the previous row value. If a non-null is encountered again
            # on subsequent row, the line will start again there.
            # col 2,3 etc. are other lines.
            # Max allowed number for these columns is set to 20
            # For each line - the color and style is set in graph attributes

            # To plot a line for each column we need two arrays:
            # One - all the y values. If null is encountered, the y value is
            # set to the previous value. If first value is null, it is set to
            # miny value. if miny is none, then to zero.
            # Two - masked x points.
            # Two arrays for each column, arranged as a dictionary 'yvalues', 'xmasked'
            # We don't know beforehand how many columns there are,
            # so we create a list to keep them
            col_values_list = list()

            # x coordinates are the same for all cols, so we make one array
            x_values_list = list()
            
            # collect column titles for cols 1 - ... as labels
            legend_list = list()
            n = 0
            for col in columns:
                # that's column name
                s = col[0]
                if type(s) is str:
                    s = s.decode('utf-8')
                elif type(s) is unicode:
                    s = col[0]
                if n > 0:
                    legend_list.append(s)
                n += 1
            

            # now deal with line color for each column
            # TODO line colors should be specified exactly
            # like matplotlib understands
            color_converter = ColorConverter()

            final_color_list = list()
            for i in range(0,col_count-1):
                # Just in case the user specified less colors, than columns
                if i < len(line_color_list):
                    color_str = line_color_list[i]
                else:
                    # we have more columns, than colors specified by user
                    color_str = self.DEFAULT_LINE_COLOR
                
                # The color may well be gibberish
                try:
                    color_rgba = color_converter.to_rgba(color_str)
                except Exception, e:
                    #sys.stderr.write("Color error: %s\n" % color_str)
                    color_str = self.USER_ERROR_LINE_COLOR

                final_color_list.append(color_str)

                # now add a dictionary for each column
                d = {'yvalues': list(), 'xmasked': list()}
                col_values_list.append(d)

#            list_of_lists_of_x_values = list()
#            list_of_lists_of_y_values = list()
            

            # 80 dots per inch. So 7 x 4 inches will make 560 x 320 pixels 
            if (chart_width > 0) and (chart_height > 0):
                fig = plt.figure(figsize=[chart_width / 80, chart_height / 80], dpi=80)
            else:
                fig = plt.figure()
            ax = fig.add_subplot(111)

            # col 0 is x labels
#            for i in range(1, col_count):
#                x_axis_values = list()
#                y_axis_values = list()
#                list_of_lists_of_x_values.append(x_axis_values)
#                list_of_lists_of_y_values.append(y_axis_values)

            # row counter, i.e. x value counter starting from 0
            x_value_counter = 0

            # tick_marks as x values. An array
            x_tick_marks = list()

            # tick_labels - same sa tick_marks
            x_tick_labels = list()

            while row is not None:
                # check for row number and stop if needs be
                if x_value_counter > self.MAX_X_POINTS:
                    break

                # Try to decode tick label
                mark = row[0]
                if mark is None:
                    # No tick mark or value here
                    pass
                else:
                    if type(mark) is str:
                        mark = mark.decode('utf-8')
                    elif type(mark) is unicode:
                        pass
                    else:
                        # TODO maybe a number
                        # we need to convert it to a string
                        # according to it's type (integer, decimal, float)
                        # date, time, datetime
                        mark = unicode(mark)

                if (mark is not None):
                    # add a value to tick marks
                    x_tick_marks.append(x_value_counter)

                    # add col value itself to the array of tick labels
                    x_tick_labels.append(mark)

                # Tick and x label is done.
                # Now add x value
                x_values_list.append(x_value_counter)


                # Now for each subsequent column
                # try to establish y values for each line
                #print col_values_list
                for i in range(0, col_count-1):
                    # get our dictionary of y values and masked x values
                    d = col_values_list[i]

                    value = row[i+1]
#                    y_axis_values = list_of_lists_of_y_values[i]
#                    x_axis_values = list_of_lists_of_x_values[i]
                    #print y_axis_values

                    # For null values. If we already have
                    # an array of y values for this column, it means it's time
                    # to draw a line. If not - just skip it and clear x and y
                    # arrays for the next line if we find one in next rows
                    if value is None:
                        # this is a gap in a line. add current x value
                        # to masked array
                        masked_x_list = d['xmasked']
                        masked_x_list.append(x_value_counter)
                        y_list = d['yvalues']
#                        if x_value_counter == 0:
                        y_list.append(None)

#                        # now draw a line
#                        if len(y_axis_values) > 0:
#                            # TODO apply line style here.
#                            color_rgba = final_color_list[i]
#
#                            # get a label
#                            line_label = legend_list[i+1]
#
#                            #ax.plot(x_axis_values, y_axis_values,
#                            #        color=color_rgba,
#                            #        label=line_label)
#                            
#                            ax.plot(x_axis_values, y_axis_values,
#                                    color=color_rgba)
#
#                            # Now clear both arrays for next parts of line
#                            x_axis_values = list()
#                            list_of_lists_of_x_values[i] = x_axis_values
#                            y_axis_values = list()
#                            list_of_lists_of_y_values[i] = y_axis_values
#
#                        else:
#                            # There were no y values before, so we just skip
#                            # this row 
#                            pass
                    else:
                        # value is not none. Don't draw the line yet. add value to list
                        y_list = d['yvalues']
                    
                        # Convert to float if possible. If not possible,
                        # just set it to zero
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0.0
                        except TypeError:
                            value = 0.0

                        y_list.append(value)
#                        y_axis_values.append(value)
#                        x_axis_values.append(x_value_counter)

                # Here ends the column cycle
                # And here we go to the next row
                x_value_counter += 1
                row = cur.fetchone()

            con.close()
            con = None
            #x_values_list.append(len(x_values_list))
                            
            # Now draw the final set of lines
            for i in range(len(col_values_list)):
                color_rgba = final_color_list[i]
                d = col_values_list[i]
                line_y_values = d['yvalues']

                # Now go through each set of y values
                final_y_values = list()
                final_x_values = list()

                legend_needed = True
                line_label = legend_list[i]

                marker_list = marker_str.split(',')

                if len(marker_list) <= i:
                    final_marker = self.ATTR_MARKER_DEFAULT
                else:
                    final_marker = marker_list[i].strip()

                # check marker
                marker_style = MarkerStyle()
                try:
                    marker_style.set_marker(final_marker)
                except Exception,e:
                    final_marker = ''

                # line width
                line_width_list = line_width_str.split(',')
                if len(line_width_list) > i:
                    final_line_width = line_width_list[i]
                else:
                    final_line_width = '1'

                try:
                    final_line_width = float(final_line_width)
                except Exception, e:
                    final_line_width = 1.0

                if final_line_width > 100.0:
                    final_line_width = 100.0
                elif final_line_width < 0:
                    final_line_width = 1.0
                

                for j in range(len(line_y_values)):
                    if line_y_values[j] is not None:
                        final_y_values.append(line_y_values[j])
                        final_x_values.append(x_values_list[j])
                    else:
                        # none
                        if len(final_y_values) > 0:
                            if legend_needed:

                                ax.plot(final_x_values, final_y_values,
                                        color=color_rgba,label=line_label,
                                        marker=final_marker,
                                        linewidth=final_line_width)

                                #ax.fill_between(final_x_values, final_y_values)
                                #ax.fill_between(final_x_values, 60, final_y_values, color=color_rgba)
                                legend_needed = False
                            else:
                                ax.plot(final_x_values, final_y_values,
                                        color=color_rgba,
                                        marker=final_marker,
                                        linewidth=final_line_width)
                                #ax.fill_between(final_x_values, final_y_values,0)
                                
                        # empty all
                        final_y_values = list()
                        final_x_values = list()

                if len(final_y_values) > 0:
                    if legend_needed:
                        ax.plot(final_x_values, final_y_values,
                                color=color_rgba,label=line_label,
                                marker=final_marker,
                                linewidth=final_line_width)
                        legend_needed = False
                        #ax.fill_between(final_x_values, 60, final_y_values, color='yellow')
                    else:
                        ax.plot(final_x_values, final_y_values,
                                color=color_rgba,
                                marker=final_marker,
                                linewidth=final_line_width)
                        #ax.fill_between(final_x_values, final_y_values)
            
            # deal with legend
            if legend_str == self.ATTR_VALUE_YES:
                ax.legend(loc='best', prop={'size': font_size})

            
            # tick marks
            ax.set_xticks(x_tick_marks)

            # tick labels in a form of graph object
            x_tick_labels_final = ax.set_xticklabels(x_tick_labels)
            plt.setp(x_tick_labels_final, rotation=45, fontsize=font_size)
            
            # grid
            ax.grid(which='major', axis=grid)
    
            # x axis label
            if xlabel <> '':
                ax.set_xlabel(xlabel, fontsize=font_size)

            # y axis label
            if ylabel <> '':
                ax.set_ylabel(ylabel, fontsize=font_size)
            
            # title
            if chart_title <> '':
                ax.set_title(chart_title, fontsize=font_size)

            # font for y major ticks
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(font_size)

            # min and max y
            if (miny is not None) or (maxy is not None):
                ax.set_ylim(miny, maxy)
            else:
                ax.set_ylim(auto=True)
            
            plt.tight_layout()
            
            tempfiledir = cherrypy.config['dwwiki.tempfiledir']
            tempfile.tempdir = tempfiledir
            try:
                f = tempfile.NamedTemporaryFile(delete=False)
                # print graph to a temporary file
                # TODO we assume it prints png. Yet I don't know
                # why. Is it the default format?
                #canvas.print_figure(f)
                #canvas.print_png(f)
                fig.savefig(f)
                f.close()


                # Now all we need is to encode the file in base64,
                # then serve it as an <img>
                input_file = open(f.name,'rb')
                output_file = cStringIO.StringIO()
                base64.encode(input_file, output_file)
                # we have it as a png string
                #yield '<img alt="graph" src="data:image/png;base64,'
                yield '<img alt="graph" src="data:image/png;base64,'
                yield output_file.getvalue()
                yield "\"/>\n"
                output_file.close()
                input_file.close()
            finally:
                os.remove(f.name)

        except DwException, e:
            if con is not None:
                con.close()
            raise e
            
        except Exception, e:
            if con is not None:
                con.close()
            traceback.print_exc()
            # reraise it wrapped in our class
            raise DwException(db_name, "Some source exception", e)
