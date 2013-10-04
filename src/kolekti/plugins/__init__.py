import imp
import os
def getPlugin(plugin, path):
    pm = imp.load_source('kolekti.plugins.'+plugin, os.path.join('kolekti','plugins',plugin+'.py'))
    pl = getattr(pm, "plugin")
    return pl(path)

