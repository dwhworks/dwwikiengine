# -*- coding: utf-8 -*-

import psycopg2
import connectionconstants

# PostgreSQL connection utils

# data types mapping
PG_DATA_TYPES = {
    23: 'int',
    25: 'str',
    # unknown
    705: 'str',
    1043: 'str',
    1082: 'date',
    1700: 'Decimal'
}

class DWPostgreSQLConnector():
    def get_con(self, dbparams):
        """ Returns a connection object given
        a dictionary of connection params
        """
        
        timeout = dbparams.get('QUERY_TIMEOUT', connectionconstants.DEFAULT_QUERY_TIMEOUT) * 1000 # milliseconds
        con = psycopg2.connect(
            user=dbparams['USER'],
            password=dbparams['PASSWORD'],
            host=dbparams['HOST'],
            database=dbparams['DB'],
            port=dbparams['PORT'],
            options="-c statement_timeout=%d" % timeout
        )
        con.set_client_encoding('utf-8')
        return con
        


    def dt(self,oid):
        return PG_DATA_TYPES.get(oid, 'unknown')


#    def get_col_info(cur):
#        res = ''
#        columns = cur.description
#        for col in columns:
#            col_name = col[0]
#            # check type. deal in utf-8 for God's sake
#            if type(col_name) is unicode:
#                col_name = col_name.encode('utf-8')
#            res += "name: %s\n" % col_name
#            res += "type_code: %s\n" % dt(col[1])
#            res += "internal_size: %d\n" % col[3]
#            if col[4] is None:
#                precision = 0
#            else:
#                precision = col[4]
#            res += "precision: %d\n" % precision
#            
#            if col[5] is None:
#                scale = 0
#            else:
#                scale = col[5]
#            res += "scale: %d\n" % scale
#
#        return res
        
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

