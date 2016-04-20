[home](../) /
[docs](./) /
user-accounts

User Accounts
===============

User accounts are stored in a separate database:

```<dwwiki_root>/db/service.db
```

which is also a SQLite database. Database access parameters
are specified in `settings.py` file as

<div class="colored-code">
<code>
SERVICE_DB = {
        'ENGINE': 'sqlite',
        'DB': servicedbpath,
        'QUERY_TIMEOUT': 60
        #'HOST': '',
        #'PORT': '',
        #'USER': '',
        #'PASSWORD': ''
}
</code>
</div>

This database is separate from reports databases and isn't
accessible by users unless you allow it.

It contains only one table - `dw_users` with user names, encrypted
passwords and user groups.

For details see files in `db` directory. The script `makefirstusers.py`
creates user accounts and outputs them as sql insert statements.

Password encryption is implemented as md5 encryption. For details
see comments in `makefirstusers.py` and `settings.py`.

The python module which deals with password checking is `dwwiki/usermanager.py`.

You may use this system as is, but move it into your own database,
or you may implement your own, for example using LDAP, Active Directory
or whatever you come up with. In this case `usermanager.py` must be replaced.

A pluggable system of user managers,  much the same as database connectors
is on the short list but it is not yet implemented.

Creating User Accounts Online
-----------------------------

This feature is also under way, but not yet ready.
It definitely should be customizable. Just adding a "Register" page
and storing credentials is not enough.

Administrator must assign groups, give permissions, allocate disk quota,
create OS accounts for ssh access and so on. Making a single model
that fits everyone simply will not do. 

The default module is going to be a bare replaceable minimum.

It's absense, however, isn't a problem
for data warehouses, since administrators commonly create user accounts
with their own hands (or scripts). Yet it must be present for using dwwiki
front end as publicly available online service.

----------------------------------------------------------------------

[View page source](file-access-security.markdown)

        
        