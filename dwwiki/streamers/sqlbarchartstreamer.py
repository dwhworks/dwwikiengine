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
import tempfile
import base64
import cStringIO
import urllib

# database connectors
import dwwiki.connectors



class SqlBarChartStreamer(dwstreamer.BaseDwStreamer):
    """Creates a vertical bar chart out of sql query
    A query should return columns in a given order:
    1st - An x-axis tick marks
    2nd - Bar value, i.e. y value
    3rd - Optional. Bar color. If absent, bar color will be
          a default bar color
    """

    TAGNAME = 'sqlbarchart'
    
    # === Attributes that can be used with tagname sqlbarchart ===

    # this is as usual
    ATTR_DB = 'db'
    ATTR_TITLE = 'title'
    ATTR_WIDTH = 'width'
    ATTR_HEIGHT = 'height'
    ATTR_XLABEL = 'xlabel'
    ATTR_YLABEL = 'ylabel'
    ATTR_FONT_SIZE = 'fontsize'
    # grid lines to draw. Can be 'x', 'y', and 'both' and 'none'
    # if not specified none is drawn. default is none
    ATTR_GRID = 'grid'

    # x tick labels rotation in degrees
    ATTR_XTICK_ROTATION = 'xtickrotation'
    # default is 45 degrees
    DEFAULT_XTICK_ROTATION = 45
    
    # display legend or not. default no
    ATTR_LEGEND = 'legend'
    ATTR_VALUE_YES = 'yes'
    ATTR_VALUE_NO = 'no'
    DEFAULT_LEGEND = ATTR_VALUE_NO
    
    # LEGEND_LOCATIONS
    ATTR_LEGEND_LOCATION = 'legendlocation'
    DEFAULT_LEGEND_LOCATION = 'best'
    VALID_LEGEND_LOCATIONS = [
        'right',
        'center left',
        'upper right',
        'lower right',
        'best',
        'center',
        'lower left',
        'center right',
        'upper left',
        'upper center',
        'lower center'
    ]

    # stacked chart instead of side by side. Can be yes or no. Default no
    ATTR_STACKED = 'stacked'

    # width of bar or bar group in fractions of 1. min=0.2 max=1 default=0.8
    ATTR_BAR_WIDTH = 'barwidth'
    DEFAULT_BAR_WIDTH = 0.8
    MIN_BAR_WIDTH = 0.2
    MAX_BAR_WIDTH = 1.0

    # the bar color if user hasn't specified one
    DEFAULT_BAR_COLOR = 'grey'

    # the bar color if user has specified it,
    # but made an error
    USER_ERROR_BAR_COLOR = 'black'
            
    # maximum number of bars allowed
    MAX_BARS = 100

    # default bar width in units on x scale. e.g. zero to one is one.
    DEFAULT_BAR_WIDTH = 0.8

    # default top margin over the top of the tallest bar
    # measured in fractions of the height of the tallest bar.
    DEFAULT_TOP_Y_AXIS_MARGIN = 0.1

    # default graph width and height in inches
    #DEFAULT_GRAPH_WIDTH = 7
    #DEFAULT_GRAPH_HEIGHT = 4

    DEFAULT_FONT_SIZE = 10
    
    def factory(self):
        return SqlBarChartStreamer()

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

#        connector = dwwiki.connectors.connectors.get(db['ENGINE'], None)
#
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
        #   {sqlbarchart: title='Some string' | other params as yet unknown...}

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

        def int_or_default(val, default=0):
            """ Returns int or a given default
            """
            try:
                ret = int(val)
            except ValueError:
                ret = default

            return ret

        def float_or_default(val, default=0.0):
            """ Returns float or a given default
            """
            try:
                ret = float(val)
            except ValueError:
                ret = default

            return ret

        tokens = self.parse_block(block_text)

        # get our tokens
        db_name = tokens.get(self.ATTR_DB, settings.DATABASE_DEFAULT_ALIAS).strip()

        # chart title. empty by default
        chart_title = tokens.get(self.ATTR_TITLE, '').strip()

        # chart width and height in pixels. Beware, the user
        # inevitably will write anything but valid numbers
        chart_width = int_or_none(tokens.get(self.ATTR_WIDTH, '').strip())
        chart_height = int_or_none(tokens.get(self.ATTR_HEIGHT, '').strip())
        ylabel = tokens.get(self.ATTR_YLABEL, '').strip()
        xlabel = tokens.get(self.ATTR_XLABEL, '').strip()
        font_size = int_or_default(tokens.get(self.ATTR_FONT_SIZE, self.DEFAULT_FONT_SIZE))
        if font_size <= 1:
            font_size = self.DEFAULT_FONT_SIZE
        if font_size >= 100:
            font_size = self.DEFAULT_FONT_SIZE
        
        # grid
        grid = tokens.get(self.ATTR_GRID, 'none').strip().lower()
        if grid not in ('x','y','both','none'):
            grid = 'none'

        # also check for negative numbers or zeroes
        if (chart_width is not None) and (chart_height is not None):
            if (chart_width <= 0) or (chart_height <= 0):
                # both none
                chart_width = None
                chart_height = None
        else:
            # some of them are none
            # set both to none
            chart_width = None
            chart_height = None

        # xtick rotation
        x_tick_rotation = int_or_default(tokens.get(self.ATTR_XTICK_ROTATION, self.DEFAULT_XTICK_ROTATION))
        if x_tick_rotation > 90:
            x_tick_rotation = 90

        if x_tick_rotation < -90:
            x_tick_rotation = -90

        # legend
        legend_str = tokens.get(self.ATTR_LEGEND, self.ATTR_VALUE_NO).strip().lower()
        if legend_str not in (self.ATTR_VALUE_NO, self.ATTR_VALUE_YES):
            legend_str = self.ATTR_VALUE_NO

        # legend location
        legend_location = tokens.get(self.ATTR_LEGEND_LOCATION, self.DEFAULT_LEGEND_LOCATION).strip().lower()
        # this is not necessary, matplotlib does it by himself,
        # yet we check it here to avoid warnings on stdout
        if legend_location not in self.VALID_LEGEND_LOCATIONS:
            legend_location = self.DEFAULT_LEGEND_LOCATION

        # bar width
        bar_width = float_or_default(tokens.get(self.ATTR_BAR_WIDTH, self.DEFAULT_BAR_WIDTH), self.DEFAULT_BAR_WIDTH)
        if bar_width > self.MAX_BAR_WIDTH:
            bar_width = self.MAX_BAR_WIDTH
        
        if bar_width < self.MIN_BAR_WIDTH:
            bar_width = self.MIN_BAR_WIDTH

        # stacked
        stacked = tokens.get(self.ATTR_STACKED, self.ATTR_VALUE_NO).strip().lower()
        if stacked not in (self.ATTR_VALUE_YES, self.ATTR_VALUE_NO):
            stacked = self.ATTR_VALUE_NO

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
            cur.execute(true_sql)
            row = cur.fetchone()

            
            
            # TODO Now if row is None it means the set is empty
            # in this case we have to generate a stub
            # for now assume the data is present

            # Get columns for labels
            # We need at least two columns
            # first one is x axis, column heading does not matter
            # the second is y axis values
            # the third one is the color of values
            # if there is no third column,  use default color
            # which is gray
            columns = cur.description
            col_count = len(columns)
            if col_count < 2:
                raise DwException(db_name, "There should be at least two columns")

            # second column should be a number. Don't test it here.
            # we will try to test each value

            # every odd column is value
            # every even column is color

            # Now traverse all the rows
            # x_tick_marks is col 0 values
            x_tick_marks = list()

            # y_values is an array of bar heights
            # stored in the second column, fourth etc. columns

            # this is array of arrays
            y_values_array = list()
            y_colors_array = list()
            for i in range(1,col_count):
                is_value = i % 2 == 1
                is_color = i % 2 == 0
                if is_value is True:
                    y_values = list()
                    y_values_array.append(y_values)
                    # add color array in any case
                    y_colors = list()
                    y_colors_array.append(y_colors)
                #if is_color is True:
                    #y_colors_array.append(y_colors)
                
            #y_values = list()
            
            # bar_colors is an array of bar colors
            # stored in the third column
            # if there is no third column,
            # assume the color is grey
            #y_colors = list()

            # Now traverse. If row count is too big,
            # just stop where it exceeds the maximum allowed number
            # which we set to 100 for now
            curr_bar = 0

            color_converter = ColorConverter()

            while row is not None:
                # tick mark as unicode
                mark = row[0]
                if mark is None:
                    mark = ''
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

                x_tick_marks.append(mark)

                # collect values and colors
                for i in range(1,col_count):
                    is_value = i % 2 == 1
                    is_color = i % 2 == 0

                    # value itself. plot does not support Decimal,
                    # need to convert to float
                    if is_value is True:
                        value_index = i / 2
                        y_values = y_values_array[value_index]

                        value = row[i]
                        tp = type(value).__name__
                        if tp is 'Decimal':
                            value = float(value)

                        # all nulls are replaced with zeroes
                        if value is None:
                            value = 0.0

                        y_values.append(value)
                        
                        # now colors
                        color_col = i+1

                        y_colors = y_colors_array[value_index]

                        # color himself +1 col if exists
                        color_str = None
                        
                        if color_col < len(row):
                            color_str = self.make_unicode_or_none(row[i+1])

                        if color_str is None:
                            color_str = self.DEFAULT_BAR_COLOR

                        # Now try to make a color. If it's unsuccessful,
                        # it returns an exception
                        try:
                            color_rgba = color_converter.to_rgba(color_str)
                        except Exception, e:
                            #sys.stderr.write("Color error: %s\n" % color_str)
                            color_rgba = color_converter.to_rgba(self.USER_ERROR_BAR_COLOR)

                        # Hopefully, color_rgba is now set
                        # to a tuple of R, G, B and Alpha
                        y_colors.append(color_rgba)

                # increment row counter
                curr_bar += 1
                if curr_bar >= self.MAX_BARS:
                    break
                else:
                    row = cur.fetchone()

            # Now we have collected all the values, marks and colors

            con.close()
            con = None
            
            # Build a graph
            

            # 80 dots per inch. So 7 x 4 inches will make 560 x 320 pixels 
            if (chart_width > 0) and (chart_height > 0):
                fig = plt.figure(figsize=[chart_width / 80, chart_height / 80], dpi=80)
            else:
                fig = plt.figure()
                


            ax = fig.add_subplot(111)
            
            # data size
            #N = len(curr_bar) # number of bar groups - scale units for x axis = number of query rows

            # arrange N between 0 and N-1. Returns an array
            ind = np.arange(curr_bar) # distribute equally

            # todo expose bar width
            if stacked == self.ATTR_VALUE_NO:
                width = bar_width / len(y_values_array) # width of the bars (measures?)
            else:
                width = bar_width

            min_value = 0
            max_value = 0

            for y_values in y_values_array:
                # remember it may be negative
                temp_min_value = min(y_values)
                min_value = min(temp_min_value, min_value)
                if min_value > 0:
                    min_value = 0

                temp_max_value = max(y_values)
                max_value = max(temp_max_value, max_value)
                if max_value < 0:
                    max_value = 0

            # now add additional 10% of min-max range at the top
            value_range = max_value - min_value
            top_y_axis_margin = value_range * self.DEFAULT_TOP_Y_AXIS_MARGIN

            # no margin for bottom
            bottom_y_axis_margin = 0

            # if we have negative bars, set margin below too
            if min_value < 0:
                bottom_y_axis_margin = top_y_axis_margin

            # here we set final max and min y axis values to account for our margins
            max_y_axis_value = max_value + top_y_axis_margin
            min_y_axis_value = min_value - bottom_y_axis_margin

            # cycle through values and draw bars
            for i in range(len(y_values_array)):
                y_values = y_values_array[i]
                y_colors = y_colors_array[i]

                # bar labels
                # get a description
                # it's in columns 1,3,5 etc.
                # i=0 => col=1
                # i=1 => col=3
                col_index = i*2+1
                col = columns[col_index]
                bar_label = col[0]
                if type(col[0]) is str:
                    bar_label = col[0].decode('utf-8')
                elif type(col[0]) is unicode:
                    bar_label = col[0]
                
                # The Drawing
                if stacked == self.ATTR_VALUE_NO:
                    rects1 = ax.bar(ind+i*width, y_values, width, color=y_colors, label=bar_label)
                else:
                    rects1 = ax.bar(ind, y_values, width, color=y_colors, label=bar_label)

            ax.set_xlim(-1+bar_width, len(ind))
            
            ax.set_ylim(min_y_axis_value, max_y_axis_value)

            # draw horizontal grid lines
            if grid <> 'none':
                ax.grid(which='major', axis=grid)

            if ylabel <> '':
                plt.ylabel(ylabel, fontsize=font_size)

            if xlabel <> '':
                plt.xlabel(xlabel, fontsize=font_size)

            ax.set_title(chart_title, fontsize=font_size)

            # font for y major ticks
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(font_size)
            
            # ticks on top and bottom
            ax.set_xticks(ind + bar_width/2)

            #canvas = FigureCanvasAgg(fig)

            x_tick_labels = ax.set_xticklabels(x_tick_marks)

            plt.setp(x_tick_labels, rotation=x_tick_rotation, fontsize=font_size)

            # legend
            if legend_str == self.ATTR_VALUE_YES:
                ax.legend(loc=legend_location, prop={'size': font_size})

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



            # now encode it
            #input_file = open('graph.png', 'rb')
            #output_file = open('graph.base64', 'w')
            #base64.encode(input_file, output_file)
            #input_file.close()
            #output_file.close()

            #plt.figure(1)
            #plt.subplot(211)
            #plt.plot([1,2,3,4], [1,4,9,16], 'r', label='exchange rate', linewidth=2)
            #plt.subplot(212)
            #plt.plot([2,3,4,5], [2,3,1,0.5], 'b', linewidth=2)
            #plt.hist2d(([1,2,3,4], [7,8,3,5]))
            #plt.axis([0,6,0,10])
            #plt.xlabel('dates')
            #plt.ylabel(u'доллары')
            #plt.show()
            #plt.savefig('graph.png')

        except DwException, e:
            if con is not None:
                con.close()
            raise e
            
#        except Exception, e:
#            if con is not None:
#                con.close()
#            traceback.print_exc()
#            # reraise it wrapped in our class
#            raise DwException(db_name, "Some source exception", e)
