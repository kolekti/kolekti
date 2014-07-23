#!/usr/bin/python
# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os

import argparse
import ConfigParser
import settings
#import pysvn

import logging


import mimetypes
mimetypes.init()


def readConfig(cmds = None, alternatefile = None):
    """Read the kolekti config file.
    
    Keywords arguments:
    appspec -- application name(s) to read config sections from
    alternatefile -- a alternative config file to ~/.kolekti

    Returns:
    A dictionnary containing the config and additional config values
    from appspec

    """
    
    config = ConfigParser.SafeConfigParser()
    res={}

    # shall we read the alternate or default config file
    try:
        if alternatefile is not None:
            config.read(alternatefile)
        else:
            config.read(os.path.expanduser('~/.kolekti'))
    except:
        logging.info("No config file, using default parameters")

    try:
        res.update({'kolekti':dict(config.items("kolekti"))})
    except ConfigParser.NoSectionError:
        res.update({'kolekti':{}})

    # add additional config sections
    for cmd in cmds:
        try:
            res.update({cmd:dict(config.items(cmd))})
        except ConfigParser.NoSectionError:
            res.update({cmd:{}})
    return res



if __name__ == '__main__':
    
    metaparser = argparse.ArgumentParser(add_help=False)
    metaparser.add_argument('-C','--config', help="alternative config file", metavar="FILE")
    metaparser.add_argument('-v','--verbose', help="display verbose ouput", action = 'store_true' )
    args, remaining_argv = metaparser.parse_known_args()
    
    config_sections=['server',
                     'publish',
                     ]
    
    if args.config:
        config = readConfig(config_sections,args.config)
    else:
        config = readConfig(config_sections)

    if args.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        
    # read configuration
    parser = argparse.ArgumentParser(parents=[metaparser],description=__doc__)    
    defaults=config.get("kolekti",{})
    
#    print defaults
    parser.set_defaults(**defaults)
    
    parser.add_argument('-b','--base', action='store',help="kolekti base path")
    subparsers = parser.add_subparsers(title='kolekti commands')

    # http server 
    parser_s = subparsers.add_parser('runserver', help="start kolekti server")
    parser_s.add_argument('host', action='store', default="127.0.0.1:8088",nargs='?')
    defaults=config.get("server",{})
    defaults.update({'cmd':'server'})
    parser_s.set_defaults(**defaults)

    # publication
    parser_pub = subparsers.add_parser('publish', help="assemble, filter and publish documents")
    parser_pub.add_argument('toc', action='store')
    parser_pub.add_argument('job', action='store')
    parser_pub.add_argument('-l', '--lang', action='store', nargs="+")
    defaults=config.get("publish",{})
    defaults.update({'cmd':'publish'})
    parser_pub.set_defaults(**defaults)
    

    # re-publication 
    parser_pub = subparsers.add_parser('republish', help="publish documents from assembly")
    parser_pub.add_argument('assembly', action='store')
    defaults=config.get("republish",{})
    defaults.update({'cmd':'republish'})
    parser_pub.set_defaults(**defaults)
    
    args = parser.parse_args()

    #print args

    if args.cmd == 'server':
        host,port = args.host.split(':')
        from kolekti.server.wsgi import wsgiclass
        from paste import httpserver
        wsgi = wsgiclass(args.base)
        httpserver.serve(wsgi, host, port)
        
    if args.cmd == 'publish':
        from kolekti import publish
        langs = args.lang
        try:
            if langs is None:
                p = publish.Publisher(args.base)
                p.publish_toc(args.toc, [args.job])
            else:
                for lang in langs:
                    p = publish.Publisher(args.base, lang=lang)
                    p.publish_toc(args.toc, [args.job])
            logging.info("Publication sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Publication ended with errors")
            
    if args.cmd == 'republish':
        from kolekti import publish
        try:
            p = publish.Publisher(args.base)
            p.publish_assembly(args.assembly)
            logging.info("Republication sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Republication ended with errors")
            
    if args.cmd == 'convert':
        from kolekti import convert
        c = convert.converter(args.base)
        c.convert(args.svnurl,args.svnuser,args.svnpass)
