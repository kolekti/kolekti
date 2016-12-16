#!/usr/bin/python
# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os
import re
from lxml import etree as ET
import argparse
import logging
logger = logging.getLogger('convert')
#from kolekti.publish_utils import PublisherExtensions
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

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
        logger.debug(srcref)
        return topic_ref(srcref, self.args)

    def var_section_title(self, _, *args):
        titlestr = args[0]
        r = self.e.match(titlestr)
        logger.debug(titlestr)
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

def apply_xsl(stylesheet, args, infile, outfile):
        xsrc = ET.parse(infile)
        xsl = get_xsl(stylesheet, args)
        try:
            xdst = xsl(xsrc) #ET.tounicode(xsl(toc),pretty_print=True).encode('utf-8')
            with open(outfile,'w') as ofile:
                ofile.write(str(xdst))
                    
        except ET.XSLTApplyError:
            logging.exception(str(xsl.error_log))

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
        apply_xsl('topic_06to07.xsl', args, srcfile, dstfile)
        logger.debug('topic %s',dstfile)
        convert_topic_assets(srcfile)
        

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
                
    apply_xsl('topic_06to07.xsl', args, intopic, outtopic)
            
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
                
        
    apply_xsl('toc_06to07.xsl', args, intoc, outtoc)
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
    
    args = parser.parse_args()

    logger.debug(args)
    
    if args.cmd == 'toc':
        out = cmd_convert_toc(args)
        logger.info('successfully converted toc %s', out)
        
    if args.cmd == 'topic':
        cmd_convert_topic(args)


        
