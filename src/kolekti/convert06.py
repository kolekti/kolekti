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
print __name__
from kolekti.variables import OdsToXML

class ConvertException(Exception):
    pass
    
class ConvertMixin(object):
    e2 = re.compile(r'_([A-Z]+)_')
    def topic_ref(self, topic06, args):
        topic = topic06.replace('@modules/','')
        topic07 = "/sources/%s/topics/%s"%(args.get('lang'),topic.replace('.xht','.html') )
        return topic07 

    def image_criteria_repl(self, src, criteria):
        def repl(matchobj):
            try:
                return criteria[matchobj.group(1)]
            except KeyError:
                return matchobj.group(0)
        return self.e2.sub(repl, src)
    
    def image_criteria(self, src, profiles):
        m = self.e2.findall(src)
        if len(m)==0:
            yield src
        else:
            for pname, criteria in profiles.iteritems():
                yield self.image_criteria_repl(src, criteria)
        return
                          
class XSLExtensions(ConvertMixin):
    e = re.compile(r'\[var (\w+):(\w+)\]')
    
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('args'):
            self.args = kwargs.get('args')

    def fsname(self, _, *args):
        return unicode(args[0].replace(" ","_"))
    
    def translate(self, _, *args):
        return args[0] 

    def getarg(self, _, *args):
        argname = args[0] 
        try:
            return self.args[argname]
        except:
            return "FIXME"
        
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
            return [titlestr]
        
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

    def img_path(self, _, *args):
        imgpath = self.e2.sub(r'{\1}', args[0])
        pathparts = imgpath.split('/')
        return '/' + '/'.join(['sources', self.args.get('lang'), 'pictures'] + pathparts[4:])
        
    def link_path(self, _, *args):
        linkpath = args[0]
        if linkpath[0] == "#":
            return linkpath
        if linkpath[:7] == "http://" or linkpath[:8] == "https://":
            return linkpath
        logger.debug(linkpath)
        linkpath = linkpath.replace('.xht','.html')
        pathparts = linkpath.split('/')
        return '/' + '/'.join(['sources', self.args.get('lang'), 'topics'] + pathparts[4:])
        
class Converter(ConvertMixin):
    def __init__(self, lang, source_project):
        self.lang = lang
        self.source_project = source_project
        self._appdir = os.path.dirname(os.path.realpath( __file__ ))
        
    
    def get_xsl(self, name, args):
        extclass = XSLExtensions
        exts = [n for n in dir(extclass) if not(n.startswith('_'))]
        extensions = ET.Extension(XSLExtensions(args=args),exts,ns="kolekti:migrate")
        
        return ET.XSLT(ET.parse(os.path.join(self._appdir,'xsl',name)), extensions = extensions)

    def apply_xsl(self, stylesheet,  infile, outfile, args, xsl_args={}, parser=ET.XMLParser()):
        xsrc = ET.parse(infile, parser)
        xsl = self.get_xsl(stylesheet, args)
        try:
            xdst = xsl(xsrc, **xsl_args)
            #ET.tounicode(xsl(toc),pretty_print=True).encode('utf-8')
        except ET.XSLTApplyError:
            for err in xsl.error_log:
                logging.exception(unicode(err).encode('utf-8'))
            
        with open(outfile,'w') as ofile:
            ofile.write(str(xdst))
            
        return xdst
    
    def convert_topic_assets(self, srcfile, args):
        xsrc = ET.parse(srcfile, parser = ET.XMLParser(load_dtd=True))
        for img in xsrc.xpath('//html:img', namespaces={'html':"http://www.w3.org/1999/xhtml"}):
            
#            logger.debug('image %s',img.get('src'))
            for ic in self.image_criteria(img.get('src'), args['profiles']):
                parts = ic.split('/')
                srcimg = args.get('source_project') + '/'.join(parts[3:])
                destimg = args.get('target_project') + 'sources/' + args.get('lang') + '/pictures/' + '/'.join(parts[4:]) 
                self.makedirs(os.path.dirname(destimg))
#                logger.debug("copy " + srcimg + " to " + destimg)
                try:
                    shutil.copy(srcimg, destimg)
                except:
                    logger.exception('could not copy image')
     
                                             
            
            
    def convert_toc_topics(self, toc, args):
        logger.info('Converting topics')
        xsrc = ET.parse(toc)
        for topic in xsrc.xpath('//t:module', namespaces={'t':'kolekti:trames'}):
            topic06 = topic.get('resid')
#            logger.info(topic06)
            if topic06[:8] == 'kolekti:':
                continue

            srcfile = os.path.join(self.source_project, topic06[1:])
            topic07 = self.topic_ref(topic06, args)[1:]
            dstfile = os.path.join(
                args['target_project'],
                topic07
                )
            dstdir = os.path.dirname(dstfile)
            self.makedirs(dstdir)
            self.apply_xsl(
                'topic_06to07.xsl',
                srcfile,
                dstfile,
                args,
                parser = ET.XMLParser(load_dtd=True))
#            logger.debug('topic %s',dstfile)
            self.convert_topic_assets(srcfile, args)
            

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
#            logger.debug(xjob)
            
            for script in xjob.xpath('/job/scripts//script'):
                scriptname = script.get('name')
#                logger.debug(scriptname)
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
#                    logger.debug(paramname)

                    pval = script.xpath('parameters/parameter[@name = "%s"]'%paramname)
                    if len(pval):
                        paramvalue = p.get('dir') + "/" + pval[0].get('value') + "." + p.get('ext')
#                        logger.debug(paramvalue)
                        
                        if not os.path.exists(os.path.join(releasepath, p.get('dir'), paramvalue)):
                            if os.path.exists(os.path.join(project_path, paramvalue)):
                                self.makedirs(os.path.join(releasepath, p.get('dir')))
                                shutil.copy(os.path.join(project_path, paramvalue), os.path.join(releasepath, p.get('dir')))
                                if p.get('ext') == "css":
                                    paramparts = p.get('dir') + "/" + pval[0].get('value') + ".parts"
                                    if os.path.exists(os.path.join(project_path, paramparts)):
                                        shutil.copytree(os.path.join(project_path, paramparts), os.path.join(releasepath,paramparts))
                                        
            for f in  myzip.namelist():
                if f[:7] == "medias/" and f[-1]!= '/':
                    myzip.extract(f, os.path.join(releasepath, 'sources', lang, 'pictures'))
                    newpdir = os.path.dirname(os.path.join(releasepath, 'sources', lang, 'pictures',f[7:]))
                    self.makedirs(newpdir)
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
            self.source_project,
            "modules",
            args.get('topic')
            )
    
        outtopic = os.path.join(
            args.get('target_project'),
            "sources",
            args.get('lang'),
            "topics",
            self.topic_ref(args.get('topic'), args),
            )
        self.apply_xsl('topic_06to07.xsl', intopic, outtopic)
            
    def convert_toc(self, args):        
        intoc = os.path.join(
            self.source_project,
            "trames",
            args['toc'])
        
        self.makedirs(os.path.join(
            args['target_project'],
            "sources",
            args['lang'],
            "tocs"))
            
        outtoc = os.path.join(
            args['target_project'],
            "sources",
            args['lang'],
            "tocs",
            args['toc'].replace('.xml', '.html'),
            )
                        
        self.apply_xsl('toc_06to07.xsl', intoc, outtoc, args)
        if args['recurse']:
            self.convert_toc_topics(intoc, args)
        return outtoc
        
    def convert_job(self, args):        
        injob = os.path.join(
            self.source_project,
            "configuration",
            "orders",
            args['job'] + '.xml')
        
        self.makedirs(os.path.join(
            args['target_project'],
            "kolekti",
            "publication-parameters"))

            
        outjob = os.path.join(
            args['target_project'],
            "kolekti",
            "publication-parameters",
            args['job'] + '.xml'
            )
                        
        self.apply_xsl('job_06to07.xsl', injob, outjob, args)
        
        if args['recurse']:
            xjob = ET.parse(injob)
            profiles = {}
            for p in xjob.xpath('/order/profiles/profile'):
                pname = p.find('label').text
                crits = dict([(c.get('code'),c.get('value')) for c in p.findall('criterias/criteria')])
                profiles.update({pname:crits})
            toc = xjob.xpath("string(/order/trame/@value)")
            args.update({
                'toc':toc[8:],
                'profiles': profiles})
            self.convert_toc(args)
        return outjob
        
