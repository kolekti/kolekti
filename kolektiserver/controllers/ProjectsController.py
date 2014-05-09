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



"""controller for modules"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.exceptions import exceptions as EXC
from kolekti.mvc.MVCFactory import MatchRejected
from kolekti.mvc.controllers.Controller import Controller

from lxml import etree as ET

class ProjectsController(Controller):

    # routing matchers
    def _matcher_resid(self,http,match):
        try:
            resid=http.getdata('kolekti','resid')
            if not match.search(resid):
                raise MatchRejected
            if http.params.get('upload', '0') == '1':
                return
        except AttributeError:
            raise MatchRejected

    def __init__(self,*args,**kwargs):
        """registers project informations into http object"""
        super(ProjectsController,self).__init__(*args,**kwargs)
        self.project = {}
        try:
            self.project = self.model.project
            self._setdata('kolekti','project',self.project)
            resid='@' + '/'.join(self.http.path.split('/')[3:])
            self._setdata('kolekti','resid',resid)
        except:
            pass

    def ctrALL(self):
        if not self.model.checkProjectAccess(self.project.get('directory', '')):
            raise EXC.Forbidden

    def ctrGET(self):
        if not self.model.checkProjectAccess(self.project.get('directory', '')):
            raise EXC.Forbidden
            
        resid = self.http.getdata('kolekti','resid')
        if resid == '@':
            self._setdata('kolekti','orders',self.model.list_orders())
            
            model=self._loadMVCobject_('ModulesModel')
            histo = model.getpropval(u'@modules', 'history', 'kolekti')
            if not histo is None:
                self._setdata('kolekti','loglistmodules',histo.find('listfiles'))

            model=self._loadMVCobject_('TramesModel')
            histo = model.getpropval(u'@trames', 'history', 'kolekti')
            if not histo is None:
                self._setdata('kolekti','loglisttrames',histo.find('listfiles'))

            model=self._loadMVCobject_('ConfigurationModel')
            histo =model.getpropval(u'@configuration/orders', 'history', 'kolekti')
            if not histo is None:
                self._setdata('kolekti','loglistlaunchers',histo.find('listfiles'))

            model=self._loadMVCobject_('PublishModel')
            histo =model.getpropval(u'@configuration/orders', 'history', 'kolekti')
            if not histo is None:
                self._setdata('kolekti','loglistorders',histo.find('listfiles'))

        if resid == '@translate':
            # Display log of masters publish
            model=self._loadMVCobject_('MastersModel')
            histo =model.getpropval(u'@masters', 'history', 'kolekti')
            if not histo is None:
                self._setdata('kolekti','loglistmasters',histo.find('listfiles'))
