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
import time

from lxml import etree as ET
htmlns="http://www.w3.org/1999/xhtml"

class plugin(pluginBase.plugin):
    def postpub(self):
        # supprimer le répertoire publication S5
        #try:
        #    shutil.rmtree(os.path.join(pubpath,'S5'))
        #except:
        #    pass
        # creer le répertoire publication S5
        pubpath = self.publisher.model.pubpath
        try:
            os.mkdir(os.path.join(pubpath,self.label))
        except:
            pass

        # copier le contenu la lib dans le répertoire de publication
        libdir=os.path.join(self.plugindir,'lib','ui')
        for d in os.listdir(libdir):
            shutil.copytree(os.path.join(libdir,d),os.path.join(pubpath,self.label,'ui',d))

        # copier la css S5
        # copier les elements de la css S5
        css = self.params.get('css', '')

        # copier les illustration et css
        # copier le logo
        #shutil.copytree(os.path.join(pubpath,'css'),os.path.join(pubpath,helpname,'css'))
        try:
            shutil.copytree(os.path.join(pubpath,'medias'),os.path.join(pubpath,self.label,'medias'))
        except:
            pass

        # générer les pages
        pivot = self.publisher.document
        self.generate(pivot,css,pubpath)

        linkurl = self.publisher.model.local2url(self.publisher.model.pubpath)
        yield(self.publisher.view.publink('index.html', self.label, '/'.join((linkurl, self.label, 'index.html'))))

        if self.params.has_key('zip') and self.params['zip']=='1':
            #produire un zip
            zipname="%s%s.zip" %(self.publisher.profilename, self.label)
            zf=os.path.join(pubpath,zipname)
            zippy = self.publisher.model.get_zip_object()
            zippy.open(zf,"w")
            top=os.path.join(pubpath,'S5')
            for root, dirs, files in os.walk(top):
                for name in files:
                    rt=root[len(top) + 1:]
                    zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(self.label, rt, name)))
            zippy.close()
            yield(self.publisher.view.publink('Zip', self.label, '%s/%s' %(linkurl, zipname)))

    def generate(self,pivot,css,pubpath):
        xslt_doc=ET.parse(os.path.join(self.plugindir,'xsl','S5.xsl'))
        xslt=ET.XSLT(xslt_doc)
        templdir=os.path.join(self.publisher.model.projectpath,'sheets')+os.path.sep
        doc=xslt(pivot,
                 pubdir="'%s'"%pubpath,
                 css="'%s'"%css)

        iff=file(os.path.join(pubpath,self.label,'index.html'),'w')
        iff.write(str(doc))
        iff.close()
