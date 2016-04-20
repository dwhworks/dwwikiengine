#!/usr/bin/python
# -*- coding: utf-8 -*-

# Database settings
# These are real connections, meaning, not aliases

import os
import sys

serverpath = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))

# main database
dbpath = os.path.join(serverpath, 'db', 'examples.db')

# service database for storing users
servicedbpath = os.path.join(serverpath, 'db', 'service.db')

# path to access permissions file
accessfile = os.path.join(serverpath, 'fileaccess.conf')

# These are databases to use as report sources.
# installed database connectors: mysql, postgresql, sqlite, oracle
# connector type goes into ENGINE parameter
# see how dwwiki.connectors are designed. They are really trivial.
# You can make your own in no time.
DATABASES = {
    # this is a database name as referred to
    # further in database aliases
    # actual database used in examples
    'dwh': {
        'ENGINE': 'sqlite',
        'DB': dbpath,
        # limits rows only in html output
        'LIMIT_ROWS': 500,
        # max timeout in seconds, after which the query will be terminated
        'QUERY_TIMEOUT': 60
    },
    # these are just examples, not actual databases
    'dwh_mysql': {
        'ENGINE': 'mysql',
        'HOST': 'localhost',
        'PORT': '3306',
        'DB': 'library',
        'USER': 'librarian',
        'PASSWORD': 'libpassword',
        'LIMIT_ROWS': 250,
        'QUERY_TIMEOUT': 2 # these are whole seconds
    },
    'dwh_postgres': {
        'ENGINE': 'postgresql',
        'HOST': 'localhost',
        'PORT': '5432',
        'DB': 'dwh_test',
        'USER': 'dwhuser',
        'PASSWORD': '54321',
        # limits rows only in html output
        'LIMIT_ROWS': 500,
        'QUERY_TIMEOUT': 60
    }
}

# This dictionary shows what actual connections are used
# when user makes a connection through for example, dwh alias.
# Each alias is mapped with groups and connections used by these groups
# When connecting we are looking for a user's primary group
# if there is no connection for a particular group, an error should be raised
DATABASE_ALIASES_FOR_GROUPS = {
    'dwh': {
        # group = database from DATABASES
        'dev': 'dwh',
        'users': 'dwh',
        'default': 'dwh'
    },
    'service': {
        # this one will not connect, it's an example
        'dev': 'service',
        'users': 'service',
        'default': 'service'
    }
}

# db to store user information, passwords, emails etc...
# it is not used for user queries, and is not accessible for users.
# if you need to give user access to it, make an entry
# in DATABASES for it.
SERVICE_DB = {
        'ENGINE': 'sqlite',
        'DB': servicedbpath,
        'QUERY_TIMEOUT': 60
        #'HOST': '',
        #'PORT': '',
        #'USER': '',
        #'PASSWORD': ''
}

# password salt used to md5-encrypt user passwords
# passwords are encrypted as md5(username + salt + password)
# the algorithm may be changed. see dwwiki.usermanager.py
PWD_SALT = 'blackdog'

# access permissions file
ACCESS_FILE = accessfile


# Default database string which is assumed when nothing is set in query parameters
# This points to an item in DATABASE_ALIASES_FOR_GROUPS
DATABASE_DEFAULT_ALIAS = 'dwh'

# Formats for csv file downloads
CSV_DOWNLOAD_FORMAT = {
    'en': {
        'DATE_FORMAT': '%Y-%m-%d',
        'FIELD_SEPARATOR': ';',
        # either None or '\n' or <br/> or whatever you like - not "\n" mind you.
        # It will literally replace a newline character in a string
        # if None, newlines will be retained and the whole string will be enclosed
        # in double quotes
        'NEWLINE_REPLACEMENT': '\n',
        'TAB_REPLACEMENT': '\t',
        'ENCODING': 'utf8',
        'NEWLINE': "\n"
    }
}

# Supported languages
#
# In URLs language goes before any directory. Like this:
# http://dwworks.ru/dwwiki/en/path/to/report
# In which case http://dwworks.ru is served by apache,
# then /dwwiki is where our server starts to serve pages from
# then /en or /ru is a language the user wants to see system messages in.
# This language mark does not define the language of a report itself.
# It depends on each report.
SUPPORTED_LANGUAGES = ['en']

# When language mark is not used in URL, assume this language
# by default TODO unless the user chooses another language in his settings
DEFAULT_LANGUAGE = 'en'

# This is displayed as a "root" folder, when generating
# the folder structure for newly created pages
# Like so:
# home / dwh / test
# language is always English here, for it copies the url structure
ROOT_DIRECTORY_TITLE = 'dwwiki'

