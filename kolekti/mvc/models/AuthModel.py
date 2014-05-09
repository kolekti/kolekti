# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
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

""" model : User Authentification class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import os


from kolekti.exceptions import exceptions as EXC
from kolekti.kolekticonf import conf
#from kolekti.mvc.models.sql.models import Users

from kolekti.mvc.models.Model import Model
from kolekti.mvc.models.PassUtils import PassUtils

class AuthModel(Model, PassUtils):
    authfile=os.path.join(conf.get('appdir'),'config','passwd')

    def authenticate(self, login, password):
        """ checks the auth of a user

        login : login of the user
        password : pass of the user

        if the authentication is successful, return the uid, else raise 401 exception
        """
        passhash = self._encode_password(password)
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "login='%s' and password='%s'" %(login, passhash))
        if user == []:
            raise EXC.AuthError
        else:
            return user[0].id

    def user(self, uid):
        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            user = sql.select(Users, "id='%d'" %uid)
            return user[0]
        except:
            return None

    def lang(self, uid):
        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            user = sql.select(Users, "id='%d'" %uid)
            return user[0].lang
        except:
            return 'fr'

    def timezone(self, uid):
        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            user = sql.select(Users, "id='%d'" %uid)
            return user[0].timezone
        except:
            return 1

    def is_admin(self, uid):
        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            user = sql.select(Users, "id='%d'" %uid)
            return user[0].is_admin
        except:
            return False

    def is_translator(self, uid):
        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            user = sql.select(Users, "id='%d'" %uid)
            return user[0].is_translator
        except:
            return False
