#!/usr/bin/python
# -*- coding: utf-8 -*-
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os
import re
from lxml import etree as ET
import argparse
from zipfile import ZipFile
import logging
import shutil

logger = logging.getLogger(__name__)

from kolekti.variables import OdsToXML

class ConvertException(Exception):
    pass
    
class ConvertMixin(object):
    def topic_ref(self, topic06, args):
        topic = topic06.replace('@modules/','')
        topic07 = "/sources/%s/topics/%s"%(args.lang,topic.replace('.xht','.html') )
        return topic07 


class XSLExtensions(ConvertMixin):
    e = re.compile(r'\[var (\w+):(\w+)\]')

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('args'):
            self.args = kwargs.get('args')

    def fsname(self, _, *args):
        return unicode(args[0].replace(" ","_"))
    
    def translate(self, _, *args):
        return "FIXME "+args[0] 

    def topictranslate(self, _, *args):
        srcref = args[0][0]
        return self.topic_ref(srcref, self.args)
 
    def var_section_title(self, _, *args):
        titlestr = args[0]
        r = self.e.match(titlestr)
        if r:
            var = ET.Element('{http://www.w3.org/1999/xhtml}var')
            var.set("class",':'.join(r.groups()))
            return [var]
        else:
            return 'FIXME ' + titlestr
        
    def translate_jobstring(self, _, *args):
        thestr = args[0][0]
        crits  = args[1][0]
        critlist = crits.xpath('.//criteria/@code')
        for crit in critlist:
            e = re.compile(r'_%s_'%crit)
            thestr = re.sub(e, '{%s}'%crit, thestr)

        thestr = re.sub(self.e, r'{\1:\2}', thestr)
            
        return thestr

    def translate_variable(self, _, *args):
        thestr = args[0][0]
        critlist = self.args['config'].xpath('/data/profiles/profile/criterias/criteria/@code')
        for crit in set(critlist):
            e = re.compile(r'_%s_'%crit)
            thestr = re.sub(e, r'{%s}'%crit, thestr)
        return thestr
        
    def var_string(self, _, *args):
        titlestr = args[0]
        r = self.e.match(titlestr)
        if r:
            var = ET.Element('{http://www.w3.org/1999/xhtml}var')
            var.set("class",':'.join(r.groups()))
            return [var]
        else:
            return 'FIXME ' + titlestr

class Converter(ConvertMixin):
    def __init__(self, lang, source_project):
        self.lang = lang
        self.source_project = source_project
        self._appdir = os.path.dirname(os.path.realpath( __file__ ))
        
    
    def get_xsl(self, name, args):
        extclass = XSLExtensions
        exts = [n for n in dir(extclass) if not(n.startswith('_'))]
        extensions = ET.Extension(XSLExtensions(args=args),exts,ns="kolekti:migrate")
        logger.debug(self._appdir)
        
        return ET.XSLT(ET.parse(os.path.join(self._appdir,'xsl',name)), extensions = extensions)

    def apply_xsl(self, stylesheet,  infile, outfile, args, xsl_args={}, parser=ET.XMLParser()):
        xsrc = ET.parse(infile, parser)
        xsl = self.get_xsl(stylesheet, args)
        try:
            xdst = xsl(xsrc, **xsl_args)
            #ET.tounicode(xsl(toc),pretty_print=True).encode('utf-8')
        except ET.XSLTApplyError:
            logging.exception(str(xsl.error_log))
            
        with open(outfile,'w') as ofile:
            ofile.write(str(xdst))
            
        return xdst

    def convert_topic_assets(self, srcfile):
        xsrc = ET.parse(srcfile)
        for img in xsrc.xpath('//html:img', namespaces={'html':"http://www.w3.org/1999/xhtml"}):
            logger.debug('image %s',img.get('src'))
    
    def convert_toc_topics(self, toc, args):
        logger.debug('Converting topics')
        xsrc = ET.parse(toc)
        for topic in xsrc.xpath('//t:module', namespaces={'t':'kolekti:trames'}):
            topic06 = topic.get('resid')
            srcfile = os.path.join(args.source_project, topic06[1:])
            topic07 = self.topic_ref(topic06, args)[1:]
            dstfile = os.path.join(
                args.target_project,
                topic07
                )
            self.apply_xsl('topic_06to07.xsl',  srcfile, dstfile, args)
            logger.debug('topic %s',dstfile)
            self.convert_topic_assets(srcfile)
        

    def makedirs(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        
    def convert_enveloppe(self, args, release_parent_dir = "releases"):
        inenv = args.get('enveloppe')
        with ZipFile(inenv, 'r') as myzip:
            config = myzip.open('config/config.xml')
            xconfig = ET.parse(config)
            config = myzip.open('config/config.xml')
            assembly = myzip.open('assembly.xhtml')
            lang = myzip.read('lang').strip()
            
            args.update({'config':xconfig})
        
            releasename = xconfig.xpath("string(/data/field[@name='mastername']/@value)")
            releasepath = os.path.join(
                args.get('target_project'),
                release_parent_dir,
                releasename)
            project_path = args.get('target_project')
            print releasepath
    
            self.makedirs(os.path.join(releasepath, 'kolekti', 'publication-parameters'))
            self.makedirs(os.path.join(releasepath, 'kolekti', 'publication-templates'))
            self.makedirs(os.path.join(releasepath, 'sources', lang, 'assembly'))
            self.makedirs(os.path.join(releasepath, 'sources', lang, 'pictures'))
            self.makedirs(os.path.join(releasepath, 'sources', lang, 'variables','ods'))
            self.makedirs(os.path.join(releasepath, 'sources', 'share'))
        
            self.apply_xsl(
                'assembly_06to07.xsl',
                assembly,
                os.path.join(releasepath, 'sources', lang, 'assembly', releasename + '_asm.html'),
                args,
                xsl_args={'lang': "'%s'"%lang},
                parser = ET.HTMLParser()
                )
        
            xjob = self.apply_xsl(
                'env_job_06to07.xsl',
                config,
                os.path.join(releasepath, 'kolekti', 'publication-parameters', releasename + '_asm.xml'),
                args
                )
            
            scriptsdef = ET.parse(os.path.join(self._appdir, 'pubscripts.xml'))
            logger.debug(xjob)
            
            for script in xjob.xpath('/job/scripts//script'):
                scriptname = script.get('name')
                logger.debug(scriptname)
                scriptdef = scriptsdef.xpath('/scripts/pubscript[@id="%s"]'%scriptname)
                if len(scriptdef) == 0:
                    continue
                for p in scriptdef[0].xpath('parameters/parameter[@type="resource"]'):
                    paramname = p.get('name')
                    paramvalue = p.get('dir') + "/" + p.get('file') + "." + p.get('ext')
                    if not os.path.exists(os.path.join(releasepath, p.get('dir'), paramvalue)):
                        if os.path.exists(os.path.join(project_path, paramvalue)):
                            self.makedirs(os.path.join(releasepath, p.get('dir')))
                            shutil.copy(os.path.join(project_path, paramvalue), os.path.join(releasepath, p.get('dir')))
                        else:
                            if not p.get('onfail') == 'silent':
                                raise ConvertException('Cannot not copy resource %s'%paramvalue)
                        
                for p in scriptdef[0].xpath('parameters/parameter[@type="filelist"]'):
                    paramname = p.get('name')
                    logger.debug(paramname)

                    pval = script.xpath('parameters/parameter[@name = "%s"]'%paramname)
                    if len(pval):
                        paramvalue = p.get('dir') + "/" + pval[0].get('value') + "." + p.get('ext')
                        logger.debug(paramvalue)
                        
                        if not os.path.exists(os.path.join(releasepath, p.get('dir'), paramvalue)):
                            if os.path.exists(os.path.join(project_path, paramvalue)):
                                self.makedirs(os.path.join(releasepath, p.get('dir')))
                                shutil.copy(os.path.join(project_path, paramvalue), os.path.join(releasepath, p.get('dir')))
                                if p.get('ext') == "css":
                                    paramparts = p.get('dir') + "/" + pval[0].get('value') + ".parts" 
                                    shutil.copytree(os.path.join(project_path, paramparts), os.path.join(releasepath,paramparts))                              
                            
            for f in  myzip.namelist():
                if f[:7] == "medias/" and f[-1]!= '/':
                    myzip.extract(f, os.path.join(releasepath, 'sources', lang, 'pictures'))
                    newpdir = os.path.dirname(os.path.join(releasepath, 'sources', lang, 'pictures',f[7:]))
                    if not os.path.exists(newpdir):
                        os.makedirs(newpdir)
                    shutil.move(
                        os.path.join(releasepath, 'sources', lang, 'pictures',f),
                        os.path.join(releasepath, 'sources', lang, 'pictures',f[7:])
                        )
                if f[:7] == "sheets/" and f[-1]!= '/':
                    ods_file = f.split('/')[-1]
                    ods_path = os.path.join(releasepath, 'sources', lang, 'variables', 'ods')
                    xml_path = '/' + '/'.join([release_parent_dir, releasename, 'sources', lang, 'variables', ods_file.replace('.ods', '.xml')])
                    myzip.extract(f, ods_path)
                    converter = OdsToXML(project_path)
                    converter.convert(os.path.join(ods_path, f), xml_path, sync = False)
        return releasename
        
        
    def convert_topic(self, args):
        intopic = os.path.join(
            args.source_project,
            "modules",
            args.topic
            )
    
        outtopic = os.path.join(
            args.target_project,
            "sources",
            args.lang,
            "topics",
            self.topic_ref(args.topic, args),
            )
        self.apply_xsl('topic_06to07.xsl', intopic, outtopic, args)
            
    def convert_toc(self, args):
        intoc = os.path.join(
            args.source_project,
            "trames",
            args.toc)

        outtoc = os.path.join(
            args.target_project,
            "sources",
            args.lang,
            "tocs",
            args.toc,
            )
                        
        self.apply_xsl('toc_06to07.xsl', intoc, outtoc, args)
        if args.recurse:
            self.convert_toc_topics(intoc, args)
        return outtoc
        
