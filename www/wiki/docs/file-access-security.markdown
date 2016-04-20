[home](../) /
[docs](./) /
file-access-security

File Access Security
====================

Permissions to access reports in `wiki` directory are set in
`fileaccess.conf` file in root dwwiki installation directory.

The placement of this file does not matter, it is specified
in `settings.py`. Look at comments in `fileaccess.conf`.

Basically, access permissions are copied from Linux filesystem.

`fileaccess.conf` has a structure similar to windows ini files.

Each group enclosed in square brackets represents a directory:

<div class="colored-code">
<code>
[/]
execute=public
read=public
write=dev
</code>
</div>

`execute` means permission to view files in a directory as html or
pdf or Excel, in short - execute reports.

`read` means permission to view reports source code (markdown).

`write` means permission to open report in online editor and save it.

`public` and `dev` are user groups. User names are also allowed here.

## Special User Groups ##

There are two special user groups:

1. `public` means not logged in users.
2. `other` means all logged in user belonging to other groups not specifically mentioned.
   This means the same as UNIX file permissions "other" means.


## Non-web Security ##

If you grant someone permission to access a certain file over FTP or ssh,
`fileaccess.conf` obviously will not prevent it.

I decided not to make the whole system too complicated. I could have stored
file permissions in a database or in a LDAP catalog. Maybe for certain
installations it would have been better. If so, consider making your own
security module and use it instead of `dwwiki/securityguard.py` which
is used by default. For most common situations this system is adequate.

Next -> [User Accounts](user-accounts)

----------------------------------------------------------------------

[View page source](file-access-security.markdown)

        
        