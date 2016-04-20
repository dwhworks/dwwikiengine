# -*- coding: utf-8 -*-

import mysql.connector
import connectionconstants

# data types mapping
MYSQL_DATA_TYPES = {
    23: 'int',
    25: 'str',
    # unknown
    705: 'str',
    1043: 'str',
    1082: 'date',
    1700: 'Decimal'
}

class DWMySqlConnector():
    def get_con(self, dbparams):
        timeout = dbparams.get('QUERY_TIMEOUT', connectionconstants.DEFAULT_QUERY_TIMEOUT) * 1000 # milliseconds
        con = mysql.connector.connect(
            user=dbparams['USER'],
            passwd=dbparams['PASSWORD'],
            host=dbparams['HOST'],
            database=dbparams['DB'],
            connection_timeout=timeout
        )
        return con

    def dt(self,oid):
        return SQLITE_DATA_TYPES.get(oid, 'unknown')

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

