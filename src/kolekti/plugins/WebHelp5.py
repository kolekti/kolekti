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


import os
import time
import shutil
import logging

from lxml import etree as ET

from kolekti.plugins import pluginBase
from _WebHelp5 import ac_index

htmlns="http://www.w3.org/1999/xhtml"

helpname="WebHelp5"

class plugin(pluginBase.plugin):
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        logging.debug( "WebHelp5  : %s %s"%(self.assembly_dir,self.publication_dir))

        # copy libs from assembly space to publication directory
        
#        libsdir = os.path.join(self.getOsPath('/'.join([self.assembly_dir,self.get_base_template(label)])), 'lib')
#        libpdir = os.path.join(self.getOsPath(self.publication_dir), 'lib')
#        try:
#            shutil.rmtree(libpdir)
#        except:            
#            pass
#        shutil.copytree(libsdir, libpdir)


        # ouvrir le fichier template
        templatename = self.get_script_parameter('template')
        logging.debug( "WebHelp5 template : %s"%templatename)
        if len(templatename):
            tfile="%s.xht"%templatename
        else:
            tfile="%s.xht"%self._plugin
        templatepath = '/'.join([self.assembly_dir,self.get_base_template(self.scriptname),tfile])
        template=self.parse(templatepath)

        # copier les illustration et css
        # copier le logo
        try:
            logo=template.xpath("//html:span[@id='logo_visuel']",namespaces={'html':htmlns})[0].text
            self.copy_file('/'.join(['medias',logo]), self.publication_dir)
        except:
            pass

        #self.copy_dirfiles(os.path.join(pubpath,'css'),os.path.join(pubpath,self.publisher.pivname,'css'))
        self.copymedias()
        

        # pivot = self.filter_pivot(self.pivot)
        
        #try:
        #    filterfile="%s.xsl"%self.get_script_parameter('template')
        #    filter=self.parse('/'.join([self.assembly_dir,self.get_base_template(label),filterfile]))
        #    f=ET.XSLT(filter)
        #    pivot=f(pivot)
        #except:
        #    logging.debug("warning: Filter file not found: %s"%filterfile)

        # generer l'index pour recherche
        try:
            self.makedirs('/'.join([self.publication_plugin_dir,'js']))
        except:
            pass
        idxx=self.index(self.pivot)
        with open(self.getOsPath('/'.join([self.publication_plugin_dir,'js','index.js'])),'w') as iff:
            iff.write(idxx)

        css=self.get_script_parameter('css')

        # générer les pages
        xslt=self.get_xsl('xsl/generate', profile = self.profile, lang = self.lang)
        puburl=self.getUrlPath(self.publication_plugin_dir)
        templateurl=self.getUrlPath(templatepath)
        try:
            doc=xslt(self.pivot,
                     pubdir=u"'%s'"%puburl,
                     css=u"'%s'"%css,
                     template=u"'%s'"%templateurl,
                     )
            res.append({'type':"html", "label":"%s_%s"%(self.publication_file,self.scriptname), "url": "%s/index.html"%self.publication_plugin_dir})
        except:
            logging.error('WebHelp5: pages generation failed')
            import traceback
            logging.debug(traceback.format_exc())
            logging.debug(xslt.error_log)
            logging.debug('--')
            raise Exception

#        linkurl = self.publisher.model.local2url(self.publisher.model.pubpath)
#        yield(self.publisher.view.publink('index.html', self.label, '/'.join((linkurl, self.label, 'index.html'))))

        try:
            if self.get_script_parameter('zip'):
                from zipfile import ZipFile
                #produire un zip
                zipname="%s_%s.zip" %(self.publication_file, self.scriptname)
                top = self.getOsPath(self.publication_plugin_dir)
                zf=os.path.join(self.getOsPath(self.publication_dir), zipname)
                with ZipFile(zf,"w") as zippy:
                    for root, dirs, files in os.walk(top):
                        for name in files:
                            if name == zipname:
                                continue
                            rt=root[len(top) + 1:]
                            zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))

                res.append({'type':"zip", "label":zipname, "url": "%s/%s"%(self.publication_dir,zipname)})
                #yield(self.publisher.view.publink('Zip', self.label, '%s/%s' %(linkurl, zipname)))
        except:
            logging.error('WebHelp5: zip archive generation failed')
            import traceback
            logging.debug(traceback.format_exc())
            print traceback.format_exc()
        logging.debug( "generation complete")
        return res
    
    def index(self,pivot):
        logging.debug("**** Search index")
        self.__firstmod = ""
        idx=ac_index.indexer()
        b=pivot.xpath("/h:html/h:body",namespaces={'h':htmlns})[0]
        for e in b.iterdescendants():
            modid=self.getmodid(e)
            if modid and e.text:
                for word in ac_index.lexer(e.text):
                    idx.addword(word,modid)
            if modid and e.tail:
                for word in ac_index.lexer(e.tail):
                    idx.addword(word,modid)
        
        logging.debug("**** Search index DONE")
        return idx.writewords()

    def getmodid(self,elt):
        res=None
        for d in elt.iterancestors():
            if d.tag=="{%s}div"%htmlns and d.get('class')=="topicinfo":
                return False
            if d.tag=="{%s}div"%htmlns and d.get('class')=="topic":
                if d.xpath("h:div[@class='topicinfo']/h:p[h:span[@class='infolabel']='topic_file']",namespaces={'h':htmlns}):
                    res=d.xpath("h:div[@class='topicinfo']/h:p[h:span[@class='infolabel']='topic_file']/h:span[@class='infovalue']",namespaces={'h':htmlns})[0].text
                else:
                    res=d.get('id')
                if self.__firstmod == "" or self.__firstmod == res:
                    self.__firstmod = res
                    res = "index"
                break
        return res


    def filter_pivot(self,pivot):
        try:
            xslfile ='/'.join(['design','publication',self._plugin,'config','filter.xsl'])
            xsldoc = self.parse(xslfile)
            xslt = ET.XSLT(xsldoc)
            filtered_pivot=xslt(pivot)
        except:
            import traceback
            logging.debug(traceback.format_exc())
            return pivot
        return filtered_pivot
