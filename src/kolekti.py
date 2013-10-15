#!/usr/bin/python
import sys
import os

import argparse
import ConfigParser
import settings
import pysvn
import mimetypes
mimetypes.init()

from kolekti.server.wsgi import wsgiclass



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
    # shall we read the alternate or default config file
    if alternatefile is not None:
        config.read(alternatefile)
    else:
        config.read(os.path.expanduser('~/.kolekti'))
    res={}

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
    args, remaining_argv = metaparser.parse_known_args()
    
    config_sections=['server',
                     'publish',
                     ]
    
    if args.config:
        config = readConfig(config_sections,args.config)
    else:
        config = readConfig(config_sections)
    # read configuration
    parser = argparse.ArgumentParser(parents=[metaparser],description=__doc__)    
    defaults=config.get("kolekti",{})
    print defaults
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
    parser_pub = subparsers.add_parser('publish', help="publish documents")
    parser_pub.add_argument('-l', '--lang', action='store', nargs="*")
    parser_pub.add_argument('jobs', action='store', nargs="+")
    defaults=config.get("publish",{})
    defaults.update({'cmd':'publish'})
    parser_pub.set_defaults(**defaults)
    
    args = parser.parse_args()

    print args
    print '-----'
    if args.cmd == 'server':
        host,port = args.host.split(':')
        from paste import httpserver
        wsgi = wsgiclass(args.base)
        httpserver.serve(wsgi, host, port)
        
    if args.cmd == 'publish':
        from kolekti import publish
        langs = args.lang
        
        if langs is None:
            p = publish.Publisher(args.base)
            print p
            p.publish(args.jobs)
        else:
            for lang in langs:
                p = publish.Publisher(args.base, lang=lang)
                p.publish(args.jobs)

    if args.cmd == 'convert':
        from kolekti import convert
        c = convert.converter(args.base)
        c.convert(args.svnurl,args.svnuser,args.svnpass)
