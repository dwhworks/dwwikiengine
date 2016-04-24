#!/usr/bin/python
# -*- coding: utf-8 -*-

# Translation strings
import gettext
#gettext.install('messages', 'locale', unicode=True)

import os
import cherrypy
import markdown

from cherrypy.lib.static import serve_file
import locale
from string import Template
import utils
import codecs
import settings
import urllib
import htmlconstants
import loginform
import reporteditor
import time
import re
import mdstreamer
#from streamers.sqltablestreamer import SqlTableStreamer
#from streamers.sqlbarchartstreamer import SqlBarChartStreamer
#from streamers.sqllinechartstreamer import SqlLineChartStreamer
#from streamers.sqlinlinestreamer import SqlInlineStreamer
from securityguard import SecurityGuard
from usermanager import UserManager
import HTMLParser


class DWWikiEngine(object):
    def __init__(self):
        # just in case
        locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

        # This object is created once for all users
        self.user_manager = UserManager(settings.SERVICE_DB, settings.PWD_SALT)

        # locale path
        self.locale_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')

        # Streamer lists
        self.block_streamers = list()
        self.inline_streamers = list()

        # Here we add our parsers. This should be made
        # easily extendable for custom parsers
        #self.streamer.add_block_parser(sqltablestreamer.SqlTableStreamer())
        #self.streamer.add_block_parser(sqlbarchartstreamer.SqlBarChartStreamer())
        #self.streamer.add_block_parser(sqllinechartstreamer.SqlLineChartStreamer())
        #self.streamer.add_inline_parser(SqlInlineStreamer())
        # security
        #self.guard = SecurityGuard('fileaccess.cfg', 'userlist.cfg')

    def register_block_streamer(self, streamer):
        self.block_streamers.append(streamer)

    def register_inline_streamer(self, streamer):
        self.inline_streamers.append(streamer)

    def get_streamer(self):
        """ Creates a new streamer per each request for thread safety.
        And returns it.
        """
        res = mdstreamer.MdStreamer()

        # Here we add all our streamers.
        for streamer in self.block_streamers:
            res.add_block_parser(streamer.factory())

        for streamer in self.inline_streamers:
            res.add_inline_parser(streamer.factory())

        #res.add_block_parser(SqlTableStreamer())
        #res.add_block_parser(SqlBarChartStreamer())
        #res.add_block_parser(SqlLineChartStreamer())
        #res.add_inline_parser(SqlInlineStreamer())

        return res


    def check_access(self, action, *vpath):
        """ Check access to some resource with security guard.
        Returns True if granted, False otherwise
        """
        user = cherrypy.session.get('user', '')
        rep_dir = self.reports_dir()
        #access_file = os.path.join(rep_dir, 'fileaccess.conf')
        quick_guard = SecurityGuard(settings.ACCESS_FILE, self.user_manager)
        res = quick_guard.request_access(user, action, *vpath)
        return res

    def goto_login(self, *vpath, **params):
        """ Redirects to login if user is not logged in
        """
        base = cherrypy.config.get('tools.proxy.base', '')
        get_params = cherrypy.request.request_line.split()[1]

        #user = cherrypy.session.get('user', '')
        #if user == '':
        # redirect here to login
        # url requested in the first place will be put
        # into session variable report_requested_at_login
        # the root report is not needed
        if len(vpath) == 0:
            cherrypy.session['report_requested_at_login'] = ''
        else:
            cherrypy.session['report_requested_at_login'] = base + get_params

        # login to specific language
        lang = settings.DEFAULT_LANGUAGE
        #if (len(vpath) > 0) and (vpath[0] in settings.SUPPORTED_LANGUAGES):
        #    lang = vpath[0]

        #raise cherrypy.HTTPRedirect(base + '/' + lang + "/login")
        raise cherrypy.HTTPRedirect(base + '/login')
        #else:
            # user logged in and access denied
            #raise cherrypy.HTTPError(403, "Access to requested URL denied.")

    def check_access_or_goto_login(self, action, *vpath):
        """ Check access to resource. If access denied but user is logged
        in, redirect to login page with message.
        Does not return anything, just raises an exception if needed
        """
        base = cherrypy.config.get('tools.proxy.base','')
        get_params = cherrypy.request.request_line.split()[1]

        #user = cherrypy.session.get('user', '')
        result = self.check_access(action, *vpath)
        if result == False:
            if user == '':
                # redirect here to login
                # url requested in the first place will be put
                # into session variable report_requested_at_login
                # the root report is not needed
                if len(vpath) == 0:
                    cherrypy.session['report_requested_at_login'] = ''
                else:
                    cherrypy.session['report_requested_at_login'] = base + get_params
                        
                raise cherrypy.HTTPRedirect(base + "/login")
            else:
                # user logged in and access denied
                raise cherrypy.HTTPError(403, "Access to requested URL denied.")

    def set_lang(self, lang):
        """Sets current language for user based on sesseion variable
        """
        t = gettext.translation('messages', localedir=self.locale_path, languages=[lang])
        # all strings will be in utf-8. no unicode
        t.install(unicode=False)

    def set_lang_from_vpath(self, *vpath):
#        "set current language depending on language element in path"
        lang = settings.DEFAULT_LANGUAGE
#        if len(vpath) > 0:
#            # we may have language mark
#            if vpath[0] in settings.SUPPORTED_LANGUAGES:
#                lang = vpath[0]
#
        # The language for messages is set
        self.set_lang(lang)
        
    def reports_dir(self):
        """ Returns absolute path for reports storage
        """
        return cherrypy.config['dwwiki.wikidir']

    def find_real_file(self, *vpath):
        """ Finds real file from http path
        returns path to a real file or None if it's not found.
        Accounts for lang
        """
        final_path = None
        # Extract the path
        real_path = self.reports_dir() # this should exist
        lang_path = real_path
        if len(vpath) > 0:
            for el in vpath:
                real_path = os.path.join(real_path, el)
                lang_path = os.path.join(lang_path, el)
#            for el in vpath:
#                # try for language
#                if el in settings.SUPPORTED_LANGUAGES:
#                    lang_path = os.path.join(lang_path, el)
#                else:
#                    real_path = os.path.join(real_path, el)
#                    lang_path = os.path.join(lang_path, el)
 
        # make it absolute just in case
        real_path = os.path.abspath(real_path)
        lang_path = os.path.abspath(lang_path)

        # first try the lang path
        if os.path.isdir(lang_path):
            lang_path = os.path.join(lang_path, 'index.markdown')
        else:
            lang_path += '.markdown'

        if not os.path.exists(lang_path):
            # fall back to path without lang

            if os.path.isdir(real_path):
                # The path can possibly lead not to a file as such,
                # but to a directory. In that case we should return index.markdown
                # if one is present in a directory
                real_path = os.path.join(real_path, 'index.markdown')
            else:
                # it can be a file but witout extension or a nonexistent path
                real_path += '.markdown'
        
            if not os.path.exists(real_path):
                real_path = None
            final_path = real_path
        else:
            # lang_path exists
            final_path = lang_path

        return final_path

    @cherrypy.expose
    def default(self, *vpath, **params):
        base = cherrypy.config.get('tools.proxy.base','')

        #redirect_to_lang = cherrypy.config.get('dwwiki.langredirect', False)
        #if len(vpath) == 0 and redirect_to_lang is True: 
        #    lang = settings.DEFAULT_LANGUAGE
        #    target = base + '/' + lang + '/'
        #    raise cherrypy.HTTPRedirect(target)


        # This is path starting from base and including all params
        get_params = cherrypy.request.request_line.split()[1]
        user = cherrypy.session.get('user', '')

        # The language for messages is set
        self.set_lang_from_vpath(*vpath)

        # -------------------------------------
        # Next thing is to establish the action the user requires.
        # The user may want to do one of the following:
        # 1. Execute a report. It means there should be just a name of report
        #    without .markdown extension. Some parameters that are used in 
        #    report generation may follow. E.g.:
        #    http://dwworks.ru/dwwiki/samplereport?year=2016
        #
        # 2. View report source. Just report source without any editing.
        #    In this case it should be just a path to report file. Like this:
        #    http://dwworks.ru/dwwiki/samplereport.markdown
        #    And no other params?
        #
        # 3. Edit report. That means view report in the editor. If the user
        #    has permission to 'read' report, it should be displayed, even if
        #    the user doesn't have permission to 'write' it. On an attempt
        #    to actually save it, it would be denied.
        #    Here we use a special reserved parameter - 'action'. Like this:
        #    http://dwworks.ru/dwwiki/samplereport?action=edit
        # 
        # All above are meant to use GET request method.
        # If we have a POST request method, it means the user tries to

        # possible actions - 'action=xxx' understood by server
        URL_PARAM_ACTION = 'action'
        URL_ACTION_EDIT = 'edit'

        MARKDOWN_EXT = '.markdown'

        # what should we do?
        # execute
        #
        FINAL_ACTION_UNKNOWN = 0
        FINAL_ACTION_EXECUTE = 1
        FINAL_ACTION_VIEW_SOURCE = 2
        FINAL_ACTION_VIEW_EDITOR = 3
        # var
        final_action = FINAL_ACTION_UNKNOWN

        if cherrypy.request.method == 'GET':

            # if we have no params and file name ends with
            # .markdown, that means read raw text
            if len(vpath) > 0:
                # try for login/logout
                # try for read
                fn = vpath[-1]
                if fn == 'login':
                    method = getattr(self, 'login', None)
                    return method(*vpath, **params)
                elif fn == 'logout':
                    method = getattr(self, 'logout', None)
                    return method(*vpath, **params)
                    

                if fn[-len(MARKDOWN_EXT):] == MARKDOWN_EXT:
                    final_action = FINAL_ACTION_VIEW_SOURCE

            # no result yet
            if final_action == FINAL_ACTION_UNKNOWN:
                # try for edit
                edit = params.get(URL_PARAM_ACTION, '')
                if edit == URL_ACTION_EDIT:
                    final_action = FINAL_ACTION_VIEW_EDITOR
                # nothing. try execute
                else:
                    final_action = FINAL_ACTION_EXECUTE
            
            # Now just feed the request to specific handlers    
            if final_action == FINAL_ACTION_EXECUTE:
                method = getattr(self, 'mkdown', None)
                return method(*vpath, **params)
            elif final_action == FINAL_ACTION_VIEW_SOURCE:
                method = getattr(self, 'display_report_source', None)
                return method(*vpath, **params)
            elif final_action == FINAL_ACTION_VIEW_EDITOR:
                method = getattr(self, 'display_report_editor', None)
                return method(*vpath, **params)
        # end of GET method
        elif cherrypy.request.method == 'POST':
            if len(vpath) > 0:
                # try for login/logout
                # try for read
                fn = vpath[-1]
                if fn == 'login':
                    method = getattr(self, 'login', None)
                    return method(*vpath, **params)
            # maybe a user tried to save the edited report
            # in which case we have in our request line 'action=edit'
            # because the edited form is posted to the same URL
            # it was received from

            # params** here contains both params in url, like 'action=edit' and 'month=2'
            # and form fields too. like editor='report source text'
            action_param = params.get('action', '')
            if action_param == 'edit':
                method = getattr(self, 'save_report_editor', None)
                return method(*vpath, **params)
            else:
                # POST request without action=edit is not allowed
                # exception
                raise cherrypy.HTTPError(405, "Post method with these parameters not implemented.")


    # declare streaming for default page
    default._cp_config = {'response.stream': True}


    # This routine shows the login page
    #@cherrypy.expose
    def login(self, *vpath, **params):
        self.set_lang_from_vpath(*vpath)
        #user = cherrypy.session['user']
        #if user == None:
        user = 'Public'
        base = cherrypy.config.get('tools.proxy.base','')

        if cherrypy.request.method == 'GET':
            # show the form
            # format subheader
            # get requested login
            target_report = params.get('target', '')
            # in case it requests just the top of the server
            if target_report == '/':
                target_report = ''
            if target_report == base + '/':
                target_report = ''


            page_template = utils.get_report_template('loginform.html', *vpath)


            page_menu = utils.make_page_menu(langs=True)
            #subheader = htmlconstants.PAGE_LOGO.format(base=base)
        
            #result = loginform.LOGIN_PAGE_HEADER.format(base=base)
            #result += subheader

            # check for invalid logins
            notice = ''
            if cherrypy.session.get('last_login_incorrect',False):
                # show login incorrect
                notice = loginform.LOGIN_INCORRECT.format(invalid_username=_('LC_INVALID_USERNAME'))

            page = page_template.format(base=base,
                                        title="login",
                                        notice=notice,
                                        lc_login_to_dw_wiki=_('LC_LOGIN_TO_DW_WIKI'),
                                        lc_user_name=_('LC_USER_NAME'),
                                        lc_password=_('LC_PASSWORD'),
                                        lc_navigate_to=_('LC_NAVIGATE_TO'),
                                        lc_log_in=_('LC_LOG_IN'),
                                        target_report=target_report,
                                        page_menu=page_menu)

            return page
        elif cherrypy.request.method == 'POST':
            base = cherrypy.config.get('tools.proxy.base','')
            get_params = cherrypy.request.request_line.split()[1]
            # try to log the user in

            user = ''
            psswrd = ''
            target = ''
            
            if 'user' in params:
                user = params['user']
            if 'psswrd' in params:
                psswrd = params['psswrd']
            if 'target' in params:
                target = params['target']

            user_access = False

            ud = self.user_manager.get_user_data(user)
            if ud is not None:
                user_access = self.user_manager.check_password(ud, psswrd)

            if user_access is True:
                # ok. store user in session and redirect to report
                cherrypy.session['user'] = user
                if target == '':
                    #lang = settings.DEFAULT_LANGUAGE
                    #if len(vpath) > 0:
                    #    if vpath[0] in settings.SUPPORTED_LANGUAGES:
                    #        lang = vpath[0]
                    #target = base + '/' + lang + '/'
                    target = base + '/'

                # remove target from session.
                cherrypy.session['target'] = ''
                # remove invalid logins
                cherrypy.session['invalid_logins'] = 0
                # remove last login incorrect
                cherrypy.session['last_login_incorrect'] = False
                raise cherrypy.HTTPRedirect(target)
            else:
                # TODO unknown user/password.
                # redirect to itself again. target remains in session

                # Track invalid logins to lock user
                invalid_logins = 0
                if 'invalid_logins' in cherrypy.session:
                    invalid_logins = cherrypy.session['invalid_logins']
                invalid_logins += 1
                cherrypy.session['invalid_logins'] = invalid_logins
                cherrypy.session['last_login_incorrect'] = True

                    
                #target = base + '/login'
                # TODO base and get_params base may include some get params
                #raise cherrypy.HTTPRedirect(base + get_params)
                raise cherrypy.HTTPRedirect(get_params)



            raise cherrypy.HTTPError(405, "Method not implemented.")
        else:
            raise cherrypy.HTTPError(405, "Method not implemented.")
            
    login._cp_config = {'response.stream': True}

    # routine used for logout
    @cherrypy.expose
    def logout(self, *vpath, **params):
        base = cherrypy.config.get('tools.proxy.base','/')
        user = cherrypy.session.get('user', '')
        # if user is set, redirect to base.
        # Anyway, just redirect in any case
        cherrypy.session['user'] = ''
        # remove target from session.
        cherrypy.session['target'] = ''
        cherrypy.lib.sessions.expire()
        # TODO generally we should log all login-logout attempts
        lang = '/'
        raise cherrypy.HTTPRedirect(base)
#        if len(vpath) > 0:
#            if vpath[0] in settings.SUPPORTED_LANGUAGES:
#                lang = '/' + vpath[0] + '/'
#        raise cherrypy.HTTPRedirect(base + lang)


    
    def display_report_source(self, *vpath, **params):
        """ Display a markdown file as is.
        Security should be checked before calling this, for
        it is not checked. Nor does this function check
        for correct file extension. Just returns it as text/plain
        """
        real_path = self.reports_dir()
        # vpath should point to existing file. Otherwise we
        # generate 404 not found
        if len(vpath) > 0:
            for el in vpath:
                real_path = os.path.join(real_path, el)
        # make it absolute just in case
        real_path = os.path.abspath(real_path)
        if os.path.isdir(real_path):
            raise cherrypy.HTTPError(404, "Requested URL does not exist")
        else:
            # real_path is a file
            if not os.path.exists(real_path):
                raise cherrypy.HTTPError(404, "Requested URL does not exist")
            else:
                # file exists
                # TODO exceptions. file may not open
                cherrypy.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                input_file = codecs.open(real_path, mode="r", encoding="utf-8")
                result = input_file.read()
                input_file.close()
                return result


    def save_report_editor(self, *vpath, **params):
        """ Saves a reports that has been edited and returns
        may do one of the following:
        1. Return to a page the editor was called from
        2. Just save the report, inform user and stay on the same page
        3. Inform user that a report could not be saved for some reason
           and stay on the same page, displaying edited text
        """
        # try to save
        # check for allowance first
        new_file = False
        base = cherrypy.config.get('tools.proxy.base','')
        get_params = cherrypy.request.request_line.split()[1]
        user = cherrypy.session.get('user', '')
        access_granted = self.check_access('write', *vpath)

        if access_granted:
            # Find a real file if there is one
            # A real filename is stored in url
            real_path = self.find_real_file(*vpath)
    
            if real_path is None:
                # we are about to create a new file
                rd = self.reports_dir()
                for el in vpath[:-1]:
                    rd = os.path.join(rd, el)
                if os.path.exists(rd) and os.path.isdir(rd):
                    # check if the name is good
                    fn = vpath[-1]
                    fn = fn.replace('.markdown', '')
                    # now check
                    # 1-new-report is good
                    # NewReport is bad, as is 1_new_report
                    p = re.compile(u'^[a-z,0-9]+[a-z,0-9,-]+[a-z,0-9]+$')
                    m = p.match(fn)
                    if m is None:
                        raise cherrypy.HTTPError(404, _("LC_URL_DOES_NOT_EXIST"))

                    # file name is good. directory exists. go ahead, create a new file
                    # set flags here
                    new_file = True
                    new_file_name = fn + '.markdown'
                    real_path = os.path.join(rd, new_file_name)    
                else:
                    raise cherrypy.HTTPError(404, _("LC_URL_DOES_NOT_EXIST"))

            # now access granted, file exists or will be created. Check if we have an editor param
            if not 'editor' in params:
                raise cherrypy.HTTPError(400, "Bad request")

            # now editor text is present.
            edit_text = params.get('editor', u'').encode('utf-8')

            # now remove CRLF and set LF instead
            edit_text = edit_text.replace("\r\n", '\n')
            # edit_text now is unicode
            # check if it's empty
            #if edit_text.strip() == '':
                #raise cherrypy.HTTPError(405, "Report text is an empty string. This is not allowed.")

            # now at last now we can save it
            # file may not be allowed for writing
            # with current server permissions
            try:
                # TODO here we must call version control after writing file
                f = open(real_path, 'w')
                f.write(edit_text)
                f.close()
            except Exception, e:
                # TODO don't return exception. Return back to editor
                raise cherrypy.HTTPError(405, _('LC_ERROR_WRITING_TO_FILE'))
                
            # Now redirect to the same URL the editor was called from
            # to test the file contents
            back_link = base + get_params
            
            # remove action=edit
            back_link = back_link.replace('&action=edit', '')
            back_link = back_link.replace('?action=edit', '')
            if back_link[-1:] in ['?', '&']:
                back_link = back_link[0:-1]

            # set the message


            cherrypy.session['info_message'] = _('LC_INFO_REPORT_CHANGES_SAVED')
            # do the redirection

            # if just save, redirect to itself
            if 'save' in params:
                raise cherrypy.HTTPRedirect(base + get_params)
            # this is saveandclose
            else:
                raise cherrypy.HTTPRedirect(back_link)
        else:
            # access not granted. TODO Really we want to go back to
            # editing mode, displaying the changed source.
            # Admin may have revoked privileges while user was working
            # hard on editing the bloody report.
            # for now just throw an exception and happily loose all the changes.
            raise cherrypy.HTTPError(403, "Editing of this report is not allowed for this user.")

    def display_report_editor(self, *vpath, **params):
        """Displays a report editor
        """
        new_file = False
        new_file_name = ''

        # Check access
        base = cherrypy.config.get('tools.proxy.base','')
                
        user = cherrypy.session.get('user', '')

        # this is the line that was used to get here
        get_params = cherrypy.request.request_line.split()[1]

        # this is checked when the file is saved
        #quick_guard = SecurityGuard('fileaccess.cfg', 'userlist.cfg')
        access_to_write = self.check_access('write', *vpath)
        access_to_read = self.check_access('read', *vpath)


        if access_to_read == False:
            # even viewing the editor is not allowed
            # TODO when throwing 403 id doesn't want to work
            # The string is probably not unicode that's why
            raise cherrypy.HTTPError(403, _("LC_READING_REPORT_NOT_ALLOWED"))
            
        real_path = self.find_real_file(*vpath)

        if real_path is None:
            # new file. And it is not a directory, in which
            # case a real file would have been with index
            # show editor only if we have write access
            if not access_to_write:
                raise cherrypy.HTTPError(404, _("LC_URL_DOES_NOT_EXIST"))
            else:
                # we have access to write. File does not exist
                # The user cannot create directories.
                # So assemble the path again from elements.
                # The last element must conform to url rules
                # The previous element must be a real directory
                rd = self.reports_dir()
                for el in vpath[:-1]:
                    rd = os.path.join(rd, el)
                if os.path.exists(rd) and os.path.isdir(rd):
                    # check if the name is good
                    fn = vpath[-1]
                    fn = fn.replace('.markdown', '')
                    # now check
                    # 1-new-report is good
                    # NewReport is bad, as is 1_new_report
                    p = re.compile(u'^[a-z,0-9]+[a-z,0-9,-]+[a-z,0-9]+$')
                    m = p.match(fn)
                    if m is None:
                        raise cherrypy.HTTPError(404, _("LC_URL_DOES_NOT_EXIST"))

                    # file name is good. directory exists. go ahead, create a new file
                    # set flags here
                    new_file = True
                    new_file_name = fn + '.markdown'
                        
                else:
                    raise cherrypy.HTTPError(404, _("LC_URL_DOES_NOT_EXIST"))
                    
                    
        # now read the file
        

        report_text = ''
        #report_text = u'# ' + report_text
        if new_file:
            filename_str = new_file_name
            # generate links upwards
            # If we are at the top, and making a file,
            # last link will always be ./
            links_upwards = ''
            str_level_up = '../'
            if len(vpath) > 1:
                deepness = len(vpath) - 2
                for i in range(deepness):
                    if i == 0:
                        el = settings.ROOT_DIRECTORY_TITLE
                    else:
                        el = vpath[i]
                    links_upwards += '[' + el + '](' + str_level_up * deepness + ") / \n"
                    deepness -=1
            if len(vpath) > 1:
                links_upwards += "[" + vpath[-2] + "](./) / \n"

            report_text = links_upwards + "\n"
            report_text += "# {new_file}\n\n{under_construction}".format(new_file=new_file_name,
                    under_construction=_('LC_UNDER_CONSTRUCTION'))
            cancel_link = 'javascript:history.back();'
        else:
            # opening old file
            input_file = codecs.open(real_path, mode="r", encoding="utf-8")
            line = input_file.readline().encode('utf-8')
            while line:
                report_text += line
                line = input_file.readline().encode('utf-8')

            input_file.close()



            filename_str = os.path.basename(real_path)
            
        # unescape html entities
        # textarea will always replace &lt; into < and we cannot
        # reliably avoid it unless replacing all entities into &amp;lt; etc.
        # When saving it seems to do the reverse.
        to_textarea = re.sub('&(\w+;)', '&amp;\g<1>',  report_text)
        
        relative_path = cherrypy.request.request_line.split()[1]
        
        path_str = base + relative_path
        qmark = path_str.find('?')
        if qmark >= 0:
            path_str = path_str[:qmark]

        # Cancel link. Must point to current page
        cancel_link = base + relative_path
        # remove action=edit
        cancel_link = cancel_link.replace('?action=edit', '')
        cancel_link = cancel_link.replace('&action=edit', '')
        if cancel_link[-1:] in ['?', '&']:
            cancel_link = cancel_link[0:-1]

        if new_file:
            # don't show cancel link for we don't know whence the
            # user has come. Show empty link
            cancel_link = "/"
        
        #cancel_link = 'javascript:history.back();'

        # now render it from template
        page_template = utils.get_report_template('reporteditor.html', *vpath)

        #result = reporteditor.PAGE_HEADER.format(base=base)
        #result += htmlconstants.PAGE_LOGO.format(base=base)

        message_str = cherrypy.session.get('info_message', '')
        cherrypy.session['info_message'] = ''
        if not access_to_write:
            message_str = _('LC_WRITING_REPORT_NOT_ALLOWED')
        elif new_file:
            message_str = _('LC_CREATING_NEW_FILE')

        if message_str <> '':
            message_str = reporteditor.PAGE_INFO_MSG.format(message_str=message_str)
            

        page_menu = utils.make_page_menu(langs=False)

        # set title
        page_title = settings.ROOT_DIRECTORY_TITLE
        if len(vpath) > 0:
            s = vpath[-1]
            if s not in settings.SUPPORTED_LANGUAGES:
                page_title = s
        page_title += ':' + _('LC_EDITOR')

        result = page_template.format(title=page_title,
                                      base=base,
                                      notice=message_str,
                                      page_menu=page_menu,
                                      file_name=filename_str,
                                      full_path=path_str,
                                      save_str=_('LC_SAVE'),
                                      save_and_close_str=_('LC_SAVE_AND_CLOSE'),
                                      cancel_link=cancel_link,
                                      cancel_str=_('LC_CANCEL'),
                                      report_text=to_textarea,
                                      edit_str='')
        return result


    #@cherrypy.expose
    def mkdown(self, *vpath, **params):
        """Returns a page generated with markdown parser.
        """
        
        dwwiki_path = cherrypy.request.request_line.split()[1]
        
#        def make_redirect_url():
#            base = cherrypy.config.get('tools.proxy.base','')
#            new_url = base + '/' + settings.DEFAULT_LANGUAGE + cherrypy.request.request_line.split()[1]   
#            return new_url


        # first check the path with security guard
        # the vpath may be anything here, a pile of rubbish for example.
        # It may be that someone scans the server.
        # If the user logged in, and requested file does not exist,
        # and the user has permission to create new files,
        # redirect to editor for creation of a new file
        # language does not matter here, by the way
        ag = self.check_access('execute', *vpath)
        access_to_write = self.check_access('write', *vpath)
        if not ag:
            # self.goto_login(*vpath, **params)
            # Don't. Just return 403 not allowed if user logged in.
            # Otherwise return 404 not found.
            # TODO for now - just not found
            raise cherrypy.HTTPError(404, _('LC_URL_DOES_NOT_EXIST'))
            #raise cherrypy.HTTPError(404, "page does not exist")
            

        new_url = ''
        # if given url without language, redirect
        # not now
        #if len(vpath) == 0:
        #    new_url = make_redirect_url()
        #    raise cherrypy.HTTPRedirect(new_url)
        #elif vpath[0] not in settings.SUPPORTED_LANGUAGES:
        #    new_url = make_redirect_url()
        #    raise cherrypy.HTTPRedirect(new_url)


        # real path points to a real file, which does exist
        real_path = self.find_real_file(*vpath)

        if real_path is None:
            # okay. path does not exist
            # maybe create a new file?

            # We do not allow to create directories.
            # User may have asked to create it

            # Now we need to check it. So file does not exist, we know it.
            qmark_pos = dwwiki_path.find('?')
            if qmark_pos > 0:
                dwwiki_path_without_params = dwwiki_path[:qmark_pos]
            else:
                dwwiki_path_without_params = dwwiki_path

            # now check for final '/'
            if dwwiki_path_without_params[-1] == '/':
                # this is directory which does not exist
                # throw 404
                raise cherrypy.HTTPError(404, _('LC_URL_DOES_NOT_EXIST'))


            # if we are still here, we have a request to create a file
            # which does not exist
            # here we check access to write. assuming vpath has
            # a non-existent file name, not a directory name, as it's last element
            self.check_access('write', *vpath)
            #if ag:
            if access_to_write:
                # go to report editor
                base = cherrypy.config.get('tools.proxy.base','')
                edit_url = base + cherrypy.request.request_line.split()[1]
                if edit_url.find('?') >= 0:
                    edit_url += '&action=edit'
                else:
                    edit_url += '?action=edit'

                # make up the path
                raise cherrypy.HTTPRedirect(edit_url)
            else:
                raise cherrypy.HTTPError(404, _('LC_URL_DOES_NOT_EXIST'))

        # now real path is not none.
        # Yet, user may have asked for a directory, i.e. index.markdown,
        # but his url does not contain the word 'index'
        # and does not end in slash '/'
        fn = os.path.basename(real_path)
        if (fn == 'index.markdown'):
            base = cherrypy.config.get('tools.proxy.base','')
            full_url = base + cherrypy.request.request_line.split()[1]
            redir = False
            if '?' in full_url:
                if '/?' not in full_url:
                    full_url = full_url.replace('?', '/?')
                    redir = True
            else:
                if full_url[-1] <> '/':
                    full_url += '/'
                    redir = True
            if redir:
                raise cherrypy.HTTPRedirect(full_url)



        # check for download action
        csv_tableid = params.get('csvdownload', None)
        xls_tableid = params.get('xlsdownload', None)

        # check for printable
        action_param = params.get('action', None)

        streamer = self.get_streamer()
        
        if action_param == 'printable':
            return streamer.stream_to_response(real_path, access_to_write, True, *vpath, **params)

        if action_param == 'pdf':
            return streamer.stream_to_pdf(real_path, access_to_write, True, *vpath, **params)

        if csv_tableid is not None:
            return streamer.stream_to_csv_or_xls(real_path, csv_tableid, 'csv', *vpath, **params)
        elif xls_tableid is not None:
            return streamer.stream_to_csv_or_xls(real_path, xls_tableid, 'xls', *vpath, **params)
        else:
            return streamer.stream_to_response(real_path, access_to_write, False, *vpath, **params)


    # here we set this streaming only for mkdown
    mkdown._cp_config = {'response.stream': True}


    #index.exposed = True

    # Error pages
    # ===========


    def error_page_403(status, message, traceback, version):
        
        t = utils.get_report_template('httperror.html')
        base = cherrypy.config.get('tools.proxy.base','')
        url_str = base + cherrypy.request.request_line.split()[1]
        res = t.format(title=_('LC_ERROR'), base=base,error_code=404,error_message=message,url=url_str)
        
        return res

    def error_page_404(status, message, traceback, version):

        t = utils.get_report_template('httperror.html')
        base = cherrypy.config.get('tools.proxy.base','')
        url_str = base + cherrypy.request.request_line.split()[1]
        res = t.format(title=_('LC_ERROR'), base=base,error_code=404,error_message=message,url=url_str)

        return res

    def secureheaders():
        CSP = """default-src='self';
        script-src www.dwworks.ru;
        """

        # allow style
        # style-src 'self';

        headers = cherrypy.response.headers
        headers['X-Frame-Options'] = 'DENY'
        headers['X-XSS-Protection'] = '1; mode=block'
        headers['Content-Security-Policy'] = CSP
    
    cherrypy.config.update({'error_page.403': error_page_403})
    cherrypy.config.update({'error_page.404': error_page_404})

    cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize', secureheaders, priority=60)


    #def start_server():
        

