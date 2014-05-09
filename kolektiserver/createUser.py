#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
    Create a new user for kolekti 0.6
    Set a new user in DB
"""

import traceback
import hashlib
import os

from optparse import OptionParser


class KolektiUpdate():
    def __init__(self, user=None, is_admin=False, is_translator=False):
        print '--- Start ---'
        self.user = user
        self.is_admin = is_admin
        self.is_translator = is_translator
        try:
            self.sqlDBbackend = SQLAlchemyBackend()
            self.sqlDBbackend.connect()
            self.sqlDBbackend.create_tables()
            self.create_user()
        except:
            print 'ERROR: %s' %traceback.format_exc()
        print '--- Finish ---'

    def create_user(self):
        ''' Create new user '''
        (l,p,fname,lname,e,org) = self.user
        passhash = self.__encode_password(p)
        newuser = Users(l,passhash,fname,lname,e,org, True, self.is_admin, self.is_translator)

        try:
            self.sqlDBbackend.insert(newuser)
            print 'INFO: User login %s has been add' %l
        except:
            self.sqlDBbackend.rollback()
            print 'ERROR: User login %s already exist' %l

    def __encode_password(self, password):
        sha256 = hashlib.sha256()
        sha256.update(password)
        return sha256.hexdigest()

if __name__ == '__main__':
    usage = "usage: %prog -u login password firstname lastname email organization [-a -t]"
    parser = OptionParser(usage)
    parser.add_option("-u", "--user", help="User informations",
                      dest="user", default=None, action="store", nargs=6)
    parser.add_option("-a", "--admin", help="User is admin",
                      dest="admin", default=False, action="store_true")
    parser.add_option("-t", "--translator", help="User is translator",
                      dest="translator", default=False, action="store_true")

    (options, args) = parser.parse_args()
    if not options.user:
        parser.error("Missing options: user are mandatory")

    # defined environ param if not defined
    if not os.environ.has_key('KOLEKTI_APPDIR'):
        os.environ['KOLEKTI_APPDIR'] = os.getcwd()
    if not os.environ.has_key('KOLEKTI_APP'):
        os.environ['KOLEKTI_APP'] = 'kolektiserver'

    from kolekti.utils.backends.sqlalchemybackend import SQLAlchemyBackend
    from kolektiserver.kolekticonf import conf
    # here the import should be changed
    from kolekti.mvc.models.sql.fmk_db_models import Users

    kUpdate = KolektiUpdate(user=options.user,is_admin=options.admin,is_translator=options.translator)
