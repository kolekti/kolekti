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

from lxml import etree as ET

import pluginBase
from _WebHelp5 import ac_index

htmlns="http://www.w3.org/1999/xhtml"

helpname="WebHelp5"

class plugin(pluginBase.plugin):

    def postpub(self):
        """
        main publication function
        """
        label = self.scriptdef.get('name')
       
        # copier le contenu la lib dans le répertoire kohelp
        libsdir = os.path.join(self._plugindir,'lib')

        libpdir = os.path.join(self.getOsPath(self.pubscriptdir), 'lib')
        try:
            shutil.rmtree(libpdir)
        except:            
            pass
        shutil.copytree(libsdir, libpdir)

        libpdir = os.path.join(self.getOsPath('/'.join([self.pubprofiledir_c,'stylesheets',label])), 'lib')
        try:
            shutil.rmtree(libpdir)
        except:            
            pass
        shutil.copytree(libsdir, libpdir)

        # ouvrir le fichier template
        templatename = self.get_script_parameter('template')
        if len(templatename):
            tfile="%s.xht"%templatename
        else:
            tfile="%s.xht"%self._plugin
        template=self.parse('/'.join(['design','publication',self._plugin,'config',tfile]))

        # copier les illustration et css
        # copier le logo
        try:
            logo=template.xpath("//html:span[@id='logo_visuel']",namespaces={'html':htmlns})[0].text
            self.copy_file('/'.join(['medias',logo]),self.pubscriptdir)
        except:
            pass

        #self.copy_dirfiles(os.path.join(pubpath,'css'),os.path.join(pubpath,self.publisher.pivname,'css'))
        self.copymedias()
        

        pivot = self.filter_pivot(self.pivot)
        
        try:
            filterfile="%s.xsl"%self.get_script_parameter('template')
            filter=self.parse('/'.join('design','publication',self._plugin,'config',filterfile))
            f=ET.XSLT(filter)
            pivot=f(pivot)
        except:
            print "Warning : Filter file not found", filterfile

        # generer l'index pour recherche
        try:
            self.makedirs('/'.join([self.pubscriptdir,'js']))
        except:
            pass
        idxx=self.index(pivot)
        with open(self.getOsPath('/'.join([self.pubscriptdir,'js','index.js'])),'w') as iff:
            iff.write(idxx)


        css=self.get_script_parameter('css')

        # générer les pages
        xslt=self.get_xsl('generate', profile = self.profile, lang = self.lang)
        templdir=self.getUrlPath('/'.join(['design','publication',self._plugin,'config']))+'/'
        templtrans=self.getUrlPath('sheets')+'/'
        puburl=self.getUrlPath(self.pubscriptdir)
        try:
            doc=xslt(pivot,
                     pubdir=u"'%s'"%puburl,
                     css=u"'%s'"%css,
                     templatedir=u"'%s'"%templdir,
                     templatetrans=u"'%s'"%templtrans,
                     template=u"'%s'"%template,
                     label=u"'%s'"%label,
                     )
        except:
            import traceback
            print traceback.format_exc()
            print "ERROR FROM XSL"
            print xslt.error_log
            raise Exception

#        linkurl = self.publisher.model.local2url(self.publisher.model.pubpath)
#        yield(self.publisher.view.publink('index.html', self.label, '/'.join((linkurl, self.label, 'index.html'))))

        try:
            if self.get_script_parameter('zip'):
                #produire un zip
                zipname="%s%s.zip" %(profile.get('name'), label)
                zf=os.path.join(pubpath,zipname)
                zippy = self.publisher.model.get_zip_object()
                zippy.open(zf,"w")
                for root, dirs, files in os.walk(self.pubscriptdir):
                    for name in files:
                        rt=root[len(top) + 1:]
                        zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))
                zippy.close()
                #yield(self.publisher.view.publink('Zip', self.label, '%s/%s' %(linkurl, zipname)))
        except:
            import traceback
            print traceback.format_exc()
            #yield(self.publisher.view.error(self.publisher.setmessage(u"[0064]Problème lors de la création de l'archive zip")))
        yield self._plugin, "OK"
        return
    
    def index(self,pivot):
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
            print traceback.format_exc()
            return pivot
        return filtered_pivot
