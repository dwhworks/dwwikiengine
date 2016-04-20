# -*- coding: utf-8 -*-


import hashlib

class UserManager(object):
    """ User manager.

    Checks user passwords
    """

    def __init__(self, servicedb, salt):
        # try to establish a connection
        self.db = servicedb
        self.salt = salt

    def get_connection(self):
        """Gets and returns a database connection. Or exception.
        """
        res = None
        if self.db['ENGINE'] == 'postgresql':
            import psycopg2
            res = psycopg2.connect(
                    user=self.db['USER'],
                    password=self.db['PASSWORD'],
                    host=self.db['HOST'],
                    database=self.db['DB'],
                    port=self.db['PORT'])
            res.set_client_encoding('utf-8')
        elif self.db['ENGINE'] == 'sqlite':
            import sqlite3
            timeout = self.db.get('QUERY_TIMEOUT', 60) * 1000 # milliseconds
            res = sqlite3.connect(
                database=self.db['DB'],
                timeout=timeout
            )
        return res
            

    def get_user_data(self, user):
        """Returns a dictionary of user data if one is found. Or None
        username
        password - hashed
        groups
        """
        res = None
        # TODO postgresql uses %s instead of ? as parameters
        #sql = "select dw_password, dw_groups from dw_users where dw_username = '{username}';".format(username=user)
        sql = "select dw_password, dw_groups from dw_users where dw_username = ?;"
        con = self.get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (user,))
            #cur.execute(sql)
            row = cur.fetchone()
            if row is not None:
                res = {'username': user, 'password': row[0], 'groups': row[1]}
        finally:
            if con is not None:
                con.close()
            return res
        
    def check_password(self,user_data, clear_password):
        """Checks a clear text password against a hashed one
        stored in user_data dict. Returns true or false
        """
        res = False
        if user_data is not None:
            username = user_data['username']
            stored_hash = user_data['password']
            salted_string = username + self.salt + clear_password
            print salted_string
            hash_object = hashlib.md5(salted_string)
            hash_for_check = hash_object.hexdigest()
            if hash_for_check == stored_hash:
                res = True
        return res

