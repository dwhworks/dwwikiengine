[home](../) /
[docs](./) /
online-editing

Online Editing
==============

Reports may be created and edited in a browser, although
in my humble opinion a proper text editor, like [vim] [1]
is much better. Yet, web editing may be useful at times.

[1]: https://en.wikipedia.org/wiki/Vim_(text_editor)

So, to edit a report online, you must login as a user who has
permissions to edit reports in a certain directory.
The whole permissions system will be explained later.

You may read through comments in a file `fileaccess.conf` in dwwiki
installation directory.

Okay, click "Log in" and log in as admin.

Now you may see "edit" link. By clicking on it you may edit
this page.

Creating New Reports Online
---------------------------

To create a new report, you must first create a link to it
on some other page. When you are logged in as a user who
has permissions to edit reports in the current directory,
and you click on a link that leads to nonexistent page,
you are redirected to the editor to create it.

Try this (you must be logged in as admin):

[new admin report](/users/admin/new-report-1)

The editor is a minimal one, without javascript or WYSIWYG interface.
The editor does not allow you to create new directories.
It does not allow you to create `index.markdown` file in an empty
directory. And it doesn't allow you to delete reports.

The idea behind these limitations is this:

The whole permissions system is based on directory structure.
To create a new directory usually means to set permissions to access it.
The directory tree should be under control of administrators
so as to keep links between pages under control.

When a directory is created by admin, (s)he also creates an `index.markdown`
in it and sets all permissions.

Commonly, all the reports are put under version control (svn, git or whatever you like).
So when a report is created, edited or deleted not through version control
but directly through web editor, it must be added to version control
using some policies set by administrators.

It is much easier for admins to configure all these to their liking
rather than creating a complicated online file system manipulation
application which nobody would like anyway.

You also have ftp, ssh, webdav, windows shared folders and more
to access server directories directly through your operating system
interfaces. We cannot beat these so why bother?

Web report editor is a tool to make quick corrections, not
complicated reports. And honestly, I am thoroughly sick of bloated web interfaces.

Next -> [Connecting to your database](connecting-to-your-database)

-------------------------------------------------------------
[View source](online-editing.markdown)  
[Printable html](?action=printable)
