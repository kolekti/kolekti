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

import os
import time
import copy

from StringIO import StringIO
from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolekti.logger import dbgexc,debug

from kolektiserver.models.PublishModel import PublishModel
from kolektiserver.models.MastersModel import MastersModel

class TranslateModel(PublishModel, MastersModel):
    _msg = ""
    _masterzipbase = ""
    _masterversion = 0

    def __init__(self, *args, **kargs):
        super(TranslateModel, self).__init__( *args, **kargs)
        resid = self.http.getdata('kolekti','resid')
        if resid.startswith('@masters'):
            self.mastername = resid.split('/')[-1]
        else:
            self.mastername = ''

    @property
    def pivot(self):
        parser = ET.XMLParser(load_dtd=True)
        p = self.__zipfile.read(self._masterzipbase+'assembly.xhtml')
        return ET.XML(p, parser)

    @property
    def config(self):
        xml = self.__zipfile.read(self._masterzipbase+'config/config.xml')
        return ET.XML(xml)

    @property
    def modules_history(self):
        xml = self.__zipfile.read(self._masterzipbase+'modules-history.xml')
        return ET.XML(xml).getroottree()

    @property
    def module_infos(self):
        xml = self.__zipfile.read(self._masterzipbase+'config/moduleinfos.xml')
        return ET.XML(xml)

    @property
    def lang(self):
        try:
            # Read master lang file
            lang = self.__zipfile.read(self._masterzipbase+'lang')
            return lang.strip()
        except:
            return super(TranslateModel, self).lang

    @property
    def locale_lang(self):
        return super(TranslateModel, self).lang

    def savemaster(self, zipfile):
        self._masterversion = self._master_version_file(zipfile.file)
        if self._masterversion > 0:
            (res, error) = self._check_master_assembly(zipfile.file)
            if res:
                if self._masterversion == 2:
                    if not self._check_master_manifest(zipfile.file):
                        return None
                self.mastername = zipfile.filename
                mpath = u'@masters/%s' %zipfile.filename
                if self.abstractIO.exists(mpath):
                    self.setmessage(u"[0356]Echec lors de l'ajout de l'enveloppe: %(filename)s déjà existant.", {'filename': ufile.filename.encode('utf-8')})
                    return None
                self.abstractIO.putFile(mpath, zipfile.file.read())
                return self.abstractIO.normalize_id(mpath)
            else:
                if not error is None:
                    self.setmessage(error)
                else:
                    self.setmessage(u"[0355]moduleinfo source manquants dans le fichier assembly.xhtml de l'enveloppe %(filename)s.", {'filename': ufile.filename.encode('utf-8')})
                return None
        else:
            self.setmessage(u"[0019]Le fichier %(filename)s n'est pas une enveloppe.", {'filename': zipfile.filename.encode('utf-8')})

    def setzip(self, zipfile):
        self.__zipfile = self._loadMVCobject_('ZipFileIO')
        self.__zipfile.open(zipfile, 'r')
        self.__set_masterzipbase(self.__zipfile)

    def __set_masterzipbase(self, zip):
        for arcname in zip.namelist():
            if arcname.split('/')[-1] == "assembly.xhtml":
                basename = arcname.rsplit('/', 1)[0]
                if basename != arcname:
                    self._masterzipbase = arcname.rsplit('/', 1)[0]+'/'
                break

    def closezip(self):
        self.__zipfile.close()

    def params(self):
        params = {}
        config = self.config

        params['pubdir'] = unicode(config.xpath("string(/data/field[@name='pubdir']/@value)"))
        params['pubtitle'] = unicode(config.xpath("string(/data/field[@name='pubtitle'][not(@value = '')]/@value|/data[not(field[@name='pubtitle']) or field[@name='pubtitle']/@value = '']/@id)"))
        params['profiles'] = config.xpath("/data/profiles/profile")
        params['scripts'] = config.xpath("/data/scripts/script")
        params['trame'] = unicode(config.xpath("string(/data/field[@name='trame']/@value)"))
        params['mastername'] = unicode(config.xpath("/data/field[@name='mastername']/@value"))
        try:
            params['filtermaster'] = unicode(config.xpath("/data/field[@name='filtermaster']/@value"))
        except:
            pass

        return params

    def profile(self, resid):
        p = self.__zipfile.read(self._masterzipbase+resid)
        return ET.XML(p)

    def isCollection(self, resid):
        return True

    def getvariables(self, filename):
        try:
            foff = StringIO(self.__zipfile.read(self._masterzipbase+'sheets/sources/%s.ods'%filename))
            xml = self.genVarFile(foff, 'ods')
        except:
            debug(u"Missing sheet file '%s' in master, try to get local" %filename)
            return super(TranslateModel, self).getvariables(filename)
        # replace xml lang by lang file
#        lang = zip.read('lang').strip()
#        for crit in xml.xpath("/h:variables/h:variable/h:value/h:crit[@name='LANG']", namespaces={"h":"http://www.w3.org/1999/xhtml"}):
#            crit.set('value', lang)
        return xml.getroot()

    def medias_copy(self, source, srcdir="medias"):
        if srcdir != "medias":
            return super(TranslateModel, self).medias_copy(source,srcdir)
        src = u'/'.join(source.split('/')[3:])
        dest = u'/'.join((self.pubdir, src))
        realcd = u'/'.join(dest.split('/')[:-1])
        if not(self.abstractIO.exists(realcd)):
            self.abstractIO.makedirs(dest)
        media = self.__zipfile.read(self._masterzipbase+src)
        self.abstractIO.putFile(dest,media)
        return self.abstractIO.normalize_id(dest)
    
    def generateManifest(self, trame):
        ''' Generate manifest file '''
        mfile = '/'.join((('@'+conf.get('dirPUB')), '_manifest.xml'))
        if self.abstractIO.exists(mfile):
            m=self.abstractIO.getpath(mfile)
            elt = ET.parse(m)
            manifest = elt.getroot()
        else:
            manifest = ET.Element('manifest')
        ET.SubElement(manifest, 'publication', {'trame': trame, 'uid': str(self.http.userId), 'time': str(self.pubtime), 'master': self.mastername})
        self.abstractIO.putFile(mfile, ET.tostring(manifest, pretty_print=True))

    def genVarFile(self,foff,ftype,filter="export-variables"):
        # genere le fichier de textes automatiques à partir du openoffice
        debug ('gen variables file')
        xslt_doc1=ET.parse(os.path.join(conf.get('appdir'),'publication','xsl','oofilters','%s-%s-pass1.xsl'%(filter,ftype)))
        xslt1=ET.XSLT(xslt_doc1)
        xslt_doc2=ET.parse(os.path.join(conf.get('appdir'),'publication','xsl','oofilters','%s-pass2.xsl'%(filter)))
        xslt2=ET.XSLT(xslt_doc2)
        z = copy.copy(self.__zipfile)
        z.open(foff, 'r')
        foffx=z.read('content.xml')
        z.close()
        vx=xslt1(ET.ElementTree(ET.XML(foffx)))
        vy=xslt2(vx)
        return vy

