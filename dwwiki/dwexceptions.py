#!/usr/bin/python
# -*- coding: utf-8 -*-

# Exception classes. Used primarily by database connection handlers


# our common exception class
class DwException(Exception):
    # common exception properties
    # our_message - our own error message
    # source_error - first exception, if we re-raise some other exception
    # db_name - database name from settings 
    def __init__(self, db_name, our_message, source_error=None):
        self.db_name = db_name
        self.our_message = our_message
        self.source_error = source_error
        Exception.__init__(self, our_message)

