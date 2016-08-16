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



import os
import time
import urllib
import urllib2
import json
import uuid
from lxml import etree as ET
from PIL import Image
from StringIO import StringIO
from zipfile import ZipFile
import tempfile
import subprocess
import re

import logging
logger = logging.getLogger(__name__) 
import pygal

#from _odt import odtpdf
from kolekti.plugins import pluginBase

MFNS="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"

def getid(iter):
    return "10000000000%8X%05X"%(int(time.strftime('6013670%Y%m%d%M%S')),iter)
    

class plugin(pluginBase.plugin):
    """
    Plugin for odt publication

    Injects the content of the pivot file into an odt template
    The way xhtml is converted into odt is defined :
    - by a xslt preprocessing of the xhtml file : design/publication/opendocument/[theme]/filter.xsl
    - by a set of conversion mapping rules design/publication/opendocument/[theme]/mapping.xml
    """

    _META_= {
        "templates":"design/publication/opendocument",
        "add_to_projects":True,
        "parameters":''
        }
        
    _ns ={'h':'http://www.w3.org/1999/xhtml'}
     
    def postpub(self):
        res = []
        logger.debug(self.assembly_dir)
        dfile=StringIO()
        tfile = self.get_script_parameter('template')
        if tfile is None:
            tfile=self._plugin
        templatepath = '/'.join([self.get_base_template(self.scriptname),"%s.ott"%tfile])
        logger.debug(templatepath)
        # get the theme elements for publishing

        mapfile = '/'.join([self.get_base_template(self.scriptname),"mapping.xml"])
        tmppivot = "%s/tmppiv.xml" %(self.publication_plugin_dir,)
        tmpstyles = "%s/tmpstyles.xml" %(self.publication_plugin_dir,)

        tmpdebug = "%s/tmpdebug.xml" %(self.publication_plugin_dir,)
        
        #coverfile= os.path.join(self.publisher.model.projectpath,tplpath,theme,"cover.xsl")
        #filterfile=os.path.join(self.publisher.model.projectpath,tplpath,theme,"filter.xsl")
        
        # res.append({'type':"opendocument", "label":"sss", "url": ""})
        # return res

        # generate elocus graphics
        self._generate_graphics()
        
        # apply the pre filter.xsl to the pivot file
        try:
            xslt = self.get_xsl("filter", profile = self.profile, lang = self._publang)
            pivot = xslt(self.pivot)
        except:
            logger.exception('error in fiter pivot')
            pivot = self.pivot
            debug(f.error_log )
        
        # copy the template into the publication space
        # shutil.copy(tfile, dfile)
        self.xwrite(pivot, tmpdebug)

        # uncompress the template
        with ZipFile(self.getOsPath(templatepath),'r') as zipin:
            with ZipFile(dfile,'w') as zipout:
                # get the template index of files
                mf=ET.XML(zipin.read('META-INF/manifest.xml'))


                # handle all media
                odtids={}
                iter = 0
                try:
                    for img in pivot.xpath('/h:html/h:body//h:img', namespaces=self._ns):
                        newsrc = img.get('src')
                        newsrc = "/".join([self.publication_plugin_dir,newsrc])
                        logger.debug('image %s'%newsrc)
                        if odtids.get(newsrc, '') == '':
                            # get an uuid for the image
                            odtid = getid(iter)+os.path.splitext(newsrc)[1]
                            odtids.update({newsrc: odtid})
                            iter += 1
                            # copy the media in the zip
                            try:
                                imgdata=self.read(newsrc)
                                zipout.writestr("Pictures/%s"%str(odtid),imgdata)
    
                                # registers the image in the manifest
                                ment=ET.SubElement(mf,"{%s}file-entry"%MFNS)
                                ment.set("{%s}media-type"%MFNS,"image/png")
                                ment.set("{%s}full-path"%MFNS,"Pictures/%s"%odtid)
                            except:
                                logger.exception('source image not found %s'%newsrc)
                        else:
                            odtid = odtids.get(newsrc)
                        # inserts the uuid in the pivot for futher references from xslt
                        img.set('newimgid',odtid)
                        try:
                            # sets the size and def of the image in the pivot for xslt processing
                            im = Image.open(StringIO(self.read(newsrc)))
                            (w,h)=im.size
                            img.set('orig_width',str(w))
                            img.set('orig_height',str(h))
                            try:
                                (dw,dh)=im.info['dpi']
                                img.set('orig_resw',str(dw))
                                img.set('orig_resh',str(dh))
                            except:
                                pass
                        except:
                            pass
                except:
                    logger.exception('could not add media to zip') 
                mmt=mf.xpath('/manifest:manifest/manifest:file-entry[@manifest:full-path]', namespaces={'manifest':MFNS})[0]
                mmt.set('{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}media-type','application/vnd.oasis.opendocument.text')

                # write back the manifest in the produced odt file
                zipout.writestr('META-INF/manifest.xml', bytes=ET.tostring(mf))

                # creates a temporary pivot file (should use an xslt extension for that
                self.xwrite(pivot, tmppivot)
                
                # creates a temporary styles file from the template, TODO : use an xslt extension
                styles = zipin.read('styles.xml')
                self.write(styles,tmpstyles)
                styles = ET.XML(styles)
                

                
                # generates the metadata of the odt file

                tmeta=ET.XML(zipin.read('meta.xml'))
                
                try:
                    xslx=self.get_xsl('generate-meta')
                except:
                    logger.exception('XSL parse error generate-meta odt')
                    raise
                try:
                    logger.debug(tmppivot)
                    doc=xslx(tmeta, pivot="'%s'"%tmppivot)
                except:
                    logger.exception('XSL runtime error generate-meta odt')
                    logger.debug(xslx)
                    for entry in xslx.error_log:
                        logger.debug('message from line %s, col %s: %s' % (entry.line, entry.column, entry.message))

                zipout.writestr('meta.xml', bytes=str(doc))

                xslx = self.get_xsl('generate-styles')
                doc=xslx(styles,
                        pivot="'%s'"%tmppivot)

                for entry in xslx.error_log:
                    print('message from line %s, col %s: %s' % (entry.line, entry.column, entry.message))
                zipout.writestr('styles.xml', bytes=str(doc))

                # generates the content

                template=ET.XML(zipin.read('content.xml'))

                xslx = self.get_xsl('generate')
                content=xslx(template,
                         pivot="'%s'"%tmppivot,
                         styles="'%s'"%tmpstyles,
                         mapping="'%s'"%mapfile)
                for entry in xslx.error_log:
                    print('message from line %s, col %s: %s' % (entry.line, entry.column, entry.message))

                # self.xwrite(pivot, tmpdebug)
                zipout.writestr('content.xml', bytes=str(content))
                zipout.writestr('mimetype', bytes='application/vnd.oasis.opendocument.text')

                # Copy all unhandled files from template to generated doc

                for f in zipin.namelist():
                    if not zipout.namelist().__contains__(f):
                        zipout.writestr(f, bytes=zipin.read(f))
        
        odtfilename = "%s/%s.odt" %(self.publication_plugin_dir, self.publication_file)
        
        # save the generated zip (odt)
        self.write(dfile.getvalue(), odtfilename)

        #removes temporary files
        self.delete_resource(tmppivot)
        self.delete_resource(tmpstyles)

        # output file name
        res.append({'type':"opendocument", "label":"%s_%s"%(self.publication_file,self.scriptname), "url": odtfilename})
        return res



    def _generate_graphics(self):
        self.makedirs(self.publication_plugin_dir+'/img')
        for component in self.pivot.xpath('//h:div[starts-with(@class, "kolekti-component-")][not(@data-hidden)]',
                                      namespaces = self._ns):
            compid = component.get('id', None)
            if compid is None:
                compid = 'id' + str(uuid.uuid1())
                component.set('id',compid)
            
            component_type = component.get('class').replace("kolekti-component-","")

            #            data = topic.xpath('string(.//h:p[@class="kolekti-sparql-result-chartjs"])',namespaces=self._ns)
            try:
                renderer = getattr(self, '_render_%s'%(component_type,))
                graphicfile = self.getOsPath(self.publication_plugin_dir + '/img/component_' + compid + '.png')
                logger.debug('graphic export to %s'%graphicfile)
                try:
                    renderer(component,  graphicfile)
                except:
                    logger.exception("unable to render component %s"%component_type)
            except:
                logger.debug("no renderer for component %s"%component_type)

    def _render_map(self, component, imgpath):
        _, inpath = tempfile.mkstemp(suffix='.html')
        logger.debug('---render map---')
#        logger.debug(ET.tostring(component))
        xsl = self.get_system_xsl('components/render_map')
        staticpath = os.path.join(self._appdir,'..','kolekti_server/kserver/static')
        logger.debug(staticpath)
        domhtml = xsl(component, static = "'%s'"%staticpath)
        if domhtml.xpath('.//h:div[@data-geojson=""] or not(.//h:div[@data-geojson])', namespaces=self._ns):
            logger.debug('json not found')
            return
        
        with open(inpath, 'w') as f:
            f.write('<!DOCTYPE html>\n')
            f.write(ET.tostring(domhtml, method="html", xml_declaration=None, pretty_print=True))
        self._rasterize_phantom("rasterize-map.js", inpath, imgpath)
        os.unlink(inpath)        
    
    def _render_chart(self, component, imgpath):
        _, inpath = tempfile.mkstemp(suffix='.html')
        xsl = self.get_system_xsl('components/render_chart')
        staticpath = os.path.join(self._appdir,'..','kolekti_server/kserver/static')
        domhtml = xsl(component, static = "'%s'"%staticpath)
        with open(inpath, 'w') as f:
            f.write('<!DOCTYPE html>\n')
            f.write(ET.tostring(domhtml, method="html", xml_declaration=None, pretty_print=True))
        self._rasterize_phantom("rasterize-chart.js", inpath, imgpath)
#        os.unlink(inpath)
        

    def _rasterize_phantom(self, script, inpath, imgpath):
        try:
            cmd = ['phantomjs','--disk-cache=true','kserver/static/'+script, inpath, imgpath.encode('utf-8'), "600px"]
            logger.debug(' '.join(cmd))
            exccmd = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True)
            err=exccmd.stderr.read()
            out=exccmd.stdout.read()
            exccmd.communicate()
            err=err.decode(self.LOCAL_ENCODING)
            out=out.decode(self.LOCAL_ENCODING)
            for line in err.split('\n'):
                logger.error(line)
            for line in out.split('\n'):
                logger.info(line)
                
        except:
            logger.exception('error when raterize %s', str(cmd))
            
    def _render_details(self, component, imgpath):
        pass

    def _render_title(self, component, imgpath):
        pass

    def _render_wysiwyg(self, component, imgpath):
        pass
       
    def _generate_Bar(self, data, chartfile):
        bar_chart = pygal.Bar()
        bar_chart.x_labels = data['labels']
        bar_chart.width = 500
        bar_chart.height = 300
        for serie in data['datasets']:
            bar_chart.add(serie['label'], [float(v) for v in serie['data']])
          
        bar_chart.render_to_png(chartfile)

    def _generate_Line(self, data, chartfile):
        line_chart = pygal.Line()
        line_chart.width = 500
        line_chart.height = 300
        line_chart.x_labels = data['labels']
        for serie in data['datasets']:
            line_chart.add(serie['label'], [float(v) for v in serie['data']])
          
        line_chart.render_to_png(chartfile)

    def _generate_none(self, data, chartfile):
        return
