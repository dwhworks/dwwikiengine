#!/usr/bin/python

""" Create a sql file with statements to insert dwwiki users
Outputs sql statements to stdout.
"""

import hashlib
import sys

SQL_INSERT = """insert into dw_users(dw_username,dw_password,dw_groups,show_public_directory)
values ('{name}','{pwd}','{groups}',{show_public_dir});
"""

# This is used as a primitive salt to add to user password
# The whole password is created by md5-hashing of
# concatenation of username, PWD_SALT and password. In this order.
# The same algorithm is used in dwwiki engine to check for passwords.
# If you change PWD_SALT, you must also change it in settings.py
PWD_SALT = 'blackdog'


def hashit(s):
    """ Hash the password
    """
    hash_object = hashlib.md5(s)
    return hash_object.hexdigest()


def pu(name, pwd, groups, show_public_dir=0):
    """ Put user. Output users to stdout
    name: user name
    pwd: user password in plain text
    groups: groups the user is in, concatenated by comma
    show_public_dir: 0 or 1 - to show user public directory to
        well, public, or not. This parameter does not matter really,
        It is only an extension, so to say, to show all public
        folders, if needed in a dwwiki page.
    """
    hashed_pwd = hashit(name + PWD_SALT + pwd)
    out_sql = SQL_INSERT.format(
        name=name,
        pwd=hashed_pwd,
        groups=groups,
        show_public_dir=show_public_dir
    )
    sys.stdout.write(out_sql)



pu('demo', 'demo', 'dwusers',1)
pu('admin' , 'admin', 'dev,dwusers',1)

