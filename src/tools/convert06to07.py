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
import shutil
logger = logging.getLogger('kolekti.convert06')
#from kolekti.publish_utils import PublisherExtensions
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

try:
    from kolekti import convert06
except ImportError:
    print "ERROR : Unable to find kolekti sources, set your PYTHONPATH varible to kolekti src path"
    sys.exit(1)
    
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)


logger.addHandler(ch)
               
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('source_project', help="kolekti 06 source project path")
    parser.add_argument('target_project', help="kolekti 07 target project path")
    parser.add_argument('lang', help="kolekti 07 language")
    
    subparsers = parser.add_subparsers(title='object to convert')

    parser_job = subparsers.add_parser('job', help="convert job")
    
    defaults={'cmd':'job', 'ext':'.xml'}
    
    parser_job.set_defaults(**defaults)
    parser_job.add_argument('job', help="kolekti 06 orders to convert")
    parser_job.add_argument('-r', '--recurse', action='store_true', help="Recusrse into tocs/topics")    

    
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
    
    converter = convert06.Converter(args.lang, args.source_project)
    
    if args.cmd == 'job':
        out = converter.convert_job(args.__dict__)
        logger.info('successfully converted job %s', out)
        
    if args.cmd == 'toc':
        out = converter.convert_toc(args.__dict__)
        logger.info('successfully converted toc %s', out)
        
    if args.cmd == 'topic':
        converter.convert_topic(args.__dict__)
        
    if args.cmd == 'enveloppe':
        converter.convert_enveloppe(args.__dict__)


        
