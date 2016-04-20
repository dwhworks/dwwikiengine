#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings

# Base streamer class for handling markdown extensions

class BaseDwStreamer(object):
    # On construction we expect a database configuration
    #def __init__(self):

    # process a block that was found in markdown
    # block_text - block as is
    # the function yields it's results as it pleases, e.g. line by line.
    # user - which user asked to do the processing
    # block_id - sequential block number on page
    #            used for csv downloads fo example
    # params - what was received from http request or whatever else
    def process_block(block_text, user, block_id, **params):
        pass

    def get_tagname(self):
        """Should return tag name which the parser understands
        E.g. sqltable for {sqltable} tag"""
        return None

    def factory(self):
        """Return a new instance of object. It is needed
        to dynamically pass streamer classes to dw engine.
        The engine must create a new instance for every request,
        for thread safety. Descendants override this method.
        """
        pass
