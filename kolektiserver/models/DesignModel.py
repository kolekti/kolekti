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




""" Design model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

from lxml import etree as ET
from zipfile import BadZipfile

from kolekti.utils.i18n.i18n import tr

from kolektiserver.models.ProjectModel import ProjectModel

class DesignModel(ProjectModel):
    __msg = ""
    __localNS={"kolekti:browser":"ka",
               "kolekti:usersession":"ku",
               "kolekti:viewer":"kv"}
    _KEEPMETA=False

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(DesignModel,self).__init__(*args,**kwargs)

    def __is_root_design(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        rootlim = 5
        try:
            if splitId[4] == "edition":
                rootlim = 6
        except:
            pass
        return len(splitId) <= rootlim

    def copy(self, id, copyid):
        prjdir = self.project.get('directory')
        if self.abstractIO.isFile(id) and self.abstractIO.normalize_id(id).startswith("/projects/%s/design/edition/templates" %prjdir):
            moddata = self.abstractIO.getFile(id)
            moddata = moddata.replace('[[project]]', self.project.get('directory'))
            try:
                self.abstractIO.putFile(copyid, moddata)
            except:
                dbgexc()
                raise EXC.FailedDependency
        else:
            super(DesignModel, self).copy(id, copyid)

    def import_file(self, field):
        try:
            zip = self._loadMVCobject_('ZipFileIO')
            zip.open(field.file, 'r')
            listfiles = zip.namelist()
            if self.__validate_zip(listfiles):
                # Save file
                for n in listfiles:
                    if n[-1] == "/":
                        if not self.abstractIO.exists(u'@design/%s'%n):
                            self.abstractIO.mkDir(u'@design/%s'%n)
                    else:
                        self.putdata(u'@design/%s'%n, zip.read(n))
            else:
                raise
            zip.close()
        except BadZipfile:
            self.setmessage(u"[0016]Erreur: le fichier %(filename)s n'est pas une archive zip.", {'filename': field.filename.encode('utf-8')})
            raise
        except:
            self.setmessage(u"[0017]Erreur: l'archive %(filename)s n'est pas conforme.", {'filename': field.filename.encode('utf-8')})
            raise

    def setmessage(self, msg, params={}):
        s = tr(msg, params)
        self.__msg += u"<p>%s</p>" %s.i18n(self.http.translation)

    def getmessage(self):
        return self.__msg

    def getResponse(self, field=None):
        return u"<script type=\"text/javascript\">window.parent.kolekti.notify('browser-refresh', {'url': '%s'}, null);</script>"%self.http.path+self.__msg

    def __validate_zip(self, listfiles):
        '''Verification is zip file contains required dirs '''
        for n in listfiles:
            if n.startswith('edition/'):
                if not(n == "edition/" or n.startswith(('edition/templates/', 'edition/trames_templates/', 'edition/styles/'))):
                    return False
            elif n.startswith('publication/'):
                if not(n == "publication/" or n[0:len('publication/%s' %n.split('/')[1])+1][-1] == '/'):
                    return False
            else:
                return False
        return True

    ###############################################
    # DAV Methods
    ###############################################

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        dn = self.abstractIO.normalize_id(resid).split('/')[-1]
        if dn == u"design":
            s = tr(u"[0018]Styles")
            dn = s.i18n(self.http.translation)
        p.text = dn
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'uploaddesign'})
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if not self.__is_root_design(resid):
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaydesign'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'designviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p

