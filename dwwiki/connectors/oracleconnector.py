# -*- coding: utf-8 -*-

import cx_Oracle
import connectionconstants

# Oracle connection utils

# data types mapping
ORACLE_DATA_TYPES = {
    23: 'int',
    25: 'str',
    # unknown
    705: 'str',
    1043: 'str',
    1082: 'date',
    1700: 'Decimal'
}

class DWOracleConnector():
    def get_con(self, dbparams):
        """ Returns a connection object given
        a dictionary of connection params
        """
        
        timeout = dbparams.get('QUERY_TIMEOUT', connectionconstants.DEFAULT_QUERY_TIMEOUT) * 1000 # milliseconds
        con = cx_Oracle.connect(
            user=dbparams['USER'],
            password=dbparams['PASSWORD'],
            dsn=dbparams['DSN']
            #database=dbparams['DB'],
            #port=dbparams['PORT'],
            #options="-c statement_timeout=%d" % timeout
        )
        #con.set_client_encoding('utf-8')
        return con
        

    # routines used to determine field type out of
    # cursor description. Needed as 

    def dt(self,oid):
        return ORACLE_DATA_TYPES.get(oid, 'unknown')

    def get_col_type(self,col):
        return self.dt(col[1])

    def get_precision(self,col):
        if col[4] is None:
            precision = 0
        else:
            precision = col[4]
        return precision

    def get_scale(self,col):
        if col[5] is None:
            scale = 0
        else:
            scale = col[5]
        return scale

