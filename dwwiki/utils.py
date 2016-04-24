#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import htmlconstants
import settings
import codecs
import urllib
import re

# commonly used routines


def find_real_file(*vpath):
    """ Finds real file from http path
    returns path to a real file or None if it's not found.
    Accounts for lang
    """
    final_path = None
    # Extract the path
    # TODO what self ????
    real_path = self.reports_dir() # this should exist
    lang_path = real_path
    if len(vpath) > 0:
        for el in vpath:
            # try for language
            if el in settings.SUPPORTED_LANGUAGES:
                lang_path = os.path.join(lang_path, el)
            else:
                real_path = os.path.join(real_path, el)
                lang_path = os.path.join(lang_path, el)

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

def make_page_menu(langs=True, edit=False, add_login_link=True):
    """ Makes a menu for the page with user, log out and language
    Returns it as string
    langs - add en | ru | cn link
    No edit link
    """
    
    base = cherrypy.config.get('tools.proxy.base','')
    user = cherrypy.session.get('user', '')

    if edit is True:
        edit_url=base + cherrypy.request.request_line.split()[1]
        if edit_url.find('?') >= 0:
            edit_url += '&action=edit'
        else:
            edit_url += '?action=edit'
        edit_str=_('LC_EDIT')
    
    # This is our path starting after base. Starts with '/'
    # like /en/lalala
    temp_path = cherrypy.request.request_line.split()[1]
    # What we need is make full url 
    path_lang = temp_path[1:3]
    #default_lang = settings.DEFAULT_LANGUAGE
    lang_list = list()
    
    # make up (en|ru) link
    whole_link = ''
#    if langs:
#        if len(settings.SUPPORTED_LANGUAGES) > 1:
#            for el in settings.SUPPORTED_LANGUAGES:
#                if path_lang == el:
#                    # no link
#                    link = '&nbsp;' + el + '&nbsp;'
#                    lang_list.append(link)
#                else:
#                    # link
#                    link = '&nbsp;<a href="' + base + '/' + \
#                                  el + temp_path[:3] + \
#                                  '">' + el + '</a>&nbsp;'
#                    lang_list.append(link)
#
#            whole_link = '(' + '|'.join(lang_list) + ')'
#        else:
#            whole_link = ''
        
    if user == '':
        # show login
        #logout_url = base + '/' + path_lang + '/login'
        logout_url = base + '/login'
        get_params = cherrypy.request.request_line.split()[1]
        #print get_params
        target = cherrypy.request.request_line.split()[1]
        logout_url = logout_url + '?target=' + urllib.quote(target)
        login_logout = _('LC_LOG_IN')
    else:
        #logout_url = base + '/' + path_lang + '/logout'
        logout_url = base + '/logout'
        login_logout = _('LC_LOG_OUT')
        

    if edit is True:
        yield_str = htmlconstants.PAGE_SUB_HEADER.format(user=user, logout_url=logout_url,
                                                edit_url=edit_url,
                                                edit_str=edit_str,
                                                login_logout=login_logout,
                                                en_ru_link=whole_link)
    else:
        yield_str = htmlconstants.PAGE_SUB_HEADER_EDITOR.format(user=user, logout_url=logout_url,
                                                login_logout=login_logout,
                                                en_ru_link=whole_link)

    return yield_str


def get_current_lang():
    """ Returns current lang based on url
    """
    pass

def make_topmost_menu():
    """ makes a topmost div based on settings
    Returns it as a string
    """
    pass
    

def get_report_template(template_name, *vpath):
    """ reads report template from file and returns it as string
    in utf-8. vpath is a cherrypy vpath
    """ 
    templates_dir = cherrypy.config['dwwiki.htmltemplatesdir']
    #if len(vpath) > 0:
        # that's ru or en
    #    templates_dir = templates_dir + '/' + vpath[0]
    template_file = templates_dir + '/' + template_name
    input_file = codecs.open(template_file, 'r', encoding='utf-8')
    res = input_file.read()
    input_file.close()
    return res.encode('utf-8')

def common_error_page(error_code, error_message):
    t = utils.get_report_template('httperror')
    base = cherrypy.config.get('tools.proxy.base','')
    url_str = base + cherrypy.request.request_line.split()[1]
    res = t.format(base=base,error_code=error_code,error_message=error_message,url=url_str)
    return res


def get_report_header(*vpath):
    return get_report_template('reportheader.html', *vpath)

def get_report_footer(*vpath):
    return get_report_template('reportfooter.html', *vpath)

def get_printable_report_header(*vpath):
    return get_report_template('reportheader-printable.html', *vpath)

def get_printable_report_footer(*vpath):
    return get_report_template('reportfooter-printable.html', *vpath)


def try_to_make_number(val, default_value):
    """ Tries to make a number out of string. returns as decimal, float or int
    if val is already one of these, returns it.
    if there was no luck, returns 0 as float
    """
    result = default_value

    #print val

    FIELD_TYPES_AGGREGATION = ['Decimal', 'int', 'long', 'float']
    FIELD_TYPES_STRING = ['str', 'unicode']
    tp = type(val).__name__

    if tp in FIELD_TYPES_AGGREGATION:
        result = val
    elif tp in FIELD_TYPES_STRING:
        # convert to unicode
        if tp == 'str':
            str_val = val.decode('utf-8')
        # remove {: xxx} cell attributes
        ATTR_RE = re.compile('\{: *([ [a-z]+=\".+\" *]*)\}')
        str_val = re.sub(ATTR_RE, '', str_val)

        # remove blanks
        str_val = str_val.strip()

        # remove thousand separators
        str_val = str_val.replace(',', '')

        try:
            result = float(str_val)
        except Exception, e:
            result = default_value
    
    return result

