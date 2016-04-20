#!/usr/bin/python
# -*- coding: utf-8 -*-

import markdown
import codecs
import htmlconstants
import cherrypy
import time
import re
#import mysql.connector
#from sqltablestreamer import SqlTableStreamer
#from sqlinlinestreamer import SqlInlineStreamer
import settings
import os
import tempfile
from cherrypy.lib.static import serve_file
from dwexceptions import DwException
import traceback
import utils
import urllib
import pdfkit

# markdown streamer. Used to output results to http server or to client
class MdStreamer(object):
    """A markdown processor that yields it's results"""

    def __init__(self):
        # inialize our parsers dictionaries
        self.block_parsers = dict()
        self.inline_parsers = dict()

    def add_block_parser(self, parser):
        """Add a parser as a block parser"""
        #print parser.get_tagname()
        self.block_parsers[parser.get_tagname()] = parser

    def add_inline_parser(self, parser):
        """Adds a parser to inline parser list, i.e. parsers that
        process sql or whatever before the whole text is fed to markdown processor"""
        self.inline_parsers[parser.get_tagname()] = parser
        

    def stream_to_response(self, filename, access_to_write, printable, *vpath, **params):
        """streams as http response
        supposedly the existence of the file is already checked"""

        base = cherrypy.config.get('tools.proxy.base','')
        get_params = cherrypy.request.request_line.split()[1]
        target = ''
        if get_params <> '':
            target = urllib.quote(base + get_params)
        input_file = codecs.open(filename, mode="r", encoding="utf-8")
        
        line = input_file.readline()

        src_str = ''
        out_str = ''
        parser_keyword = ''
        seen_start = False
        sql_block = []
        block_id = 0

        # init markdown
        #md = markdown.Markdown()
        md = markdown.Markdown(extensions=['markdown.extensions.tables'])
        
        user = cherrypy.session.get('user', '')
        
        # header

        # source url
        # vpath may not contain the actual filename, but represent
        # a directory, in which case the file is index
        # filename passed to us is a real filesystem filename
        if len(vpath) > 0:
            # remove language
            new_path = '/'.join(vpath)
            if new_path[:2] in settings.SUPPORTED_LANGUAGES:
                new_path = new_path[3:]
            # TODO extract filename, see if it's index and vpath is a directory
            basename = os.path.basename(filename)
            if basename == 'index.markdown':
                if vpath[-1] == 'index': 
                    source_url = base + '/' + new_path + '.markdown'
                else:
                    source_url = base + '/' + new_path + '/index.markdown'
            else:
                source_url = base + '/' + new_path + '.markdown'
                
        else:
            source_url = base + '/index.markdown'

        # edit url
        edit_url = ''
        edit_str = ''
#        if access_to_write is True:
#            edit_url=base + cherrypy.request.request_line.split()[1]
#            if edit_url.find('?') >= 0:
#                edit_url += '&action=edit'
#            else:
#                edit_url += '?action=edit'
#            edit_str=_('LC_EDIT')

        page_menu = utils.make_page_menu(langs=True, edit=access_to_write)

        # set title
        page_title = settings.ROOT_DIRECTORY_TITLE
        if len(vpath) > 0:
            s = vpath[-1]
            if s not in settings.SUPPORTED_LANGUAGES:
                page_title = s

        if printable is False:
            html_header = utils.get_report_header(*vpath)
        else:
            html_header = utils.get_printable_report_header(*vpath)

        # message
        msg = cherrypy.session.get('info_message', '')
        if msg <> '':
            msg = htmlconstants.PAGE_INFO_MSG.format(message_str=msg)
            cherrypy.session['info_message'] = ''

        yield_str = html_header.format(base=base, title=page_title,
                                       notice=msg,
                                       page_menu=page_menu)

        yield yield_str

        # re for parsing additional parsers
        parser_re = re.compile('^\{([a-z]+)[:\}]')
        # re for parsing parameter value
        param_re = re.compile(u'\$\{[a-z]+[0-9]*\}')
        # blocks that we escape
        escape_block_start = '<code>'
        escape_block_end = '</code>'
        escape_text = False
        while line:
            if escape_text is False:
                if line.find(escape_block_start) == 0:
                    escape_text = True
            else:
                if line.find(escape_block_end) == 0:
                    escape_text = False
            if escape_text is False:
                match = parser_re.search(line)
            else:
                match = None

            if match is not None:
                if seen_start:
                    # check for previous parser keyword
                    new_parser_keyword = match.group(1)
                    if new_parser_keyword == parser_keyword:
                        # this is the end of the parser block
                        # append the line
                        sql_block.append(line)
                        seen_start = False
                        # now if the parser is inline, call it, wait for return,
                        # then pass it's return to markdown
                        found_parser = False
                        parser = self.inline_parsers.get(parser_keyword, None)
                        if parser is not None:
                            # found inline parser
                            res = ''
                            try:
                                block_id += 1
                                for s in parser.process_block(sql_block, user, **params):
                                    # it yields
                                    res += s
                            except DwException, e:
                                # TODO handle other, unknown exceptions
                                error_type = type(e).__name__
                                error_msg = str(e)
                                source_error = e.source_error
                                if source_error <> None:
                                    error_type = type(source_error).__name__
                                    error_msg = str(source_error)
                                error_msg = error_msg.replace("\n", "<br/>\n")
                                error_path = '/'
                                error_db = e.db_name
                                error_user = user
                                if len(vpath) > 0:
                                    # TODO join by simple '/', not by os delimiter
                                    for el in vpath:
                                        error_path = os.path.join(error_path, el)

                                yield htmlconstants.SQL_ERROR_MSG.format(
                                                error_type=error_type,
                                                error_msg=error_msg,
                                                error_path=error_path,
                                                error_db=error_db,
                                                error_user=error_user
                                )
                            # add to markdown
                            src_str += res 
                        else:
                            # try a block parsers
                            parser = self.block_parsers.get(parser_keyword, None)
                            if parser is not None:
                                # pass previous block to markdown
                                if src_str <> '':
                                    out_str = md.convert(src_str)
                                    yield out_str
                                    # reset
                                    src_str = ''
                                # now it will yield directly
                                try:
                                    block_id += 1
                                    for s in parser.process_block(sql_block, user, block_id, **params):
                                        yield s
                                except DwException, e:
                                    traceback.print_exc()
                                    # TODO handle other, unknown exceptions
                                    error_type = type(e).__name__
                                    error_msg = str(e)
                                    source_error = e.source_error
                                    if source_error <> None:
                                        error_type = type(source_error).__name__
                                        error_msg = str(source_error)
                                    error_msg = error_msg.replace("\n", "<br/>\n")
                                    error_path = '/'
                                    error_db = e.db_name
                                    error_user = user
                                    if len(vpath) > 0:
                                        # TODO join by simple '/', not by os delimiter
                                        for el in vpath:
                                            error_path = os.path.join(error_path, el)

                                    yield htmlconstants.SQL_ERROR_MSG.format(
                                                    error_type=error_type,
                                                    error_msg=error_msg,
                                                    error_path=error_path,
                                                    error_db=error_db,
                                                    error_user=error_user
                                    )

                            else:
                                # no parser found. leave block as is and continue
                                src_str = src_str + ''.join(sql_block)
                                sql_block = []

                        parser_keyword = ''
                    else:
                        # TODO improper ending keyword
                        pass
                else:
                    # not seen_start. This is probably the first parser keyword. Check it
                    parser_keyword = match.group(1)
                    seen_start = True
                    # a block of lines to pass to a parser
                    sql_block = []
                    # now we collect all lines that should be passed to a parser
                    sql_block.append(line)
            else:
                # match not found. we either in a parser block or in simple md
                if seen_start:
                    sql_block.append(line)
                else:
                    # pass the line to a block
                    # to be passed later to md

                    # try to find ${param} 
                    lst = param_re.findall(line)
                    # loop through all these variables and try to replace
                    # them with params passed to us
                    for item in lst:
                        stripped_item = item[2:-1]
                        # TODO check for default value here
                        # and avoid xss injections
                        value = ''
                        if stripped_item in params:                
                            value = params[stripped_item]
                            #value = urllib.unquote(value)
                            # replace it
                            line = line.replace(item, value)
                    src_str = src_str + line


            line = input_file.readline()

        input_file.close()

        # last block of text
        if src_str <> '':
            out_str = md.convert(src_str)
            yield out_str
            # reset
            src_str = ''

        # footer
        if printable is False:
            html_footer = utils.get_report_footer(*vpath)
        else:
            html_footer = utils.get_printable_report_footer(*vpath)
        html_footer = html_footer.format(source_url=source_url, page_menu=page_menu)

        yield html_footer


    def stream_to_pdf(self, filename, access_to_write, printable, *vpath, **params):
        """ Streams as pdf to response
        """
        # collect output from stream_to_response into file
        tempfiledir = cherrypy.config['dwwiki.tempfiledir']
        tempfile.tempdir = tempfiledir
        try:
            f = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
            pdf = tempfile.NamedTemporaryFile(delete=False)
            # write printable html there
            for s in self.stream_to_response(filename, access_to_write, printable, *vpath, **params):
                f.write(s.encode('utf-8'))

            f.close()
            print f.name
            #with open(f.name) as f2:
            pdfkit.from_file(f.name, pdf.name)
            # now convert to pdf
            # we need css file
            

            base_filename = os.path.splitext(os.path.basename(filename))[0]
#            base_filename += '-id' + str(tableid)
            localtime   = time.strftime("%Y-%m-%d", time.localtime())
            # using txt instead of csv. Excel messes up everything
            # if it opens csv. With txt it opens up import dialog.
            base_filename += '-' + localtime + '.' + 'pdf'
            return serve_file(pdf.name, "application/pdf", "attachment", base_filename)
        finally:
            os.remove(f.name)
            os.remove(pdf.name)

    def stream_to_csv_or_xls(self, filename, tableid, format_id='csv', *vpath, **params):
        """Streams any sql-based block as csv
        params should contain csvdownload=n where n is a the number of the required
        {sqlxxx} tag from the beginning of the file starting with one.
        Other params are used as usual. This routine does not yield it's results.
        It simply generates a temporary file and then streams it via serve_file"""

        src_str = ''
        parser_keyword = ''
        seen_start = False
        sql_block = []
        current_tableid = 0
        user = cherrypy.session.get('user', '')

        #find id
        #tableid = params.get('csvdownload', None)
        if tableid is not None:
            # TODO it can well be not a number
            tableid = int(tableid)

        input_file = codecs.open(filename, mode="r", encoding="utf-8")
        line = input_file.readline()
        # re for parsing additional parsers
        parser_re = re.compile('^\{([a-z]+)[:\}]')
        
        while line:
            match = parser_re.search(line)
            if match is not None:
                # found some parser
                if seen_start:
                    # check for previous parser keyword
                    new_parser_keyword = match.group(1)
                    if new_parser_keyword == parser_keyword:
                        # this is the end of the parser block
                        # append the line
                        sql_block.append(line)
                        seen_start = False
                        found_parser = False
                        # Only block parsers may return csv.
                        # We cannot rely upon sqltable alone. It can well be
                        # a chart or whatever.
                        parser = self.block_parsers.get(parser_keyword, None)
                        if parser is not None:
                            try:
                                f = None
                                if current_tableid == tableid:
                                    input_file.close()
                                    # this is the only positive outcome. In any other
                                    # case we return 404, e.g. if there is no such tableid
                                    # create a temp file, ask the parser to spit it's results
                                    # out into it, return the file
                                    tempfiledir = cherrypy.config['dwwiki.tempfiledir']
                                    tempfile.tempdir = tempfiledir
                                    try:
                                        f = tempfile.NamedTemporaryFile(delete=False)
                                        if format_id == 'csv':
                                            parser.process_block_as_csv(f, sql_block, user, **params)
                                        elif format_id == 'xls':
                                            parser.process_block_as_xls(f, sql_block, user, **params)
                        
                                        f.close()
                                        base_filename = os.path.splitext(os.path.basename(filename))[0]
                                        base_filename += '-id' + str(tableid)
                                        localtime   = time.strftime("%Y-%m-%d", time.localtime())
                                        # using txt instead of csv. Excel messes up everything
                                        # if it opens csv. With txt it opens up import dialog.
                                        base_filename += '-' + localtime + '.' + format_id
                                        return serve_file(f.name, "text/csv", "attachment", base_filename)
                                    finally:
                                        os.remove(f.name)


                            except DwException, e:
                                if f is not None:
                                    f.close()
                                # TODO return sensible message
                                raise cherrypy.HTTPError(404, str(e))
                                
                        else:
                            # parser not found. Ignore
                            sql_block = []

                    else:
                        # improper ending keyword
                        pass
                else:
                    # not seen_start. The first parser keyword. Check it
                    current_tableid += 1
                    parser_keyword = match.group(1)
                    seen_start = True
                    # a block of lines to pass to a parser
                    sql_block = []
                    # now we collect all lines that should be passed to a parser
                    sql_block.append(line)
            else:
                # match not found. we either in a parser block or in simple md
                if seen_start:
                    sql_block.append(line)
                else:
                    # we may encounter ${param} in a line
                    pass
                
            line = input_file.readline()
        input_file.close()
        # we should not end here. It means we haven't found the required tableid or a parser.
        # return 401
        raise cherrypy.HTTPError(404, "Requested URL does not exist")

