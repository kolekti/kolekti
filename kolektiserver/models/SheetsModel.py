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




""" Sheets model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os

from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolektiserver.models.ProjectModel import ProjectModel

from kolekti.logger import debug
from kolekti.utils.i18n.i18n import tr

class SheetsModel(ProjectModel):
    __localNS={"kolekti:browser":"ka",
               "kolekti:usersession":"ku",
               "kolekti:viewer":"kv"}
    _KEEPMETA=False
    __msg = ''

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(SheetsModel,self).__init__(*args,**kwargs)

    def put(self, id):
        ''' Override default put method '''
        if self.http.params.get('refreshsheets', '') == '1':
            debug('regenerate sheets')
            filename = id.split('/')[-1][:-4]
            ods_resid="/".join(('@'+conf.get('dirSHEETS'), 'sources','%s.ods'%filename))
            xml_resid="/".join(('@'+conf.get('dirSHEETS'), 'xml','%s.xml'%filename))
            self.genVarFile(ods_resid, xml_resid, 'ods')
        else:
            super(SheetsModel,self).put(id)
            #super(SheetsModel,self).log_save(id)

    def __is_root_sheets(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        return len(splitId) == 4

    def genVarFile(self,odsid,xmlid,ftype,filter="export-variables"):
        # genere le fichier de textes automatiques à partir du openoffice
        foff = self.abstractIO.getpath(odsid)
        debug ('gen variables file')
        xslt_doc1=ET.parse(os.path.join(conf.get('appdir'),'publication','xsl','oofilters','%s-%s-pass1.xsl'%(filter,ftype)))
        xslt1=ET.XSLT(xslt_doc1)
        xslt_doc2=ET.parse(os.path.join(conf.get('appdir'),'publication','xsl','oofilters','%s-pass2.xsl'%(filter)))
        xslt2=ET.XSLT(xslt_doc2)

        zip = self._loadMVCobject_('ZipFileIO')
        zip.open(foff, 'r')
        foffx=zip.read('content.xml')
        zip.close()

        vx=xslt1(ET.ElementTree(ET.XML(foffx)))
        vy=xslt2(vx)

        svnio = self._loadMVCobject_('svnProjectsIO')
        svnio.putFile(xmlid, ET.tostring(vy), "refresh xml sheets")
        return vy

    def import_file(self, field):
        if field.filename.split('.')[-1] == "ods":
            # put file
            ods_resid = '/'.join(('@'+conf.get('dirSHEETS'),'sources', self.http.params.get('uploaddir', ''), field.filename))
            super(SheetsModel, self).putdata(ods_resid, field.file.read())
            # generate xml
            xml_resid="/".join(('@'+conf.get('dirSHEETS'), 'xml','%s.xml'%field.filename.split('.')[0]))
            self.genVarFile(ods_resid, xml_resid, 'ods')
        else:
            self.setmessage(u"[0027]Erreur: le fichier %(filename)s n'est pas un tableur OpenOffice.", {'filename': field.filename.encode('utf-8')})
            raise

    def setmessage(self, msg, params={}):
        s = tr(msg, params)
        self.__msg += u"<p>%s</p>" %s.i18n(self.http.translation)

    def getResponse(self, field=None):
        return u"<script type=\"text/javascript\">window.parent.kolekti.notify('browser-refresh', {'url': '%s'}, null);</script>"%self.http.path+self.__msg

    ###############################################
    # DAV Methods
    ###############################################

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        if self.__is_root_sheets(resid):
            s = tr(u"[0028]Tableurs")
            p.text = s.i18n(self.http.translation)
        else:
            p.text = resid.split('/')[-1]
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newmodule'})
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if not self.__is_root_sheets(resid):
            if self.isCollection(resid) and resid.split('/')[-1] == "sources":
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'uploadsheet'})
            elif self.isResource(resid):
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaysheets'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'sheetsviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'refreshsheets'})
        return p


    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p

