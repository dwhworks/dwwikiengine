#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import ConfigParser
import settings
from usermanager import UserManager

class SecurityGuard(object):
    """Handles access to any markdown url
    """
    def __init__(self, access_list, user_manager):
        """ accesslist - filename with file and dir permissions
        userlist - filename with user groups
        """

        self.accesslist = ConfigParser.ConfigParser()
        self.accesslist.read(access_list)

        self.user_manager = user_manager

    def get_user_data(self, user):
        """ returns a user data dictionary or none
        """
        res = self.user_manager.get_user_data(user)
        return res

    def request_access(self, user, action, *vpath):
        """Newfangled access.
        Returns True if access is granted, False otherwise
        """
        # constants for get_access
        ACCESS_GRANTED = 'ACCESS_GRANTED'
        ACCESS_DENIED = 'ACCESS_DENIED'
        ACCESS_NODATA = 'ACCESS_NODATA'
        
        # this is called for each element in path
        def get_access(groups, section_name, action):
            """ Tests a section. Returns one of ACCESS_XXX constants
                user is a string - user
                groups is an array or list of user groups
                section_name - like '/finance/'
                action - 'execute', 'read' or 'write'
            """
            result = ACCESS_NODATA
            if self.accesslist.has_section(section_name):
                # find one of 'execute', 'read' and 'write'
                if self.accesslist.has_option(section_name, action):
                    # read the list of groups mentioned for this action
                    # like execute=dev,others,public,user1
                    access_groups_str = self.accesslist.get(section_name, action).strip()
                    access_groups_list = access_groups_str.split(',')
                    result = ACCESS_DENIED
                    # Now simply find if any element from groups is
                    # contained in access_groups_list
                    for group in groups:
                        for access_group in access_groups_list:
                            if group.strip() == access_group.strip():
                                result = ACCESS_GRANTED
                                break
                        if result == ACCESS_GRANTED:
                            break

            return result
        
        # --- main body ---

        result = False
        user_data = self.get_user_data(user)

        # establish user groups. A list of groups will contain
        # a user name itself, 'others' and 'public'
        groups = []
        if user <> '':
            if user_data is None:
                # unlikely though
                return result    

            groups = user_data['groups'].split(',')
#            # user name is given, i.e. the user is logged in.
#            # so we find a list of groups the user is in
#            if self.userlist.has_option('usergroups', user):
#                strgroups = self.userlist.get('usergroups', user)
#                # list of groups the user is assigned to
#                groups = strgroups.split(',')
#            else:
#                # username was passed in but it is invalid. Return False immediately
#                #print 'user ' + user + ' was not found'
#                result = False
#                return result

            # Now here we are. The user name was given, it is found in
            # some user list along with groups.
            # we also include a group 'other'
            groups.append('others')
            groups.append('public')
            # and append the user name itself
            groups.append(user)
        else:
            # the user is not logged in. He is public
            groups.append('public')

        # now we have a proper list for testing in groups list variable,
        # including the user name, others and public as needs be
        #print "--- List of groups to test ---"
        #print groups

        # traverse directories top-down.
        section_name = '/'
        test_result = get_access(groups, section_name, action)
        
        # try to narrow down. maybe access is granted lower in the tree
        # or on the contrary - access is revoked
        # if access is granted or denied somewhere, and then there is no data,
        # access remains as it were previously
        if len(vpath) > 0:
            slash = ''
            for el in vpath:
                if el not in settings.SUPPORTED_LANGUAGES:
                    section_name += slash + el
                    slash = '/'
                    #print "--- testing section ---"
                    #print section_name
                    new_result = get_access(groups, section_name, action)
                    #print new_result
                    if new_result <> ACCESS_NODATA:
                        test_result = new_result

        
        result = (test_result == ACCESS_GRANTED)
        return result


