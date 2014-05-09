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


""" Masters model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import time

from lxml import etree as ET

from kolekti.logger import dbgexc
from kolekti.utils.i18n.i18n import tr
from kolektiserver.kolekticonf import conf

from kolektiserver.models.ProjectModel import ProjectModel

class MastersModel(ProjectModel):
    __localNS={"kolekti:browser":"ka",
               "kolekti:usersession":"ku",
               "kolekti:viewer":"kv"}
    _KEEPMETA=False
    _msg = ""
    _masterzipbase = ""
    _masterversion = 0

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(MastersModel,self).__init__(*args,**kwargs)

    @property
    def masterzipbase(self):
        return self._masterzipbase

    @property
    def masterversion(self):
        return self._masterversion

    def getconfig(self, resid):
        ''' Get config file from master '''
        p = None
        try:
            zip = self._loadMVCobject_('ZipFileIO')
            zip.open(data=self.abstractIO.getFile(resid), mode='r')
            self.__set_masterzipbase(zip)
            data = zip.read(self._masterzipbase+'config/config.xml')
            zip.close()
            p = ET.XML(data)
        except:
            dbgexc()
        return p

    def getlang(self, resid):
        ''' Get lang file from master '''
        p = None
        try:
            zip = self._loadMVCobject_('ZipFileIO')
            zip.open(data=self.abstractIO.getFile(resid), mode='r')
            self.__set_masterzipbase(zip)
            data = zip.read(self._masterzipbase+'lang')
            zip.close()
            p = ET.Element("lang", {"value": data})
        except:
            dbgexc()
        return p

    def listCollection(self, resid, ignore_patterns=('_','~','.')):
        tl = [(self.abstractIO.getCreationDate("%s/%s" %(resid,f)),f) for f in self.abstractIO.getDir(resid) if not (f.split('/')[-1].startswith(ignore_patterns) or f.endswith(ignore_patterns))]
        tl.sort(reverse=True)
        return  [l for d,l in tl]

    def import_file(self, field):
        ''' Import upload file '''
        self._masterversion = self._master_version_file(field.file)
        if self._masterversion > 0:
            (res, error) = self._check_master_assembly(field.file)
            if res:
                if self._masterversion == 2:
                    if not self._check_master_manifest(field.file):
                        raise Exception
                dest = '/'.join((self.http.path, self.http.params.get('uploaddir', ''), field.filename))
                if self.abstractIO.exists(dest):
                    self.setmessage(u"[0356]Echec lors de l'ajout de l'enveloppe: %(filename)s déjà existant.", {'filename': field.filename.encode('utf-8')})
                    raise Exception
                super(MastersModel, self).putdata(dest, field.file.read())
            else:
                if not error is None:
                    self.setmessage(error)
                else:
                    self.setmessage(u"[0355]moduleinfo source manquants dans le fichier assembly.xhtml de l'enveloppe %(filename)s.", {'filename': field.filename.encode('utf-8')})
                raise Exception
        else:
            self.setmessage(u"[0019]Le fichier %(filename)s n'est pas une enveloppe.", {'filename': field.filename.encode('utf-8')})
            raise Exception

    def setmessage(self, msg, params={}):
        s = tr(msg, params)
        self._msg += u"<p>%s</p>" %s.i18n(self.http.translation)

    def getmessage(self):
        return self._msg

    def getResponse(self, field=None):
        return u"<script type=\"text/javascript\">window.parent.kolekti.notify('browser-refresh', {'url': '%s'}, null);</script>"%self.http.path+self._msg

    def _history(self, resid):
        res=ET.Element('listfiles')
        try:
            mfile = '/'.join((('@'+conf.get('dirMASTERS')), '_manifest.xml'))
            return ET.XML(self.abstractIO.getFile(mfile))
        except:
            dbgexc()
        return res

    def _master_version_file(self, file):
        ''' Check if file is a master '''
        # TODO check if is master v1 or v2
        version = 0
        try:
            zip = self._loadMVCobject_('ZipFileIO')
            zip.open(file, 'r')
            self.__set_masterzipbase(zip)
            # Check if required files exist
            zip.getinfo(self._masterzipbase+'config/config.xml')
            zip.getinfo(self._masterzipbase+'lang')
            zip.getinfo(self._masterzipbase+'assembly.xhtml')
            zip.getinfo(self._masterzipbase+'modules-history.xml')
            try:
                xml = ET.XML(zip.read(self._masterzipbase+'config/manifest.xml'))
                version = int(xml.get("version", '1'))
            except KeyError:
                version = 1
            zip.close()
            file.seek(0)
        except:
            dbgexc()
            version = 0
        return version

    def _check_master_manifest(self, file):
        ''' Check if files reference by manifest exists in zip '''
        zip = self._loadMVCobject_('ZipFileIO')
        zip.open(file, 'r')
        ok = True
        xml = ET.XML(zip.read(self._masterzipbase+'config/manifest.xml'))
        for f in xml.getchildren():
            try:
                zip.getinfo(self._masterzipbase+f.get("ref", "foo"))
            except KeyError:
                self.setmessage(u"[0357]Fichier %(filename)s manquant dans l'enveloppe.", {'filename': unicode(f.get('ref'))})
                ok = False
        zip.close()
        file.seek(0)

        return ok

    def __set_masterzipbase(self, zip):
        ''' Find base folder in master '''
        for arcname in zip.namelist():
            if arcname.split('/')[-1] == "assembly.xhtml":
                basename = arcname.rsplit('/', 1)[0]
                if basename != arcname:
                    self._masterzipbase = arcname.rsplit('/', 1)[0]+'/'
                break

    def _check_master_assembly(self, file):
        ''' Check if assembly file in a master '''
        try:
            zip = self._loadMVCobject_('ZipFileIO')
            zip.open(file, 'r')
            self.__set_masterzipbase(zip)
            assembly = zip.read(self._masterzipbase+'assembly.xhtml')
            parser = ET.XMLParser(load_dtd=True)
            xml = ET.XML(assembly, parser)
            modsrc = xml.xpath("//h:div[@class='moduleinfo']/h:p[1]/h:span[@class='infolabel'][1]", namespaces={"h": "http://www.w3.org/1999/xhtml"})
            modsrcinfo = xml.xpath("//h:div[@class='moduleinfo']/h:p[1]/h:span[@class='infolabel'][1][text() = 'source']", namespaces={"h": "http://www.w3.org/1999/xhtml"})
            zip.close()
            file.seek(0)
            return (len(modsrc) == len(modsrcinfo), None)
        except ET.XMLSyntaxError, exc:
            return (False, unicode(exc))
        except:
            dbgexc()
            return (False, None)

    def __is_root_masters(self, id):
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
        if self.__is_root_masters(resid):
            s = tr(u"[0020]Enveloppes")
            p.text = s.i18n(self.http.translation)
        else:
            fname = resid.split('/')[-1]
            p.text = fname
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'uploadmaster'})
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if not self.__is_root_masters(resid):
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaymaster'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'masterviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'getmaster'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'publishmaster'})
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p
