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


""" Modules model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import time

from lxml import etree as ET

from kolektiserver.models.ProjectModel import ProjectModel

from kolekti.logger import dbgexc,debug
from kolekti.utils.i18n.i18n import tr

class PublicationsModel(ProjectModel):
    __localNS={"kolekti:browser":"ka",
               "kolekti:viewer":"kv",
               "kolekti:publication":"kp"}
    _KEEPMETA=False

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(PublicationsModel,self).__init__(*args,**kwargs)

        lang = self.http.params.get('lang', '')
        if lang == '':
            self.publang = self.lang
        else:
            self.publang = lang
        version = self.http.params.get('version', '')
        if version == '':
            self.pubversion = ''
        else:
            self.pubversion = version

    def __is_root_pub(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        return len(splitId) == 4

    def __get_profile_logs(self, resid):
        ''' Get information of last publication for a default lang or first lang dir '''
        # Check if default lang dir exist
        if not self.abstractIO.exists('%s/%s' %(resid,self.publang)):
            # Find first lang dir
            for dir in self.abstractIO.getDir(resid):
                newid = '/'.join((resid, dir))
                if self.abstractIO.isDir(newid):
                    self.publang = dir
                    break

        if self.pubversion == '':
            lpub = self.abstractIO.getDir('%s/%s' %(resid, self.publang))
            lpub.sort(reverse=True)
            version = lpub[0]
        else:
            version = self.pubversion
        return (version, ET.XML(self.abstractIO.getFile('%s/%s/%s/_logs.xml' %(resid,self.publang,version))))

    ###############################################
    # DAV Methods
    ###############################################

    def listCollection(self, resid, ignore_patterns=('_','~','.','.csv')):
        l = super(PublicationsModel, self).listCollection(resid, ignore_patterns)
        l.sort()
        return l

    def isCollection(self, resid):
        if super(PublicationsModel,self).isCollection(resid):
            return not self.__isprofile(resid)
        return False

    def getResource(self,resid):
        if not self.__isprofile(resid):
            return super(PublicationsModel,self).getResource(resid)
        mf=ET.XML(self.abstractIO.getFile(resid+'/'+'__manifest.xml'))
        (version, log)=self.__get_profile_logs(resid)
        publog=mf.xpath("/manifest/publication[@time='%s']" %version)[0]
        self.http.setdata('publication','infos',publog)
        self.http.setdata('publication','lang',self.publang)
        self.http.setdata('publication','logs',log)
        return ('foo','text/html','')

    def isResource(self, resid):
        debug("isresource "+resid+" "+str(not self.isCollection(resid)))
        if not super(PublicationsModel,self).isResource(resid):
            return self.__isprofile(resid)
        return True

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        if self.__is_root_pub(resid):
            s = tr(u"[0025]Publications")
            p.text = s.i18n(self.http.translation)
        else:
            fname = resid.split('/')[-1]
            p.text = fname
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if not self.__is_root_pub(resid):
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaypublication'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        if self.__isprofile(resid):
            ET.SubElement(p, '{kolekti:browser}icon', attrib={'src':'icon_view'})
        return p

    def _prop_ka_isprofile(self, resid):
        ''' Define if resid is profile dir property '''
        p = self._xmlprop('isprofile','kolekti:browser')
        if self.__isprofile(resid):
            p.text = "yes"
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'publicationviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p

#### specific properties

    def _prop_kp_languages(self,resid):
        """ ordered list of publications lang """
        p = self._xmlprop('languages', 'kolekti:publication')
        try:
            if self.__isprofile(resid):
                l = super(PublicationsModel, self).listCollection(resid)
                l.sort(reverse=True)
                for v in l:
                    ET.SubElement(p,"{kolekti:publication}lang",{'dir':v})
        except:
            dbgexc()
        return p

    def _prop_kp_versions(self,resid):
        """ordered list of publications for a given profile, with formatted date & time"""
        p = self._xmlprop('versions', 'kolekti:publication')
        try:
            if self.__isprofile(resid):
                l = super(PublicationsModel, self).listCollection('%s/%s' %(resid, self.publang))
                l.sort(reverse=True)
                for v in l:
                    ET.SubElement(p,"{kolekti:publication}version",{'time':v})
        except:
            dbgexc()
        return p

    def _prop_kp_pivname(self, resid):
        ''' Get pivot file '''
        p = self._xmlprop('pivname', 'kolekti:publication')
        try:
            l=[f for f in self.abstractIO.getDir(resid) if f.split('.')[-1] == "xml"]
            l.remove(u'pivot-variables.xml')
            l.remove(u'pivot-filtered.xml')
            l.remove(u'_logs.xml')
            try:
                l.remove(u'pivot-assembly.xml')
            except ValueError:
                pass
            try:
                l.remove(u'content.xml')
            except ValueError:
                pass
            p.text = l[0]
        except:
            pass
        return p

    def __isprofile(self, resid):
        ''' Define if resid is profile dir '''
        return self.abstractIO.exists(resid+'/__manifest.xml')
