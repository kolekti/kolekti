#import imp
#import os
#import sys
#import logging

import pluginBase
import WebHelp5
import filterpivot
import serializepdf

#def getPlugin(plugin, path):
#    logging.debug('plugin import %s'%plugin)
#    d = os.path.dirname(__file__)
#    pm = imp.load_source('kolekti.plugins.'+plugin, os.path.join(d,plugin+'.py'))
#    pl = getattr(pm, "plugin")
#    return pl(path)

