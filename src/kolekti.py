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



        
    if args.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.debug('debug')
    else:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
        
    if args.config:
        config = readConfig(config_sections,args.config)
    else:
        config = readConfig(config_sections)

    # read configuration
    parser = argparse.ArgumentParser(parents=[metaparser],description=__doc__)    
    defaults=config.get("kolekti",{})
    
    parser.set_defaults(**defaults)
    
    parser.add_argument('-b','--base', action='store',help="kolekti base path")
    subparsers = parser.add_subparsers(title='kolekti commands')

    # http server 
    # parser_s = subparsers.add_parser('runserver', help="start kolekti server")
    # parser_s.add_argument('host', action='store', default="127.0.0.1:8088",nargs='?')
    # defaults=config.get("server",{})
    # defaults.update({'cmd':'server'})
    # parser_s.set_defaults(**defaults)

    # draft generation
    parser_draft = subparsers.add_parser('draft', help="assemble, filter and produce draft documents")
    parser_draft.add_argument('toc', action='store')
    # parser_draft.add_argument('job', action='store')
    parser_draft.add_argument('-l', '--lang', action='store')
    defaults=config.get("draft",{})
    defaults.update({'cmd':'draft'})
    parser_draft.set_defaults(**defaults)
    
    # release generation
    parser_release = subparsers.add_parser('release', help="create release document")
    parser_release.add_argument('toc', action='store')
    parser_release.add_argument('job', action='store')
    # parser_release.add_argument('release', action='store')
    defaults=config.get("release",{})
    defaults.update({'cmd':'release'})
    parser_release.set_defaults(**defaults)
    

    # publication d'une release 
    parser_pub = subparsers.add_parser('publish', help="publish release document")
    parser_pub.add_argument('release', action='store')
    parser_pub.add_argument('assembly', action='store')
    parser_pub.add_argument('-l', '--lang', action='store')
    defaults=config.get("publish",{})
    defaults.update({'cmd':'publish'})
    parser_pub.set_defaults(**defaults)
    
    # variables file conversion xml->ods 
    parser_varods = subparsers.add_parser('varods', help="convert variables from xml to ods")
    parser_varods.add_argument('varfile', action='store')
    parser_varods.add_argument('-l','--lines', help="produces lines-oriented ods", action = 'store_false' )
    defaults=config.get("varods",{})
    defaults.update({'cmd':'varods'})
    parser_varods.set_defaults(**defaults)
    
    # variables file conversion ods->xml 
    parser_varxml = subparsers.add_parser('varxml', help="convert variables from ods to xml")
    parser_varxml.add_argument('varfile', action='store')
    parser_varxml.add_argument('-l','--lines', help="produces lines-oriented ods", action = 'store_false' )
    defaults=config.get("varxml",{})
    defaults.update({'cmd':'varxml'})
    parser_varxml.set_defaults(**defaults)
    
    # build search index  
    parser_idx = subparsers.add_parser('index', help="(re)build search index")
    defaults=config.get("index",{})
    defaults.update({'cmd':'index'})
    parser_idx.set_defaults(**defaults)
    
    # search query  
    parser_search = subparsers.add_parser('search', help="search query")
    parser_search.add_argument('query', action='store')
    defaults=config.get("search",{})
    defaults.update({'cmd':'search'})
    parser_search.set_defaults(**defaults)
    
    # svn synchro  
    parser_sync = subparsers.add_parser('sync', help="synchronize project")
    subparsers_sync = parser_sync.add_subparsers(title='synchro commands')

    # status
    parser_sync_status = subparsers_sync.add_parser('status', help="get synchro status")
    parser_sync_status.set_defaults(cmdsync='status')
    parser_sync_update = subparsers_sync.add_parser('update', help="get synchro status")
    parser_sync_update.set_defaults(cmdsync='update')

        #parser_sync_status.add_argument('synccmd', action='store')

    defaults=config.get("sync",{})
    defaults.update({'cmd':'sync'})
    parser_sync.set_defaults(**defaults)
 
    args = parser.parse_args()

    
    
    # if args.cmd == 'server':
    #    host,port = args.host.split(':')
    #    from kolekti.server.wsgi import wsgiclass
    #    from paste import httpserver
    #    wsgi = wsgiclass(args.base)
    #    httpserver.serve(wsgi, host, port)
        
    if args.cmd == 'draft':
        from kolekti import publish
        try:
            p = publish.DraftPublisher(args.base, lang=args.lang)
            toc = p.get_base_toc(args.toc) + ".html"
            jobs = [p.get_base_job(args.job) + ".xml"]
            p.publish_draft(toc, jobs)
            logging.info("Publication sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Publication ended with errors")

    if args.cmd == 'release':
        from kolekti import publish
        try:
            p = publish.Releaser(args.base)
            toc = p.get_base_toc(args.toc) + ".html"
            jobs = [p.get_base_job(args.job) + ".xml"]
            p.make_release(toc, jobs)
            logging.info("Release sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Release ended with errors")
                    
    if args.cmd == 'publish':
        from kolekti import publish
        try:
            p = publish.ReleasePublisher(args.base, lang=args.lang)
            p.publish_assembly(args.release, args.assembly)
            logging.info("Publication sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Publication ended with errors")
            
    if args.cmd == 'varods':
        from kolekti import variables
        c = variables.XMLToOds(args.base)
        c.convert(args.varfile)

    if args.cmd == 'varxml':
        from kolekti import variables
        c = variables.OdsToXML(args.base)
        c.convert(args.varfile)


    if args.cmd == 'index':
        from kolekti import searchindex
        ix = searchindex.indexer(args.base)
        ix.indexbase()

    if args.cmd == 'search':
        from kolekti import searchindex
        ix = searchindex.searcher(args.base)
        for res in ix.search(args.query):
            print res

    if args.cmd == 'sync':
        from kolekti import synchro
        sync = synchro.synchro(args.base)
        if args.cmdsync == "status":
            changes = sync.statuses()
            for s,l in changes.iteritems():
                print s,len(l)
                for item in l:
                    logging.debug(item)
            
            # print 'files to be added:'
            # print changes['added']
            # print 'files to be removed:'
            # print changes['removed']
            # print 'files that have changed:'
            # print changes['changed']
            # print 'files with merge conflicts:'
            # print changes['conflict']
            # print 'unversioned files:'
            # print changes['unversioned']

        if args.cmdsync == "update":
            updates = sync.update()
            print updates
