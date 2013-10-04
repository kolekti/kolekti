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


import pluginBase
import os
import shutil

from lxml import etree as ET


class plugin(pluginBase.plugin):

    extensions = {}

    def postpub(self):
        """
        main publication function
        """

        self._load_extensions()
        pubpath = self.publisher.model.pubpath
        label=self.label.encode(self.LOCAL_ENCODING)
        try:
            os.mkdir(os.path.join(pubpath,label))
        except:
            pass

        # copier le contenu la lib dans le répertoire kohelp
        libdir=os.path.join(self.plugindir,'lib')
        self.copy_dirfiles(libdir,os.path.join(pubpath,label))

        try:
            self.copy_dirfiles(os.path.join(pubpath,'medias'),os.path.join(pubpath,label,'medias'))
        except:
            pass

        pivot = self.publisher.document

        css=self.params.get('css','')

        # générer les pages
        self.generate(pivot,css,pubpath)

        #produire un zip
        zipname="%s%s.zip" %(self.publisher.profilename, self.suffix)
        zf=os.path.join(pubpath,zipname)
        zippy = self.publisher.model.get_zip_object()
        zippy.open(zf,"w")
        top=os.path.join(pubpath,label)
        for root, dirs, files in os.walk(top):
            for name in files:
                rt=root[len(top) + 1:]
                zippy.write(os.path.join(root, name),arcname=os.path.join(rt, name))
        zippy.close()

        yield(self.publisher.view.publink("Zip", self.label, '%s/%s' %(self.publisher.model.local2url(pubpath), zipname)))

    def generate(self,pivot,css,pubpath):
        publang = self.publisher.model.lang.lower(),
        xslt_doc = ET.parse(os.path.join(self.plugindir,'xsl','generate.xsl'))
        xslt = ET.XSLT(xslt_doc)
        doc = xslt(pivot,
                 publang="'%s'"%publang,
                 pubdir="'%s'"%pubpath,
                 css="'%s'"%css,
                 label="'%s'"%self.label)

        # generation des hhp/hhk/hhc
        xslt = self._xsl(os.path.join(self.plugindir,'xsl','publish-doc-help.xsl'))
        doc = xslt(pivot,
                 langfile="'%s'"%os.path.join(self.plugindir,'languages.xml'),
                 publang="'%s'"%publang,
                 pubdocdir="'%s'"%pubpath,
                 pubdoccode="'%s'"%self.label,
                 profilename="'%s'" % self.publisher.pivname,
                 sheetspath="'%s'"%self.publisher.model.abstractIO.getpath(u'@sheets/xml'))


