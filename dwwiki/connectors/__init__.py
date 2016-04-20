VERSION = '1.0.0'

# a dictionary of all connectors,
# To use one, you must register it first
# with the dictionary

# global, so to say, dictionary of database connectors
_connectors = {}

# add a new database engine connector
def add_engine(name, engine):
    _connectors[name] = engine

# finds a connector object registered in connectors dictionary
# gets an actual database connection and returns it.
# Throws any exception that may occur in the process
def get_connection(dbparams):
    connector = _connectors[dbparams['ENGINE']]
    con = connector.get_con(dbparams)
    return con


def get_connector(dbparams):
    """ Get the connector object itself
    """
    connector = _connectors[dbparams['ENGINE']]
    return connector

