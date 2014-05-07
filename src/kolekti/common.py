from lxml import etree as ET
import os
import re
import urllib2
import urllib
import urlparse
import shutil


objpathes = {
    "0.6":{
        "modules" : "modules",
        "trames"  : "trames",
        "sources"  : "",
        "publications" : "publication",
        "variables" : "sheets/xml",
        "layouts" : "design/publication",
        "jobs" : "configuration/orders",
        "profiles" : "configuration/profiles"
        },
    "0.7":{
        "modules" : "sources/{LANG}",
        "trames"  : "sources/{LANG}",
        "sources"  : "sources/{LANG}",
        "publications" : "publications",
        "variables" : "sources/{LANG}/variables",
        "layouts" : "kolekti/layouts",
        "jobs" : "kolekti/jobs",
        "profiles" : "kolekti/layouts/profiles",
        }
    }


 
class kolektiBase(object):
    def __init__(self,path):
        self._appdir = os.path.dirname(os.path.realpath( __file__ ))
        self._path = path
        self._xmlparser = ET.XMLParser()
        self._xmlparser.resolvers.add(PrefixResolver())
        
        projectdir = os.path.basename(path)

        try:
            conf = ET.parse(os.path.join(path, 'kolekti', 'settings.xml')).getroot()
            self._config = {
                "project":conf.get('project',projectdir),
                "sourcelang":conf.get('sourcelang'),
                "version":conf.get('version'),
                "languages":[l.text() for l in conf.xpath('/config/languages/lang')],
                "projectdir":projectdir,
                }

        except:
            self._config = {
                "project":"Kolekti",
                "sourcelang":'en',
                "version":"0.7",
                "languages":["en","fr"],
                "projectdir":projectdir,
                }
            
        self._version = self._config['version']
        
    def __getattribute__(self, name):
        try:
            if name[:9] == "get_base_" and name[9:]+'s' in objpathes[self._config['version']]:
                def f(objpath):
                    return self.process_path(objpathes[self._config['version']][name[9:]+"s"] + "/" + objpath)
                return f
        except:
            import traceback
            print traceback.format_exc()
            pass
        return super(kolektiBase, self).__getattribute__(name)

    @property
    def config(self):
        return self._config

    def process_path(self,path):
        return path
    
    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts = urllib2.url2pathname(path).split('/')
        #        print self.__path, pathparts
        return os.path.join(self._path, *pathparts)


    def get_script(self, plugin):
        import plugins
        return plugins.getPlugin(plugin,self._path)
        

    def get_tree(self, root=None):
        if root is None:
            root = self._path
        else:
            root = self.__makepath(root)
        return self.__get_directory_structure(root).values()
            
    def __get_directory_structure(self, rootdir):
        """
        Creates a nested dictionary that represents the folder structure of rootdir
        """
        dir = {}
        rootdir = rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir

        return dir

    def get_extensions(self, extclass, **kwargs):
        extensions = {}
#        print "get_extensions",extclass,self.__path,kwargs
        extf_obj = extclass(self._path, **kwargs)
        exts = (n for n in dir(extclass) if not(n.startswith('_')))
        extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))
        return extensions
        

    def get_xsl(self, stylesheet, extclass = None, xsldir = None, system_path = False, **kwargs):
        print "get xsl",stylesheet, extclass , xsldir , kwargs
        if xsldir is None:
            xsldir = os.path.join(self._appdir, 'xsl')
        else:
            if system_path:
                xsldir = os.path.join(self._appdir, xsldir)
            else:
                xsldir = self.__makepath(xsldir)
        path = os.path.join(xsldir, stylesheet+".xsl")
        xsldoc  = ET.parse(path,self._xmlparser)
        if extclass is None:
            extclass = XSLExtensions
        xsl = ET.XSLT(xsldoc, extensions=self.get_extensions(extclass, **kwargs))
        return xsl

    def parse(self, filename):
        src = self.__makepath(filename)
        return ET.parse(src,self._xmlparser)
    
    def read(self, filename):
        ospath = self.__makepath(filename)
        with open(ospath, "r") as f:
            return f.read()

    def write(self, content, filename):
        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            f.write(content)
            
    def xwrite(self, xml, filename, encoding = "utf-8", pretty_print=True):
        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            f.write(ET.tostring(xml, encoding = encoding, pretty_print = pretty_print))
            
    # for demo
    def save(self, path, content):
        content = ET.XML(content, parser=ET.HTMLParser())
        mod = ET.XML("<html xmlns='http://www.w3.org/1999/xhtml'><head><title>KolektiModule</title></head><body/></html>")
        mod.find('{http://www.w3.org/1999/xhtml}body').append(content)
        ospath = self.__makepath(path)
        with open(ospath, "w") as f:
            f.write(ET.tostring(mod, encoding = "utf-8", pretty_print = True))

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
        
        return 'file://' + urllib.pathname2url(path.encode('utf-8'))


    def getPathFromUrl(self, url):
        return os.path.join(url.split('/')[3:])

    def getPathFromSourceUrl(self, url, base="/"):
        pu = urlparse.urlparse(url)
        if len(pu.scheme):
            return None
        else:
            r = urllib.url2pathname(url)
            aurl = urlparse.urljoin(base,r)
            return aurl

    def _get_critdict(self, profile):
        crits = profile.xpath("criterias/criteria[@checked='1']")
        critdict={}
        for c in crits:
            critdict.update({c.get('code'):c.get('value')})
        return critdict


    def substitute_criterias(self,string, profile, extra={}):
        critdict = self._get_critdict(profile)
        critdict.update(extra)

        for crit,val in critdict.iteritems():
            string=string.replace('{%s}'%crit,val)

        return string

        
    def substitute_variables(self, string, profile):
        for variab in re.findall('{[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+}', string):
            splitVar = variab[2:-1].split(':')
            sheet = splitVar[0].strip()
            v = splitVar[1].strip()
            val = self.variable_value(sheet, v, profile)
            string = string.replace(variab, val)
        return string


    def variable_value(self, sheet, variable, profile, extra={}):
        if sheet[0] != "/":
            fvar = self.get_base_variable(sheet)
        else:
            fvar = sheet
        print sheet,fvar
        xvar = self.parse(fvar)
        values = xvar.xpath('/variables/variable[@code="%s"]/value'%variable)
        # print [ET.tostring(v) for v in values]
        critdict = self._get_critdict(profile)
        critdict.update(extra)
        for value in values:
            accept = True
            for crit in value.findall('crit'):
                critname = crit.get('name')
                if critname in critdict:
                    if not critdict.get(critname) == crit.get('value'):
                        accept = False
                else:
                    accept = False
            if accept:
                return value.find('content').text
        print "Warning: Variable not matched",sheet, variable
        return "[??]"

class XSLExtensions(kolektiBase):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extension"
    def __init__(self, path):
        super(XSLExtensions, self).__init__(path)
            
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


