from lxml import etree as ET
import os
import urllib2
import shutil

class XSLExtensions(object):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extension"
    def __init__(self, path):
        self.path = path
        try:
            conf = ET.parse(os.path.join(self.path, 'kolekti', 'settings.xml')).getroot()
            self.config = {
                "sourcelang":conf.get('sourcelang'),
                "version":conf.get('version'),
                "languages":[l.text() for l in conf.xpath('/config/languages/lang')],
                }
        except:
            self.config = {
                "sourcelang":'en',
                "version":"7.0",
                "languages":["en","fr"],
                }
            
class PrefixResolver(ET.Resolver):
    """
    lxml url resolver for kolekti:// url
    """
    def resolve(self, url, pubid, context):
        """Resolves wether it's a kolekti, kolektiapp, or project url scheme"""
        if url.startswith('kolekti://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(conf.get('fmkdir'), *localpath),context)
        if url.startswith('kolektiapp://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(conf.get('appdir'), *localpath),context)
        if url.startswith('project://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(self.model.projectpath, *localpath),context)


objpathes = {
    "0.6":{
        "module" : "modules",
        "trame"  : "trames",
        "publication" : "publication",
        "variables" : "sheets/xml",
        "styles" : "design/publication",
        "orders" : "configuration/orders",
        "profiles" : "configuration/profiles"
        },
    "0.7":{
        "module" : "sources/LANG/pages",
        "trame"  : "sources/LANG/pages",
        "publication" : "publications",
        "variables" : "source/LANG/variable",
        "styles" : "kolekti/stylesheets",
        "orders" : "kolekti/layouts",
        "profiles" : "kolekti/layouts/profiles",
        }
    }
 
    
class kolektiBase(object):
    def __init__(self,path):
        self.__path = path
        self.appdir = os.path.dirname(os.path.realpath( __file__ ))

        self.xmlparser = ET.XMLParser()
        self.xmlparser.resolvers.add(PrefixResolver())

        try:
            conf = ET.parse(os.path.join(path, 'kolekti', 'settings.xml')).getroot()
            projectdir = os.path.basename(path)
            self.config = {
                "sourcelang":conf.get('sourcelang'),
                "version":conf.get('version'),
                "languages":[l.text() for l in conf.xpath('/config/languages/lang')],
                "projectdir":projectdir,
                "project":conf.get('project',projectdir),
                }



        except:
            import traceback
            print traceback.format_exc()
            self.config = {
                "project":"Kolekti",
                "sourcelang":'en',
                "version":"7.0",
                "languages":["en","fr"],
                }
        self.version = self.config['version']
        print "kolekti version",self.version
        
    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts = urllib2.url2pathname(path).split('/')
        #        print self.__path, pathparts
        return os.path.join(self.__path, *pathparts)


    def get_script(self, plugin):
        import plugins
        return plugins.getPlugin(plugin,self.__path)
        



    def get_extensions(self, extclass, **kwargs):
        extensions = {}
        print "get_extensions",extclass,self.__path,kwargs
        extf_obj = extclass(self.__path, **kwargs)
        exts = (n for n in dir(extclass) if not(n.startswith('_')))
        extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))
        return extensions
        

    def get_xsl(self, stylesheet, extclass = None, xsldir = None, **kwargs):
        print "get xsl",stylesheet, extclass , xsldir , kwargs
        if xsldir is None:
            xsldir = self.appdir
        path = os.path.join(xsldir, 'xsl', stylesheet+".xsl")
        xsldoc  = ET.parse(path,self.xmlparser)
        if extclass is None:
            extclass = XSLExtensions
        xsl = ET.XSLT(xsldoc, extensions=self.get_extensions(extclass, **kwargs))
        return xsl

    def parse(self, filename):
        src = self.__makepath(filename)
        return ET.parse(src,self.xmlparser)
    
    def read(self, filename):
        ospath = self.__makepath(filename)
        with open(ospath, "r") as f:
            return f.read()

    def write(self, content, filename):
        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            f.write(content)
            
    def makedirs(self, path):
        ospath = self.__makepath(path)
        os.makedirs(ospath)
        
    def exists(self, path):
        ospath = self.__makepath(path)
        return os.path.exists(ospath)

    def copyFile(self, source, path):
        ossource = self.__makepath(source)
        ospath = self.__makepath(path)
        return shutil.copy(ossource, ospath)

    def copyDirs(self, source, path):
        ossource = self.__makepath(source)
        ospath = self.__makepath(path)
        try:
            shutil.rmtree(ospath)
        except:            
            pass
        return shutil.copytree(ossource, ospath)

    def getOsPath(self, source):
        return self.__makepath(source)

    def getUrlPath(self, source):
        path = self.__makepath(source)
        print 'file://' + '/'.join(os.path.split(path))
        return 'file://' + '/'.join(os.path.split(path))


    def getPathFromUrl(self, url):
        return '/'.join(url.split('/')[3:])
