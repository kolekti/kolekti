#!/usr/bin/python
# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os
from lxml import etree as ET
import argparse
#from kolekti.publish_utils import PublisherExtensions


class XSLExtensions(object):
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('args'):
            self.args = kwargs.get('args')

    def fsname(self, _, *args):
        print unicode(args[0].replace(" ","_"))
        return unicode(args[0].replace(" ","_"))
    
    def translate(self, _, *args):
        return "FIXME "+args[0] 

    def topictranslate(self, _, *args):
        srcref = args[0][0]
        ref = srcref[9:].replace('.xht','.html')
        return "/sources/%s/topics/%s"%(self.args.lang, ref)

def get_xsl(name, args):
    extclass=XSLExtensions
    exts = [n for n in dir(extclass) if not(n.startswith('_'))]
    #    extensions=ET.Extension(PublisherExtensions(args.project, lang=args.lang),exts,ns="kolekti:migrate")
    print exts

    extensions=ET.Extension(XSLExtensions(args=args),exts,ns="kolekti:migrate")
    return ET.XSLT(ET.parse(name),extensions = extensions)

def apply_xsl(stylesheet, args):
        toc = ET.parse(os.path.join(args.project, args.infile))
        xsl = get_xsl(stylesheet, args)
        try:
            newtoc = ET.tounicode(xsl(toc),pretty_print=True).encode('utf-8')
            if args.outfile is not None:
                outfile = args.outfile
            else:
                outfile = "%s/sources/%s/tocs/%s%s"%(
                    args.project,
                    args.lang,
                    os.path.basename(os.path.splitext(args.infile)[0]),
                    args.ext)
                
            with open(outfile,'w') as ofile:
                ofile.write(newtoc)
                    
        except ET.XSLTApplyError:
            sys.stderr.write(str(xsl.error_log))
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('project', help="kolekti 07 target project oath, for searching variables values")
    parser.add_argument('lang', help="language")
    parser.add_argument('infile', help="kolekti 06 file")
    
    parser.add_argument('-o', '--outfile', help="kolekti 07 file path relative to project root", default=None)

    subparsers = parser.add_subparsers(title='object to convert')

    parser_toc = subparsers.add_parser('toc', help="convert trame")
    defaults={'cmd':'toc', 'ext':'.html'}
    parser_toc.set_defaults(**defaults)
    

    parser_topic = subparsers.add_parser('topic', help="convert topic")
    defaults={'cmd':'topic', 'ext':'.html'}
    parser_topic.set_defaults(**defaults)
    
    
    args = parser.parse_args()
    print args
    if args.cmd == 'toc':
        apply_xsl('toc_06to07.xsl',args)

    if args.cmd == 'topic':
        apply_xsl('topic_06to07.xsl',args)

        
