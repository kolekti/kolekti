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


""" Medias model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''


from lxml import etree as ET

from kolektiserver.models.ProjectModel import ProjectModel

from kolekti.utils.i18n.i18n import tr
#from kolektiserver.models.sql.models import Usecase

class MediasModel(ProjectModel):
    __msg = ""
    __localNS={"kolekti:medias":"kme",
               "kolekti:browser":"ka",
               "kolekti:usersession":"ku",
               "kolekti:viewer":"kv"}
    _KEEPMETA=False

    def __init__(self, *args, **kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(MediasModel,self).__init__(*args,**kwargs)

    def import_file(self, field):
        dest = '/'.join((self.http.path, self.http.params.get('uploaddir', ''), field.filename))
        super(MediasModel, self).putdata(dest, field.file.read())

    def setmessage(self, msg, params={}):
        s = tr(msg, params)
        self.__msg += u"%s\n" %s.i18n(self.http.translation)

    def getResponse(self, field=None):
        if self.http.params.has_key('CKEditor'):
            return u"<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%d, '%s', '');</script>"%(int(self.http.params.get('CKEditorFuncNum', '2')),'%s/%s'%(self.http.path,field.filename))
        else:
            return u"<script type=\"text/javascript\">window.parent.kolekti.notify('browser-refresh', {'url': '%s'}, null);</script>"%'/'.join((self.http.path, self.http.params.get('uploaddir', '')))+self.__msg

    def __is_root_medias(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        return len(splitId) == 4

    ###############################################
    # DAV Methods
    ###############################################

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        if self.__is_root_medias(resid):
            s = tr(u"[0021]Medias")
            p.text = s.i18n(self.http.translation)
        else:
            p.text = resid.split('/')[-1]
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        if self.http.headers.get('Kolektibrowser', '') != 'uploadmedia':
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'uploadmedia'})
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if self.http.headers.get('Kolektibrowser', '') != 'uploadmedia':
            if not self.__is_root_medias(resid):
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
            if self.isCollection(resid):
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newdir'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'previewmedia'})
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaymedia'})
        if self.isCollection(resid) and self.http.headers.get('Kolektibrowser', '') == 'uploadmedia':
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'selectdir'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        return p

    # Medias
    def _prop_kme_usage(self, resid):
        ''' Get module medias usage '''
        p = self._xmlprop('usage','kolekti:medias')
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        medresid=self.abstractIO.normalize_id(resid)
        res = sql.select(Usecase, "ref='%s'" %medresid)
        for r in res:
            mresid = r.resid
            if mresid[len(self.abstractIO.uriprojectpart):].startswith('/modules'):
                murl = self.abstractIO.normalize_id(mresid)
                e = ET.SubElement(p, "{kolekti:medias}module", {'resid': mresid, 'url': murl, 'urlid': self._urihash(murl)})
                modulemodel=self._loadMVCobject_('ModulesModel')
                e.text = modulemodel._prop_dav_displayname(mresid).text
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'baseviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'deleteresource'})
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p
