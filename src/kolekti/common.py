# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import sys
import re
from copy import copy
from datetime import datetime
import ConfigParser
import urllib2
import urllib
import urlparse
import shutil
import logging
import json
import mimetypes
mimetypes.init()
from lxml import etree as ET

from exceptions import *
from settings import settings
from synchro import SynchroManager
from searchindex import IndexManager

LOCAL_ENCODING=sys.getfilesystemencoding()

objpathes = {
    "0.6":{
        "topics" : "modules",
        "tocs"  : "trames",
        "sources"  : "",
        "publications" : "publication",
        "variables" : "sheets/xml",
        "templates" : "design/publication",
        "jobs" : "configuration/orders",
        "profiles" : "configuration/profiles"
        },
    "0.7":{
        "topics" : "sources/{LANG}",
        "tocs"  : "sources/{LANG}/tocs",
        "sources"  : "sources/{LANG}",
        "publications" : "publications",
        "variables" : "sources/{LANG}/variables",
        "templates" : "kolekti/publication-templates",
        "jobs" : "kolekti/publication-parameters",
        "profiles" : "kolekti/profiles",
        }
    }

 
class kolektiBase(object):
    def __init__(self, path, *args, **kwargs):
#        super(kolektiBase, self).__init__(path)
        #TODO  :  read ini file for gettininstallation directory
        try:
            Config = settings()
            self._appdir = os.path.join(Config['InstallSettings']['installdir'],"kolekti")
        except : 
            self._appdir = os.path.dirname(os.path.realpath( __file__ ))

        # logging.debug('project path : %s'%path)
        if path[-1]==os.path.sep:
            self._path = path
        else:
            self._path = path + os.path.sep
        self._xmlparser = ET.XMLParser()
        self._xmlparser.resolvers.add(PrefixResolver())
        self._htmlparser = ET.HTMLParser(encoding='utf-8')

        projectdir = os.path.basename(self._path[:-1])

        try:
            self._project_settings = conf = ET.parse(os.path.join(path, 'kolekti', 'settings.xml')).getroot()
            # logging.debug("project config")
            # logging.debug(ET.tostring(conf))
            self._config = {
                "project":conf.get('project',projectdir),
                "sourcelang":conf.get('sourcelang'),
                "version":conf.get('version'),
                "languages":[l.text for l in conf.xpath('/settings/languages/lang')],
                "projectdir":projectdir,
                }
            
        except:
            # logging.debug("default config")
            self._config = {
                "project":"Kolekti",
                "sourcelang":'en',
                "version":"0.7",
                "languages":["en","fr"],
                "projectdir":projectdir,
                }
            import traceback
            logging.debug(traceback.format_exc() )
        self._version = self._config['version']
        # logging.debug("kolekti v%s"%self._version)

        # instanciate synchro & indexer classes
        try:
            self.syncMgr = SynchroManager(self._path)
            self._syncstate = self.syncMgr.state()
        except ExcSyncNoSync:
            self._syncstate = None
        try:
            self.indexMgr = IndexManager(self._path)
        except:
            logging.debug('Search index could not be loaded')

        
    def __getattribute__(self, name):
        # logging.debug('get attribute: ' +name)
        # import traceback
        # logging.debug(traceback.print_stack())
        try:
            if name[:9] == "get_base_" and name[9:]+'s' in objpathes[self._version]:
                def f(objpath):
                    return self.process_path(objpathes[self._config['version']][name[9:]+"s"] + "/" + objpath)
                return f
        except:
            import traceback
            logging.debug('error getting attribute '+name)
            logging.debug(traceback.format_exc())
            pass
        return super(kolektiBase, self).__getattribute__(name)

    @property
    def config(self):
        return self._config

    def process_path(self,path):
        return path

    def syspath(self, path):
        return self.__makepath(path)

    def localpath(self, path):
        lp = path.replace(self._path,'')
        return '/' + '/'.join(lp.split(os.path.sep))
    
    def path_exists(self, path):
        lp = self.__makepath(path)
        return os.path.exists(lp)

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts = [p for p in urllib2.url2pathname(path).split(os.path.sep) if p!='']
        #logging.debug('makepath %s -> %s'%(path, os.path.join(self._path, *pathparts)))
        #logging.debug(urllib2.url2pathname(path))
        
        return os.path.join(self._path, *pathparts)

    def get_scripts_defs(self):
        defs = os.path.join(self._appdir, 'pubscripts.xml')
        return ET.parse(defs).getroot()


    def basename(self, path):
        return path.split('/')[-1]

    def dirname(self, path):
        return "/".join(path.split('/')[:-1])
    
    def get_directory(self, root=None, filter=None):
        res=[]
        if root is None:
            root = self._path
        else:
            root = self.__makepath(root)
        for f in os.listdir(root):
            pf = os.path.join(root, f)
            if os.path.exists(pf) and (filter is None or filter(root,f)):
                d = datetime.fromtimestamp(os.path.getmtime(pf))
                if os.path.isdir(pf):
                    t = "text/directory"
                    if os.path.exists(os.path.join(pf,'.manifest')):
                        mf = ET.parse(os.path.join(pf,'.manifest'))
                        t += "+" + mf.getroot().get('type')
                else:
                    t = mimetypes.guess_type(pf)[0]
                    if t is None:
                        t = "application/octet-stream"
                res.append({'name':f, 'type':t, 'date':d})
        return res

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

    def get_release_assemblies(self, path):
        ospath= self.__makepath(path)
        for f in os.listdir(ospath):
            if os.path.exists(os.path.join(ospath,f,'kolekti',"publication-parameters")):
                pf = os.path.join(os.path.join(ospath,f))
                d = datetime.fromtimestamp(os.path.getmtime(pf))
                yield (f, d)


    def resolve_var_path(self, path, xjob):
        criteria = re.findall('\{.*?\}', path)
        if len(criteria) == 0:
            yield path
        seen = set()
        for profile in xjob.xpath("/job/profiles/profile|/"):
            ppath = copy(path)
            for pcriterion in profile.findall('criteria/criterion'):
                if pcriterion.get('code') in criteria:
                    ppath.replace('{%s}'%pcriterion.get('code'), pcriterion.get('value'))
            if not ppath in seen:
                seen.add(ppath)
                yield ppath

                
                
    def iter_release_assembly(self, path, assembly, lang, callback):
        assembly_path = '/'.join([path,'sources',lang,'assembly',assembly+'.html'])
        job_path = '/'.join([path,'kolekti', 'publication-parameters',assembly+'.xml'])
        xjob = self.parse(job_path)
        xassembly = self.parse( assembly_path)
        for elt_img in xassembly.xpath('//h:img',namespaces={"h":"http://www.w3.org/1999/xhtml"}):
            src_img = elt_img.get('src')
            for imgfile in self.resolve_var_path(src_img, xjob):
                t = mimetypes.guess_type(imgfile)[0]
                if t is None:
                    t = "application/octet-stream"
                callback(imgfile, t)
        for elt_var in xassembly.xpath('//h:var',namespaces={"h":"http://www.w3.org/1999/xhtml"}):
            attr_class = elt_var.get('class')
            if "=" in attr_class:
                if attr_class[0] == '/':
                    varfilepath = '/'.join(path, attr_class)
                else:
                    varfilepath = '/'.join(path, "sources", lang, "variables", attr_class)
                for varfile in self.resolve_var_path(varfilepath, xjob):
                    t = mimetypes.guess_type(varfile)[0]
                    if t is None:
                        t = "application/octet-stream"
                    yield callback(varfile, t)
                    

    def copy_release(self, path, assembly_name, srclang, dstlang):
        # copy images & variables
        srcsubdirs = [d['name'] for d in  self.get_directory('%s/sources/%s'%(path, srclang)) if d['name'] != 'assembly']
        for subdir in srcsubdirs:
            srcpath = '%s/sources/%s/%s'%(path, srclang, subdir)
            dstpath = '%s/sources/%s/%s'%(path, dstlang, subdir)
            self.copyDirs(srcpath,dstpath)            
            self.syncMgr.post_save(dstpath)
            

        # copy assembly / change language in references to images
        src_assembly_path = '/'.join([path,'sources',srclang,'assembly',assembly_name+'.html'])
        assembly_path = '/'.join([path,'sources',dstlang,'assembly',assembly_name+'.html'])
        try:
            refdir = "/".join([path,'sources',dstlang,'assembly'])
            self.makedirs(refdir)
        except OSError:
            logging.debug('makedir failed')
        self.copy_resource(src_assembly_path, assembly_path)
        xassembly = self.parse( assembly_path)
        for elt_img in xassembly.xpath('//h:img',namespaces={"h":"http://www.w3.org/1999/xhtml"}):
            src_img = elt_img.get('src')
            splitpath = src_img.split('/')
            if splitpath[1:3] == ["sources",srclang]:
                splitpath[2] = dstlang 
                elt_img.set('src','/'.join(splipath))
        self.xwrite(xassembly, assembly_path)


        self.syncMgr.commit(path,"Revision Copy %s to %s"%(srclang, dstlang))

        yield assembly_path
        return

                                        
    def copy_release_with_iterator(self, path, assembly_name, srclang, dstlang):
        def copy_callback(respath, restype):
            splitpath = respath.split('/')
            if splitpath[1:3] == ["sources",srclang]:
                splitpath[2] = dstlang
                splitpath = [path]+splitpath
                try:
                    refdir = "/".join(splitpath.split('/')[:-1])
                    self.makedirs(refdir)
                except OSError:
                    logging.debug('makedir failed')

                respath = path + respath
                self.copy_resource(respath, '/'.join(splitpath))
            return '/'.join(splitpath)

        for copiedfile in self.iter_release_assembly(path, assembly_name, srclang, copy_callback):
            yield copiedfile
        src_assembly_path = '/'.join([path,'sources',srclang,'assembly',assembly_name+'.html'])
        assembly_path = '/'.join([path,'sources',dstlang,'assembly',assembly_name+'.html'])
        try:
            refdir = "/".join([path,'sources',dstlang,'assembly'])
            self.makedirs(refdir)
        except OSError:
            logging.debug('makedir failed')
        self.copy_resource(src_assembly_path, assembly_path)
        xassembly = self.parse( assembly_path)
        for elt_img in xassembly.xpath('//h:img',namespaces={"h":"http://www.w3.org/1999/xhtml"}):
            src_img = elt_img.get('src')
            splitpath = src_img.split('/')
            if splitpath[1:3] == ["sources",srclang]:
                splitpath[2] = dstlang 
                elt_img.set('src','/'.join(splipath))
        self.xwrite(xassembly, assembly_path)
        yield assembly_path
        return
    
        # iteration 
    
    def get_extensions(self, extclass, **kwargs):
        # loads xslt extension classes
        extensions = {}
#        print extclass
        extf_obj = extclass(self._path, **kwargs)
        exts = (n for n in dir(extclass) if not(n.startswith('_')))
        extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))
#        for k,e in extensions.iteritems():
#            if k[1] == "gettopic":
#                print k,e
        return extensions
        

    def get_xsl(self, stylesheet, extclass = None, xsldir = None, system_path = False, **kwargs):
        # loads an xsl stylesheet
        # 
        logging.debug("get xsl %s, %s, %s, %s"%(stylesheet, extclass , xsldir , str(kwargs)))
        if xsldir is None:
            xsldir = os.path.join(self._appdir, 'xsl')
        else:
            if system_path:
                xsldir = os.path.join(self._appdir, xsldir)
            else:
                xsldir = self.__makepath(xsldir)
        path = os.path.join(xsldir, stylesheet+".xsl")
        xsldoc  = ET.parse(path,self._xmlparser)
        if extclass is  None:
            extclass = XSLExtensions
    
        xsl = ET.XSLT(xsldoc, extensions=self.get_extensions(extclass, **kwargs))
        return xsl

    def log_xsl(self, error_log):
        print "log xsl"
        for entry in error_log:
            logging.debug('[XSL] message from line %s, col %s: %s' % (entry.line, entry.column, entry.message))
            print '[XSL] message from line %s, col %s: %s' % (entry.line, entry.column, entry.message)
            #logging.debug('[XSL] domain: %s (%d)' % (entry.domain_name, entry.domain))
            #logging.debug('[XSL] type: %s (%d)' % (entry.type_name, entry.type))
            #logging.debug('[XSL] level: %s (%d)' % (entry.level_name, entry.level))
            #logging.debug('[XSL] filename: %s' % entry.filename)

    def parse_string(self, src):
        return ET.XML(src,self._xmlparser)
    
    def parse_html_string(self, src):
        return ET.XML(src,self._htmlparser)
    
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
        self.post_save(filename)
        
    def write_chunks(self, chunks, filename):
        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            for chunk in chunks():
                f.write(chunk)
        self.post_save(filename)
        
    def xwrite(self, xml, filename, encoding = "utf-8", pretty_print=True, xml_declaration=True):

        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            f.write(ET.tostring(xml, encoding = encoding, pretty_print = pretty_print,xml_declaration=xml_declaration))
        self.post_save(filename)

            
    # for demo
    def save(self, path, content):
        content = ET.XML(content, parser=ET.HTMLParser())
        mod = ET.XML("<html xmlns='http://www.w3.org/1999/xhtml'><head><title>Kolekti topic</title></head><body/></html>")
        mod.find('{http://www.w3.org/1999/xhtml}body').append(content)
        ospath = self.__makepath(path)
        with open(ospath, "w") as f:
            f.write(ET.tostring(mod, encoding = "utf-8", pretty_print = True))
        # index / svn propagation
        self.post_save(path)



    def move_resource(self, src, dest):
        try:
            self.syncMgr.move_resource(src, dest)
        except:
            logging.info('Synchro unavailable')
            shutil.move(self.__makepath(src), self.__makepath(dest))
        try:
            self.indexMgr.move_resource(src, dest)
        except:
            logging.debug('Search index unavailable')
        
    def copy_resource(self, src, dest):
        try:
            self.syncMgr.copy_resource(src, dest)
        except:
            import traceback
            print traceback.format_exc
            logging.info('Synchro unavailable')
            shutil.copy(self.__makepath(src), self.__makepath(dest))
        try:
            self.indexMgr.copy_resource(src, dest)
        except:
            logging.debug('Search index unavailable')

    def delete_resource(self, path):
        try:
            self.syncMgr.delete_resource(path)
        except:
            logging.info('Synchro unavailable')
            if os.path.isdir(self.__makepath(path)):
                shutil.rmtree(self.__makepath(path))
            else:
                os.unlink(self.__makepath(path))
        try:
            self.indexMgr.delete_resource(path)
        except:
            logging.debug('Search index unavailable')

    def post_save(self, path):
        try:
            self.syncMgr.post_save(path)
        except:
            logging.debug('Synchro unavailable')
        try:
            self.indexMgr.post_save(path)
        except:
            logging.debug('Search index unavailable')

    def makedirs(self, path):
        ospath = self.__makepath(path)
        if not os.path.exists(ospath):
            os.makedirs(ospath)
            # svn add if file did not exist
            self.post_save(path)
        
    def rmtree(self, path):
        ospath = self.__makepath(path)
        shutil.rmtree(ospath)
        
    def exists(self, path):
        ospath = self.__makepath(path)
        return os.path.exists(ospath)

    def copyFile(self, source, path):
        ossource = self.__makepath(source)
        ospath = self.__makepath(path) 
        # logging.debug("copyFile %s -> %s"%(ossource, ospath))
               
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
        # logging.debug(path)
        upath = urllib.pathname2url(path.encode('utf-8'))
        if upath[:3]=='///':
            return 'file:' + upath
        else:
            return 'file://' + upath


    def getUrlPath2(self, source):
        path = self.__makepath(source)
        # logging.debug(path)
        
        upath = path.replace(os.path.sep,"/")
# upath = urllib.pathname2url(path.
        if upath[:3]=='///':
            return 'file:' + upath
        if upath[0]=='/':
            return 'file://' + upath
        return 'file:///' + upath


    def getPathFromUrl(self, url):
        return os.path.join(url.split('/')[3:])

    def getPathFromSourceUrl(self, url, base=""):
        pu = urlparse.urlparse(url)
        if len(pu.scheme):
            return None
        else:
            r = urllib.url2pathname(url)
            aurl = urlparse.urljoin(base,r)
            return aurl

    def _get_criteria_dict(self, profile):
        criteria = profile.xpath("criteria/criterion|/job/criteria/criterion")
        criteria_dict={}
        for c in criteria:
            criteria_dict.update({c.get('code'):c.get('value',None)})
        return criteria_dict

    def _get_criteria_def_dict(self):
        criteria = self._project_settings.xpath("/settings/criteria/criterion")
        criteria_dict={}
        for c in criteria:
            criteria_dict.update({c.get('code'):[v.text for v in c]})
        return criteria_dict


    def substitute_criteria(self, string, profile, extra={}):
        criteria_dict = self._get_criteria_dict(profile)
        criteria_dict.update(extra)
        #logging.debug(criteria_dict)
        for criterion, val in criteria_dict.iteritems():
            if val is not None:
                string=string.replace('{%s}'%criterion, val)

        return string

        
    def substitute_variables(self, string, profile):
        for variable in re.findall('{[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+}', string):
            # logging.debug(variable)
            splitVar = variable[1:-1].split(':')
            sheet = splitVar[0].strip()
            sheet_variable = splitVar[1].strip()
            # logging.debug('substitute_variables : sheet : %s ; variable : %s'%(sheet, sheet_variable))
            value = self.variable_value(sheet, sheet_variable, profile)
            string = string.replace(variable, value)
        return string


    def variable_value(self, sheet, variable, profile, extra={}):
        if sheet[0] != "/":
            variables_file = self.get_base_variable(sheet)
        else:
            variables_file = sheet

        xvariables = self.parse(variables_file + '.xml')
        values = xvariables.xpath('/variables/variable[@code="%s"]/value'%variable)

        criteria_dict = self._get_criteria_dict(profile)
        criteria_dict.update(extra)
        for value in values:
            accept = True
            for criterion in value.findall('crit'):
                criterion_name = criterion.get('name')
                
                if criterion_name in criteria_dict:
                    if not criteria_dict.get(criterion_name) == criterion.get('value'):
                        accept = False
                else:
                    accept = False
            if accept:
                return value.find('content').text
        logging.info("Warning: Variable not matched : %s %s"%(sheet, variable))
        return "[??]"


    @property
    def itertopics(self):
        for root, dirs, files in os.walk(os.path.join(self._path, 'sources'), topdown=False):
            rootparts = root.split(os.path.sep)
            if 'topics' in rootparts:
                for file in files:
                    if os.path.splitext(file)[-1] == '.html':
                        yield self.localpath(os.path.sep.join(rootparts+[file]))

    @property
    def itertocs(self):
        def filter(root,f):
            return os.path.splitext(f)[1]==".html" or os.path.splitext(f)[1]==".xml" 

        for root, dirs, files in os.walk(os.path.join(self._path, 'sources'), topdown=False):
            rootparts = root.split(os.path.sep)
            if 'tocs' in rootparts:
                for file in files:
                    if os.path.exists(os.path.join(root,file)) and filter(root,file):
                        yield self.localpath(os.path.sep.join(rootparts+[file]))

    @property
    def itervariables(self):
        for root, dirs, files in os.walk(os.path.join(self._path, 'sources'), topdown=False):
            rootparts = root.split(os.path.sep)
            if 'variables' in rootparts:
                for file in files:
                    if os.path.splitext(file)[-1] == '.xml':
                        yield self.localpath(os.path.sep.join(rootparts+[file]))
        
    @property
    def iterassemblies(self):
        for root, dirs, files in os.walk(os.path.join(self._path, 'releases'), topdown=False):
            rootparts = root.split(os.path.sep)
            if 'assembly' in rootparts:
                for file in files:
                    if os.path.splitext(file)[-1] == '.html':
                        yield self.localpath(os.path.sep.join(rootparts+[file]))

        
    @property
    def iterpivots(self):
        for root, dirs, files in os.walk(os.path.join(self._path, 'releases'), topdown=False):
            rootparts = root.split(os.path.sep)
            for file in files:
                if file=='document.xhtml':
                    yield self.localpath(os.path.sep.join(rootparts+[file]))
                        

    @property
    def iterjobs(self):
        for root, dirs, files in os.walk(os.path.join(self._path, 'kolekti','publication-parameters'), topdown=False):
            rootparts = root.split(os.path.sep)
            for file in files:
                if os.path.splitext(file)[-1] == '.xml':
                    if not file=='criterias.xml':
                        yield {"path":self.localpath(os.path.sep.join(rootparts+[file])),
                               "name":os.path.splitext(file)[0]}
        
    def release_details(self, path, lang):
        res=[]
        root = self.__makepath(path)
        for j in os.listdir(root+'/kolekti/publication-parameters'):
            # print j[-16:]
            if j[-16:]=='_parameters.json':
                release_params = json.loads(self.read(path+'/kolekti/publication-parameters/'+j))
                resrelease = []
                # print release_params
                
                for job_params in release_params:
                    publications = json.loads(self.read(path+'/kolekti/publication-parameters/'+job_params['pubname']+'_parameters.json'))
                    resjob = {
                        'lang': lang,
                        'release':release_params,
                        'publications':publications
                    }
                    resrelease.append(resjob)
                res.append(resrelease)
                    
        return res
                
                
                
class XSLExtensions(kolektiBase):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extensions:functions"
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


