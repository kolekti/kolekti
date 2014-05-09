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


"""controller for administration"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.logger import dbgexc

from kolektiserver.controllers.AdminController import AdminController
from kolekti.kolekticonf import conf

class AccountController(AdminController):

    def ctrGET(self):
        try:
            self._setdata('kolekti', 'user', self.model.get_user(self.http.userId))
        except:
            pass
        self.view.format_collection()

    def ctrPOST(self):
        error=False
        if self.http.path.startswith('/user/account'):
            try:
                locale = self._get_firstparam('locale')
                if locale == '':
                    locale = conf.get('locale_default')

                self.model.update_infos_user(self.http.userId,
                                             u'',
                                             self._get_firstparam('firstname'),
                                             self._get_firstparam('lastname'),
                                             self._get_firstparam('email'),
                                             self._get_firstparam('organization'),
                                             locale,
                                             self._get_firstparam('timezone'),
                                             "admin" in self._getdata('auth','clearances'),
                                             "translator" in self._getdata('auth','clearances'))
                self._setdata('user', 'locale', locale)
            except:
                dbgexc()
                error=True
                self._setdata('status', 'error', self._setmessage(u"[0001]Erreur lors de l'enregistrement"))

        if self.http.path.startswith('/user/ident'):
            passw = self._get_firstparam('pass')
            passw2 = self._get_firstparam('pass2')
            if passw == '' or passw != passw2:
                error=True
                self._setdata('status', 'error', self._setmessage(u"[0002]Les mots de passe ne correspondent pas"))
            else:
                try:
                    self.model.update_password(self.http.userId, passw)
                except:
                    dbgexc()
                    error=True
                    self._setdata('status', 'error', self._setmessage(u"[0003]Erreur lors du changement de mot de passe"))
        if self.http.path.startswith('/user/extsrc'):
            srcid=self._get_firstparam('extsrcid')
            con=self._get_firstparam('extsrccon')
            url=self._get_firstparam('extsrcurl')
            user=self._get_firstparam('extsrclog')
            passw=self._get_firstparam('extsrcpass')
            delsrc=False
            if srcid=='0':
                srcid=self._get_firstparam('extsrcnewid')
            else:
                delsrc=(self._get_firstparam('extsrcdelete')=='yes')
            if delsrc:
                self.model.delete('/user/extsrc/%s'%srcid)
            else:
                self.model.put('/user/extsrc/%s'%(srcid,con,url,user,passw))

        if not error:
            self._setdata('status', 'ok', '')

        self.ctrGET()
        
