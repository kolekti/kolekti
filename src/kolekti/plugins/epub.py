# -*- coding: utf-8 -*-
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
import mimetypes

from lxml import etree as ET

helpname="epub"

class plugin(pluginBase.plugin):
    htmlns="http://www.w3.org/1999/xhtml"
    extensions = {}

    def postpub(self):
        # init xslt extensions
        self._load_extensions()

        pubpath = self.publisher.model.pubpath

        # creer les répertoire pour la publication epub
        self.__makedirs(os.path.join(pubpath,self.label,'META-INF'))
        self.__makedirs(os.path.join(pubpath,self.label,'OEBPS', 'chapters'))
        self.__makedirs(os.path.join(pubpath,self.label,'OEBPS', 'medias'))

        # copier le contenu la lib dans le répertoire kohelp
        self.copy_dirfiles(os.path.join(self.plugindir,'lib'), os.path.join(pubpath,self.label,'OEBPS'))

        pivot = self.publisher.document
        self.process_medias(pivot)

        css=self.params.get('css','')

        # génére les pages
        self.generate(pivot,css,pubpath)
        self.generate_cover(pivot, pubpath)
        
        for msg in self.copy_medias(pivot, pubpath):
            yield msg

        fp = open(os.path.join(pubpath, self.label, 'mimetype'),'w')
        fp.write("application/epub+zip")
        fp.close()

        epubname = "%s%s.epub" %(self.publisher.profilename, self.label)
        try:
            zippy = self.publisher.model.get_zip_object()
            zippy.open(os.path.join(pubpath, self.label, epubname),"w")
            top=os.path.join(pubpath,self.label)
            for root, dirs, files in os.walk(top):
                for name in files:
                    if name != epubname:
                        rt=root[len(top) + 1:]
                        zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))
            zippy.close()
            yield(self.publisher.view.publink(epubname, self.label, '/'.join((self.publisher.model.local2url(pubpath), self.label, epubname))))
        except:
            yield(self.publisher.view.error(self.publisher.setmessage(u"[0065]Problème lors de la création de l'epub")))

    def process_medias(self, pivot):
        for img in pivot.xpath('/h:html/h:body//h:img|/h:html/h:body//h:embed', namespaces={'h':'http://www.w3.org/1999/xhtml'}):
            if not img.get('src').startswith('http://'):
                try:
                    img.set('src', 'medias/%s' %img.get('src').split('/medias/')[1])
                except:
                    continue

    def copy_medias(self, pivot, pubpath):
        for med in pivot.xpath("/h:html/h:body//h:img",namespaces={'h':self.htmlns}):
            try:
                medpath = os.path.join(pubpath, med.get('src').replace('/', os.sep))
                meddest = os.path.join(pubpath, self.label, 'OEBPS', med.get('src').replace('/', os.sep))
                destdir = os.path.dirname(meddest)
                if not os.path.exists(destdir): 
                    os.makedirs(destdir)
                shutil.copy(medpath, meddest)
            except:
                yield(self.publisher.view.error(self.publisher.setmessage(u"[0066]Impossible de copier l'illustration %(media)s", {'media': str(med.get('src'))})))

    def generate_cover(self,pivot,pubpath):
        fp = open(os.path.join(pubpath,self.label,'OEBPS', 'coverpage.html'), 'w')
        fp.write("""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Cover</title>
<style  type="text/css"> img { max-width: 100%; } </style>
</head>
<body class="cpw">
<div id="cover-image"><p>Couverture</p></div></body></html>
        """)
        fp.close()

    def generate(self,pivot,css,pubpath):
        xslt=self._xsl(os.path.join(self.plugindir,'xsl','generate.xsl'))
        doc=xslt(pivot,
                 pubdir="'%s/%s'"%(pubpath,self.label),
                 css="'%s.css'"%css)

        xslt=self._xsl(os.path.join(self.plugindir,'xsl','generate-contentopf.xsl'))
        doc=xslt(pivot,
                 lang="'%s'"%self.publisher.model.lang,
                 author="'dummy!'",
                 css="'%s.css'"%css)
        doc.write(os.path.join(pubpath,self.label,'OEBPS','content.opf'))

        xslt=self._xsl(os.path.join(self.plugindir,'xsl','generate-tocncx.xsl'))
        toc=xslt(pivot)
        xslt=self._xsl(os.path.join(self.plugindir,'xsl','clean-tocncx.xsl'))
        toc=xslt(toc)
        toc.write(os.path.join(pubpath,self.label,'OEBPS','toc.ncx'))

    def __makedirs(self, path):
        try:
            os.makedirs(path)
        except:
            pass

    def _load_extensions(self):
        super(plugin, self)._load_extensions()
        extf_obj = EpubExtensionsFunctions()
        exts = (n for n in dir(EpubExtensionsFunctions) if not(n.startswith('_')))
        self.extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))

# XSL extensions
class EpubExtensionsFunctions(object):
    ens = "kolekti:extensions:epub:functions"

    def mimetype(self, _, *args):
        url = args[0]
        (type, enc) = mimetypes.guess_type(url)
        return type
