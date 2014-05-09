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
import time
import urllib

from lxml import etree as ET

from kolektiserver.publication.publication import PublisherError, PublisherPrefixResolver
from kolektiserver.publication.plugins._easiware import ac_index
from kolekti.logger import dbgexc,debug

htmlns="http://www.w3.org/1999/xhtml"

helpname="easiware"

class plugin(pluginBase.plugin):

    def postpub(self):
        """
        main publication function
        """

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
        tfile = "%s.xsl" %self.params.get('template', "default")
        tpath=os.path.join(self.publisher.model.projectpath,'design','publication',self._plugin,'config', tfile)

        #try:
        #    f=ET.XSLT(ET.parse(tpath))
        #    pivot=f(pivot)
        #except:
        #    debug("Filter file not found")

        # generer l'index pour recherche
        iff=file(os.path.join(pubpath,label,'js','index.js'),'w')
        idxx=self.index(pivot)
        iff.write(idxx)
        iff.close()


        css=self.params.get('css','')

        # générer les pages
        try:
            self.generate(pivot,css,pubpath,tpath)
        except PublisherError, e:
            yield (self.publisher.view.error(unicode(e)))
            raise Exception
        except:
            dbgexc()
            yield (self.publisher.view.error(self.publisher.setmessage(u"[0340]Problème lors de l'exécution du script easiware")))
            raise Exception
        
        linkurl = self.publisher.model.local2url(self.publisher.model.pubpath)
        yield(self.publisher.view.publink('index.html', self.label, '/'.join((linkurl, self.label, 'index.html'))))

        try:
            if self.params.has_key('zip') and self.params['zip']=='1':
                #produire un zip
                zipname="%s%s.zip" %(self.publisher.profilename, self.label)
                zf=os.path.join(pubpath,zipname)
                zippy = self.publisher.model.get_zip_object()
                zippy.open(zf,"w")
                top=os.path.join(pubpath,label)
                for root, dirs, files in os.walk(top):
                    for name in files:
                        rt=root[len(top) + 1:]
                        zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))
                zippy.close()
                yield(self.publisher.view.publink('Zip', self.label, '%s/%s' %(linkurl, zipname)))
        except:
            dbgexc()
            yield(self.publisher.view.error(self.publisher.setmessage(u"[0064]Problème lors de la création de l'archive zip")))

    def index(self,pivot):
        idx=ac_index.indexer()
        b=pivot.find("{%s}body" %htmlns)
        for e in b.iterdescendants():
            modid=self.getmodid(e)
            if modid and e.text:
                for word in ac_index.lexer(e.text):
                    idx.addword(word,modid)
            if modid and e.tail:
                for word in ac_index.lexer(e.tail):
                    idx.addword(word,modid)
        return idx.writewords()

    def getmodid(self,elt):
        res=None
        for d in elt.iterancestors():
            if d.tag=="{%s}div"%htmlns and d.get('class')=="moduleinfo":
                return False
            if d.tag=="{%s}div"%htmlns and d.get('class')=="module":
                if d.xpath("h:div[@class='moduleinfo']/h:p[h:span[@class='infolabel']='topic_file']",namespaces={'h':htmlns}):
                    res=d.xpath("h:div[@class='moduleinfo']/h:p[h:span[@class='infolabel']='topic_file']/h:span[@class='infovalue']",namespaces={'h':htmlns})[0].text
                else:
                    res=d.get('id')
        return res

    def generate(self,pivot,css,pubpath,template):
        tplurl = urllib.pathname2url(template)
        xslt=self.get_xsl(os.path.join(self.plugindir,'xsl','generate.xsl'), tplurl)
        templdir=os.path.join(self.publisher.model.projectpath,'design','publication',self._plugin,'config')+os.path.sep
        templtrans=os.path.join(self.publisher.model.projectpath,'sheets')+os.path.sep
        try:
            doc=xslt(pivot,
                     pubdir=u"'%s'"%pubpath.decode(self.LOCAL_ENCODING),
                     pubtitle=u"'%s'"%self.publisher.pubparams.get('pubtitle', 'easiware'),
                     css=u"'%s'"%css.decode(self.LOCAL_ENCODING),
                     templatedir=u"'%s'"%templdir.decode(self.LOCAL_ENCODING),
                     templatetrans=u"'%s'"%templtrans.decode(self.LOCAL_ENCODING),
                     template=u"'%s'"%template.decode(self.LOCAL_ENCODING),
                     label=u"'%s'"%self.label,
                     urlform=u"'%s'"%self.params['urlform'])
        except PublisherError:
            raise
        except Exception, e:
            debug("ERROR FROM XSL")
            debug(xslt.error_log)
            raise Exception, e
            
        #iff=file(os.path.join(pubpath,self.label.encode(self.LOCAL_ENCODING),'index.html'),'w')
        #iff.write(str(doc))
        #iff.close()
        #        doc.write(os.path.join(pubpath,self.publisher.pivname,'index.html'))

    def get_xsl(self,xslfile, tplurl):
        """
        Instanciante an xsl processor with the extensions registered
        and using the custom url resolver
        """
        parser = ET.XMLParser()
        parser.resolvers.add(PublisherPrefixResolver(self.publisher.model))
        xsldoc  = ET.parse(xslfile,parser)
        importelem = xsldoc.find("{http://www.w3.org/1999/XSL/Transform}import[@id='template']")

        importelem.set("href", tplurl)
        xsl = ET.XSLT(xsldoc, extensions=self.publisher.extensions)
        return xsl
