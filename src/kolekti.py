#!/usr/bin/python
# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os

import argparse

from kolekti.settings import settings
#import pysvn

import logging


import mimetypes
mimetypes.init()




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
        config = settings(args.config)
    else:
        config = settings()

        
    # read configuration
    parser = argparse.ArgumentParser(parents=[metaparser],description=__doc__)    
    defaults=config.get("InstallSettings",{})
    
    parser.set_defaults(**defaults)
    
    parser.add_argument('-b','--base', action='store',help="kolekti base path")
    subparsers = parser.add_subparsers(title='kolekti commands')

    # http server 
    # parser_s = subparsers.add_parser('runserver', help="start kolekti server")
    # parser_s.add_argument('host', action='store', default="127.0.0.1:8088",nargs='?')
    # defaults=config.get("server",{})
    # defaults.update({'cmd':'server'})
    # parser_s.set_defaults(**defaults)

    # publish
    parser_draft = subparsers.add_parser('publish', help="assemble, filter and produce documents")
    parser_draft.add_argument('toc', action='store', help="Toc to be published")
    parser_draft.add_argument('-j', '--job', action='store', help="Job to be used, overrides the job associated with the toc")
    parser_draft.add_argument('-l', '--languages', required=True, action='store', help="comma-separated list of languages to publish")
    defaults=config.get("publish",{})
    defaults.update({'cmd':'publish'})
    parser_draft.set_defaults(**defaults)
    
    # release generation
    parser_release = subparsers.add_parser('make_release', help="create a release")
    parser_release.add_argument('toc', action='store', help="Toc source of the release")
    parser_release.add_argument('name', action='store', help="Name of the release")
    parser_release.add_argument('-l', '--lang', action='store', help="language of sources" )
    parser_release.add_argument('-j', '--job', action='store', help="Job to be used, overrides the job associated with the toc")
    # parser_release.add_argument('release', action='store')
    defaults=config.get("make_release",{})
    defaults.update({'cmd':'make_release'})
    parser_release.set_defaults(**defaults)
    

    # publication d'une release 
    parser_pub = subparsers.add_parser('publish_release', help="publish a release")
    parser_pub.add_argument('name', action='store', help="the release name")
#    parser_pub.add_argument('assembly', action='store')
    parser_pub.add_argument('-l', '--languages', action='store', help="comma-separated list of languages to publish")
    defaults=config.get("publish_release",{})
    defaults.update({'cmd':'publish_release'})
    parser_pub.set_defaults(**defaults)
    
    # perform diagnostics
    parser_diag = subparsers.add_parser('diagnostic', help="diagnostic on project or toc")
    parser_diag.add_argument('-t', '--toc', action='store')
    parser_diag.add_argument('-l', '--lang', action='store')
    defaults=config.get("diagnostic",{})
    defaults.update({'cmd':'diagnostic'})
    parser_diag.set_defaults(**defaults)
    
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
        
    if args.cmd == 'publish':
        from kolekti import publish
        try:
            langs = args.languages.split(',')
            for lang in langs:
                p = publish.DraftPublisher(args.base, lang = lang)
                toc = p.parse(p.substitute_criteria(args.toc, profile = None))
                if args.job:
                    job = args.job
                else:
                    tocjob = toc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
                    job = "/kolekti/publication-parameters/"+tocjob+'.xml'
                xjob = p.parse(job)
                pubdir = toc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.pubdir"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
                print pubdir
                xjob.getroot().set('pubdir',pubdir)
                                   
                for event in p.publish_draft(toc, xjob):
                    if event['event'] == "job":
                        logging.info('Publishing Job %s'%event['label'])
                    if event['event'] == "profile":
                        logging.info(' profile %s'%event['label'])
                    if event['event'] == "result":
                        logging.info('%s complete'%event['script'])
                        for doc in event['docs']:
                            logging.info('[%s] %s'%(doc['type'],doc['url']))

                    if event['event'] == "error":
                        logging.info(' [E] %s\n%s'%(event['msg'], event['stacktrace']) )
                    if event['event'] == "warning":
                        logging.warning(' [W] %s'%(event['msg'],) )
                        logging.debug(' [W] %s'%(event['stacktrace'],) )
            logging.info("Publication complete")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Publication ended with errors")

    if args.cmd == 'make_release':
        from kolekti import publish
        try:
            p = publish.Releaser(args.base, lang=args.lang)
            toc = p.parse(args.toc)
            if args.job:
                job = args.job
            else:
                tocjob = toc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
                job = "/kolekti/publication-parameters/"+tocjob+'.xml'
            xjob = p.parse(job)
            xjob.getroot().set('pubdir',args.name)
            p.make_release(toc, xjob, release_name=args.name)
            logging.info("Release sucessful")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Release ended with errors")
                    
    if args.cmd == 'publish_release':
        from kolekti import publish
        try:
            release = '/releases/' + args.name
            p = publish.ReleasePublisher(release, args.base, langs = args.languages.split(','))

            for event in p.publish_assembly(args.name + "_asm"):
                if event['event'] == "job":
                    logging.info('Publishing Job %s'%event['label'])
                if event['event'] == "profile":
                    logging.info(' profile %s'%event['label'])
                if event['event'] == "result":
                    logging.info('%s complete'%event['script'])
                    for doc in event['docs']:
                        logging.info('[%s] %s'%(doc['type'],doc['url']))

                if event['event'] == "error":
                    logging.info(' [E] %s\n%s'%(event['msg'], event['stacktrace']) )
                if event['event'] == "warning":
                    logging.info(' [W] %s\n%s'%(msg) )

            logging.info("Publication complete")
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Publication ended with errors")
            
    if args.cmd == 'diagnostic':
        from kolekti import diagnostic
        try:
            d = diagnostic.Diagnostic(args.base)
            if args.toc:
                d.diag_toc(args.toc)
            else:
                d.diag_project()
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Diagnostics failed")
                    
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
        sync = synchro.SynchroManager(args.base)
        if args.cmdsync == "status":
            changes = sync.statuses()
            for s,l in changes.iteritems():
                print s,len(l)
                
#                for item in l:
#                    logging.debug("%s : %s"%(item['path'],item['rstatus']))
                                           
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
