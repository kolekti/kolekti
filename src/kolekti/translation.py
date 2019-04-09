# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import os
import json
from zipfile import ZipFile
import re
import urllib2

import mimetypes
mimetypes.init()

from lxml import etree as ET
import logging
logger = logging.getLogger(__name__)

from django.utils.text import get_valid_filename

from publish_utils import PublisherMixin, PublisherExtensions, ReleasePublisherExtensions
from .common import kolektiTests, XSLExtensions, LOCAL_ENCODING, KolektiValidationError, KolektiValidationMissing
from kolekti import plugins
from .synchro import SvnClient

logger = logging.getLogger(__name__)


class TranslatorSynchro(SvnClient):
    def __init__(self, basepath, username, project, release):
        super(TranslatorSynchro, self).__init__(username = username)
        self._base = os.path.join(basepath, username, project, 'releases', release)
        self._release = release

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts=urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)
        
    def lang_state(self, lang):
        assembly = '/'.join(['sources', lang, 'assembly', self._release + '_asm.html']) 
        ospath = self.__makepath(assembly)
        try:
            props = self._client.propget('release_state', ospath)
            state = props.get(ospath.replace('\\','/').encode('utf8'), None)
        except:
            # logger.exception('could not get assembly state')
            state = None
            
        if state is None:
#            logger.debug(os.path.exists(ospath))
            if os.path.exists(ospath):
                state = "local"
        return state

    def propget(self, name, path):
        ospath = self.__makepath(path)
        try:
            props = self._client.propget(name, ospath)
            return props.get(ospath.replace('\\','/').encode('utf8'),None)
        except:
            return None

class TranslationImporter(kolektiTests):

    html = "{http://www.w3.org/1999/xhtml}"

    def __init__(self, *args, **kwargs):
        super(TranslationImporter, self).__init__(*args, **kwargs)
        self.__parser = ET.XMLParser(load_dtd=True)
        
    def __get_path(self, path, release, lang):
        pathparts = path.split('/')
        try:
            return path.split('sources/%s/'%lang)[1]
        except IndexError:
            raise KolektiValidationError('wrong path in zip file')
        
    def __checkfile(self, filepath, filec, importfiletype, release, lang):
        logger.debug('checkfile %s %s',filepath, importfiletype)
        projectfile = filepath
        if '/' in filepath:
            projectfile = self.__get_path(filepath, release, lang)
        if importfiletype in ("text/html", "text/xml", "application/xml"):
            try:
                xml = ET.fromstring(filec, self.__parser)
            except:
                error = self.__parser.error_log[0]
                logger.exception("assembly parse error")
                raise KolektiValidationError('xml parse error: line %d:%d\n%s'%(error.line, error.column, error.message))

            logger.debug(xml.tag)
            # test if assembly
            if xml.tag == self.html + 'html':
                self.test_xml(xml,"assembly")
                
                projectfile = "/releases/" + release + '/sources/' + lang +'/assembly/' + release +'_asm.html'
                xhead = xml.xpath('/h:html/h:head', namespaces = self.namespaces)[0]
                xbody = xml.xpath('/h:html/h:body', namespaces = self.namespaces)[0]
                xbody.set('lang', lang)
                xbody.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                try:
                    xmetalang = xml.xpath('/h:html/h:html/h:meta[@name="LANG"][@scheme="condition"]',
                                              namespaces = self.namespaces)[0]
                    xmetalang.set('content',lang)
                except IndexError:
                    ET.SubElement(xhead, '{http://www.w3.org/1999/xhtml}meta', {"scheme":"condition","name":"LANG","content":lang})
                self.makedirs(self.dirname(projectfile))
                self.xwrite(xml, projectfile, pretty_print=False, sync = False)
                
            if xml.tag == 'variables':
                self.test_xml(xml,'variables')
                projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
                self.makedirs(self.dirname(projectfile))
                logger.debug(projectfile)
                self.write(filec, projectfile, sync = False)
                
        if importfiletype[:6] == "image":
            projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
            self.makedirs(self.dirname(projectfile))
            self.write(filec, projectfile, sync = False)
        logger.debug(projectfile)
        return projectfile

    
    def import_files(self, path, importfile, importfiletype, release, lang):
        logger.debug("%s/%s %s", path, importfile, importfiletype)
        files = []
        
        if importfiletype == "application/zip":
            z = ZipFile(os.path.join(path, importfile))
            for ifilename in z.namelist():
                logger.debug(ifilename)
                ifilec = z.read(ifilename)
                filetype = mimetypes.guess_type(ifilename)[0]
                projectfile = self.__checkfile(ifilename, ifilec, filetype, release, lang)
                files.append(projectfile)
                #self.write(ifilec, projectfile, "wb", sync = False)
        else:
            with open(os.path.join(path, importfile)) as f:
                ifilec = f.read() 
            projectfile = self.__checkfile(importfile, ifilec, importfiletype, release, lang)
            files.append(projectfile)
            #self.write(ifilec, projectfile, "wb", sync = False)
        return files


    def commit(self, files):
        pass

    def rollback(self, files):
        pass

ns ={'namespaces': {'h':'http://www.w3.org/1999/xhtml'}}
class AssemblyImporter(object):
    namespaces = {'h':'http://www.w3.org/1999/xhtml'}
    def __init__(self, path, username, project = None, release = None):
        self._path = path
        self._username = username 
        self._release = release  
        self._project = project 
        self.__parser = ET.XMLParser(load_dtd=True)
        
    def _get_source_lang(self, project, release):
        syncmgr = TranslatorSynchro(self._path, self._username, project, release)
        for l in os.listdir(os.path.join(self._path, self._username, project, 'releases', release, 'sources')):
            if l == 'share':
                continue
            try:
                state = syncmgr.lang_state(l)
                if state=="sourcelang":
                    return l
            except:
                logger.exception('could not get lang state')
                continue

    def _check_attribute(self, elta, attr):
        attr = attr.replace('{http://www.w3.org/XML/1998/namespace}','')
        if attr == "content" and elta.xpath('local-name()="meta" and @name="LANG" and @scheme ="condition"'):
            return False
        if attr == "lang" and elta.xpath('local-name()="body"'):
            return False
        if attr == "xml:lang" and elta.xpath('local-name()="body"'):
            return False
        return True
        
    def _compare_attributes(self, elta, eltb):
        for attr,val in elta.attrib.iteritems():
            if self._check_attribute(elta, attr):
                if eltb.get(attr) != val:
                    raise KolektiValidationError('structure does not match [attributes] [%s (%s, %s)]'%(attr,val,eltb.get(attr)))
                
            
    def _iter_structures(self, elta, eltb):
        taga = elta.xpath('local-name()')
        tagb = eltb.xpath('local-name()')
        if taga != tagb:
            logger.debug('structure does not match %s %s'%(taga, tagb))
            raise KolektiValidationError('assembly structure does not match source')

        self._compare_attributes(elta, eltb)

        if taga == "head":
            return
        
        if taga == "div":
            if elta.get('class') =='topic':
                return 
        for subelta, subeltb in zip(elta, eltb):
            self._iter_structures(subelta, subeltb)
        
    def check_structure(self, project, assembly, release) :
        srclang = self._get_source_lang(project, release)
        logger.debug(5*"%s ", self._path, self._username, project,release, srclang)
        src_assembly_file = os.path.join(self._path, self._username, project, 'releases', release, "sources", srclang, "assembly", release+"_asm.html")
        src_assembly = ET.parse(src_assembly_file, self.__parser)
        try :
            src_assembly = src_assembly.getroot()
        except AttributeError:
            pass
        try :
            assembly = assembly.getroot()
        except AttributeError:
            pass
        self._iter_structures(src_assembly, assembly)



    def check_variables(self, project, assembly, release) :
        pass
    
    def fix_topic_sources(self, project, assembly, release) :
        return assembly
    
    def fix_links(self, project, assembly, release) :
        return assembly
    
    def fix_lang(self, project, assembly, release, lang) :
        for elt_img in assembly.xpath('//h:img',**ns):
            src_img = elt_img.get('src')
            splitpath = src_img.split('/')
            if splitpath[1] == "sources" and splitpath[2] != 'share':
                splitpath[2] = lang 
                elt_img.set('src','/'.join(splitpath))
        try:
            assembly.xpath('/h:html/h:head/h:meta[@scheme="condition"][@name="LANG"]',**ns)[0].set('content',lang)
        except IndexError:
            pass
        try:
            assembly.xpath('/h:html/h:head/criteria[@code="LANG"]',**ns)[0].set('value',lang)
        except IndexError:
            pass
        try:
            body = assembly.xpath('/h:html/h:body',**ns)[0]
            body.set('lang',lang)
            body.set('{http://www.w3.org/XML/1998/namespace}lang',lang)
        except IndexError:
            pass

        return assembly
    
    def fix_assembly(self, project, assembly, release) :
        fixtures = os.path.join(self._path, self._username, project, 'releases', release, 'kolekti', 'fixtures')
        if os.path.exists(fixtures):
            for fixfile in os.listdir(fixtures):
                extension = os.path.splitext(fixfile)[1]
                if extension == '.xsl':
                    xsl = ET.XSLT(ET.parse(os.path.join(fixtures, fixfile)))
                    assembly = xsl(assembly)
        return assembly
    
    def guess_project(self, assembly):
        try:
            project = assembly.xpath('/h:html/h:head/h:meta[@name="kolekti.project"]/@content', namespaces=self.namespaces)[0]
        except:
            logger.exception('project meta not found')
            raise KolektiValidationMissing('could not detect project')

        if not os.path.exists(os.path.join(self._path, self._username, project)):
            raise KolektiValidationError('project directory does not exists')
        
        return project
    
    def guess_release(self, assembly, project):
        # get assembly dir
        try:
            release = assembly.xpath('/h:html/h:head/h:meta[@name="kolekti.releasedir"]/@content', namespaces=self.namespaces)[0]
        except:            
            logger.exception('release name not found')
            raise KolektiValidationMissing('could not detect release name')

        if not os.path.exists(os.path.join(self._path, self._username, project, 'releases', release)):
            raise KolektiValidationError('release directory does not exists')            
        return release

    def lang_unalias(self, lang):
        lang = str(lang).lower()
        if re.match('[a-z]{2}[-_][a-z]{2}', lang):
            return lang[:2]
        return lang
    
    def import_assembly(self, assembly_src, lang=None, check=True):
        # xml parse
        try:
            assembly = ET.fromstring(assembly_src, self.__parser)
        except:
            error = self.__parser.error_log[0]
            logger.exception('Assembly parse error')
            raise KolektiValidationError('xml parse error: line %d:%d\n%s'%(error.line, error.column, error.message))

        
        # check lang
        if lang is None:
            try:
                lang = assembly.xpath('/h:html/h:body/@lang|/h:html/h:body/@xml:lang', namespaces=self.namespaces)[0]
            except:
                logger.exception('language not found')
                raise KolektiValidationMissing('could not detect language')

        logger.debug("{%s}",type(self._project))
        if self._project is None:
            project = self.guess_project(assembly)
        else:
            project = self._project
            
        if self._release is None:
            release = self.guess_release(assembly, project)
        else:
            release = self._release
            
        if check:
            src_lang = self._get_source_lang(project, release)
            if lang == src_lang:
                raise KolektiValidationMissing('language is source language')
        
            if not os.path.exists(os.path.join(self._path, self._username, project, 'releases', release , 'sources', lang)):
                lang = self.lang_unalias(lang)
                if not os.path.exists(os.path.join(self._path, self._username, project, 'releases', release , 'sources', lang)):

                    raise KolektiValidationError('language directory does not exists [%s]'%lang)

        release_dir = os.path.join(self._path, self._username, project, 'releases', release)
        assembly_dir = os.path.join(release_dir, 'sources', lang, 'assembly')
        assembly_file = '/'.join(['sources', lang, 'assembly', release + '_asm.html'])

        if check:
            syncmgr = TranslatorSynchro(self._path, self._username, project, release)
        
            try:
                state = syncmgr.lang_state(lang)
            except:
                logger.exception('import release state')
                raise KolektiValidationError('could not get release state')

            if not (state == 'translation' or state == 'validation'):
                raise KolektiValidationError('release state does not allow update of translation')

        logger.debug("check assembly %s, %s, %s"%(project, assembly, release))
        
        assembly = self.fix_topic_sources(project, assembly, release)
        assembly = self.fix_links(project, assembly, release)
        assembly = self.fix_assembly(project, assembly, release)
        assembly = self.fix_lang(project, assembly, release, lang)
                
        if check:
            self.check_structure(project, assembly, release)
            self.check_variables(project, assembly, release)       
        
        with open(os.path.join(self._path, self._username, project, 'releases', release , 'sources', lang, 'assembly', release+"_asm.html"), 'w') as f:
            f.write(ET.tostring(assembly, encoding='utf-8'))
        return {'project':project, 'release': release, 'lang':lang}
        
# command line
    
def cmd_compare(args):
    """ compare two assembly, runs in a relase directory
    args : (.lang) language of the assembly to compare to sourcelang
    """
    projectdir = os.path.dirname(os.path.dirname(os.getcwd()))
    release = os.path.basename(os.getcwd())
    importer = TranslationImporter(projectdir)
    assembly = importer.parse('releases/%(release)s/sources/%(lang)s/assembly/%(release)s_asm.html'% {
        'release':release,
        'lang':args.lang
        })
    importer.check_structure(assembly, release)

def cmd_import(args):
    """ import a assembly in a project
    args : object with assembly and project attributes
    """
    ti = TranslationImporter(args.project)
    with open(args.assembly) as f:
        assembly = f.read()
    ti.import_assembly(assembly)
    
def main():
    import argparse
    from django.conf import settings

    
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(title='commands')
    parser_compare = subparsers.add_parser('compare', help="compare assembly structure to source lang")
    parser_compare.add_argument('lang', action="store")
    defaults = {'cmd':'compare'}
    parser_compare.set_defaults(**defaults)

    parser_import = subparsers.add_parser('import', help="import assembly in project")
    parser_import.add_argument('assembly', action="store")
    parser_import.add_argument('project', action="store")
    defaults = {'cmd':'import'}
    parser_import.set_defaults(**defaults)
    
    args = argparser.parse_args()
    
    if args.cmd == 'compare':
        cmd_compare(args)

    if args.cmd == 'import':
        cmd_import(args)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
