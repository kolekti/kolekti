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
logger = logging.getLogger('convert')
#from kolekti.publish_utils import PublisherExtensions
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

try:
    from kolekti import convert06
except ImportError:
    print "ERROR : Unable to find kolekti sources, set your PYTHONPATH varible to kolekti src path"
    sys.exit(1)
    
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)


logger.addHandler(ch)

class XSLExtensions(object):
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
        return topic_ref(srcref, self.args)
 
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

       
def topic_ref(topic06, args):
    topic = topic06.replace('@modules/','')
    topic07 = "/sources/%s/topics/%s"%(args.lang,topic.replace('.xht','.html') )
    return topic07 
    
def get_xsl(name, args):
    extclass=XSLExtensions
    exts = [n for n in dir(extclass) if not(n.startswith('_'))]
    #    extensions=ET.Extension(PublisherExtensions(args.project, lang=args.lang),exts,ns="kolekti:migrate")

    extensions=ET.Extension(XSLExtensions(args=args),exts,ns="kolekti:migrate")
    return ET.XSLT(ET.parse(name),extensions = extensions)

def apply_xsl(stylesheet,  infile, outfile, args, xsl_args={}, parser=ET.XMLParser() ):
        xsrc = ET.parse(infile, parser)
        xsl = get_xsl(stylesheet, args)
        try:
            xdst = xsl(xsrc, **xsl_args) #ET.tounicode(xsl(toc),pretty_print=True).encode('utf-8')
    #                    
        except ET.XSLTApplyError:
            logging.exception(str(xsl.error_log))

        
        with open(outfile,'w') as ofile:
            ofile.write(str(xdst))
            
        #       xdst.write(outfile)

        return xdst

def convert_topic_assets(srcfile):
    xsrc = ET.parse(srcfile)
    for img in xsrc.xpath('//html:img', namespaces={'html':"http://www.w3.org/1999/xhtml"}):
        logger.debug('image %s',img.get('src'))
    
def convert_toc_topics(toc, args):
    logger.debug('Converting topics')
    xsrc = ET.parse(toc)
    for topic in xsrc.xpath('//t:module', namespaces={'t':'kolekti:trames'}):
        topic06 = topic.get('resid')
        srcfile = os.path.join(args.source_project, topic06[1:])
        topic07 = topic_ref(topic06, args)[1:]
        dstfile = os.path.join(
            args.target_project,
            topic07
            )
        apply_xsl('topic_06to07.xsl',  srcfile, dstfile, args)
        logger.debug('topic %s',dstfile)
        convert_topic_assets(srcfile)
        

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def cmd_convert_enveloppe(args):
    inenv = args.enveloppe
    with ZipFile(inenv, 'r') as myzip:
        config = myzip.open('config/config.xml')
        xconfig = ET.parse(config)
        config = myzip.open('config/config.xml')
        assembly = myzip.open('assembly.xhtml')
        lang = myzip.read('lang').strip()
        dargs = args.__dict__

        dargs.update({'config':xconfig})
        
        releasename = xconfig.xpath("string(/data/field[@name='mastername']/@value)")
        releasepath = os.path.join(
            args.target_project,
            "releases",
            releasename)
        print releasepath
    
        makedirs(os.path.join(releasepath, 'kolekti', 'publication-parameters'))
        makedirs(os.path.join(releasepath, 'kolekti', 'publication-templates'))
        makedirs(os.path.join(releasepath, 'sources', lang, 'assembly'))
        makedirs(os.path.join(releasepath, 'sources', lang, 'pictures'))
        makedirs(os.path.join(releasepath, 'sources', lang, 'variables','ods'))
        makedirs(os.path.join(releasepath, 'sources', 'share'))
        
        apply_xsl(
            'assembly_06to07.xsl',
            assembly,
            os.path.join(releasepath, 'sources', lang, 'assembly', releasename + '_asm.html'),
            dargs,
            xsl_args={'lang': "'%s'"%lang},
            parser = ET.HTMLParser()
            )
        
        apply_xsl(
            'env_job_06to07.xsl',
            config,
            os.path.join(releasepath, 'kolekti', 'publication-parameters', releasename + '_asm.xml'),
            args
            )

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
                myzip.extract(f, os.path.join(releasepath, 'sources', lang, 'variables', 'ods'))

        
    
def cmd_convert_topic(args):
    intopic = os.path.join(
        args.source_project,
        "modules",
        args.topic)
    
    outtopic = os.path.join(
        args.target_project,
        "sources",
        args.lang,
        "topics",
        topic_ref(args.topic, args)
    )            
                
    apply_xsl('topic_06to07.xsl', intopic, outtopic, args)
            
def cmd_convert_toc(args):
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
                
        
    apply_xsl('toc_06to07.xsl', intoc, outtoc, args)
    if args.recurse:
        convert_toc_topics(intoc, args)
    return outtoc
        
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('source_project', help="kolekti 06 source project path")
    parser.add_argument('target_project', help="kolekti 07 target project path")
    parser.add_argument('lang', help="kolekti 07 language")
    
    subparsers = parser.add_subparsers(title='object to convert')

    parser_toc = subparsers.add_parser('toc', help="convert trame")
    
    defaults={'cmd':'toc', 'ext':'.html'}
    
    parser_toc.set_defaults(**defaults)
    parser_toc.add_argument('toc', help="kolekti 06 toc to convert")
    parser_toc.add_argument('-r', '--recurse', action='store_true', help="Recusrse into topics")    

    parser_topic = subparsers.add_parser('topic', help="convert topic")
    parser_topic.add_argument('topic', help="kolekti 06 topic to convert")
    
    defaults={'cmd':'topic', 'ext':'.html'}
    parser_topic.set_defaults(**defaults)
    
    parser_env = subparsers.add_parser('enveloppe', help="convert enveloppe to release")
    parser_env.add_argument('enveloppe', help="kolekti 06 enveloppe to convert")
    
    defaults={'cmd':'enveloppe'}
    parser_env.set_defaults(**defaults)
    
    args = parser.parse_args()

    if args.cmd == 'toc':
        converter = convert06.converter(args.lang, args.source_project)
        out = converter.convert_toc(args)
        logger.info('successfully converted toc %s', out)
        
    if args.cmd == 'topic':
        converter = convert06.converter(args.lang, args.source_project)
        converter.convert_topic(args)
        
    if args.cmd == 'enveloppe':
        converter = convert06.converter(args.lang, args.source_project)
        converter.convert_enveloppe(args)


        
