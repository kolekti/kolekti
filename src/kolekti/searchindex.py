import sys
import os
import mimetypes
import urllib2
import logging
logger = logging.getLogger(__name__)

from lxml import etree as ET

from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
#from whoosh.analysis import StemmingAnalyser
from whoosh.qparser import QueryParser
from whoosh import index, writing
#from common import kolektiBase

mimetypes.init()
htmlns="http://www.w3.org/1999/xhtml"
LOCAL_ENCODING=sys.getfilesystemencoding()
htmlparser = ET.HTMLParser(encoding='utf-8')

class IndexManager(object):

    def __init__(self, projectspath, projectdir):
        self._base = '/'.join([projectspath, projectdir]) + "/"
        settings = ET.parse(os.path.join(projectspath, projectdir, 'kolekti', 'settings.xml'))
        self._sourcelangs = [l.text for l in settings.xpath('/settings/languages/lang')]
        self._publangs = [l.text for l in settings.xpath('/settings/releases/lang')]

        indexpath = os.path.join(projectspath, '.index', projectdir)
        if os.path.exists(indexpath):
            self.ix = index.open_dir(indexpath)
        else:
            os.makedirs(indexpath)
            schema = Schema( 
                path = ID(stored=True, unique=True),
                type = ID(stored=True),
                title = TEXT(stored=True),
                content = TEXT(field_boost=2.0),
            )
            self.ix = index.create_in(indexpath, schema)             
        
    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts = urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)

        
    def indexresource(self, writer, path, restype):
        logger.debug('indexing %s', path)
        if restype in ['directory',None]:
            return
        elif restype in ['topic','assembly','pivot','toc']:
            ext = self.xhtml_extract(path)
        elif restype in ['variables']:
            ext = self.xml_var_extract(path)
        else:
            ext = self.extract(path)
            
        title, content = ext
        logger.debug(title)
#        logger.debug(content)
        
        writer.add_document(path = unicode(path),
                            type = unicode(restype),
                            title = title,
                            content = content)

    def guess_restype(self, path):
        ospath = os.path.join(self._base, path)
        mime = mimetypes.guess_type(ospath)[0]
        if os.path.isdir(ospath):
            return "directory"
        if path[:9] == '/sources/':
            if path[11:19] == '/topics/':
                if mime == "text/html":
                    return 'topic'
            if path[11:17] == "/tocs/":
                if mime == "text/html":
                    return 'toc'
            if path[11:17] == "/variables/":
                if mime == "text/xml":
                    return 'variable'
            if path[8:15] == '/share/variables/':
                if mime == "text/xml":
                    return 'variable'
        if path[:10] == '/releases/':
            pass
        if path[:14] == '/publications/':
            pass
        return None
    
    def indexbase(self):
        with self.ix.writer() as writer:
            # clear index
            writer.mergetype = writing.CLEAR

            # index source
            for topic in self.itertopics():
                self.indexresource(writer, topic, 'topic')
            return
            for varfile in self.itervariables():
                self.indexresource(writer, varfile, 'variables')
                
            for assembly in self.iterassemblies():
                self.indexresource(writer, assembly, 'assembly')
                
    def itertopics(self):
        for lang in self._sourcelangs:
            logger.debug(os.path.join(self._base, 'sources', lang, 'topics'))
            top = os.path.join(self._base, 'sources', lang, 'topics')
            for root, dirs, files in os.walk(top):
                for f in files:
                    if os.path.splitext(f)[1] == ".html":
                        yield root[len(self._base):] + '/' +  f

    def itervariables(self):
        for lang in self._sourcelangs + ['share']:
            for root, dirs, files in os.walk(os.path.join(self._base, 'sources', lang, 'variables')):
                for f in files:
                    if os.path.splitext(f)[1] == ".xml":
                        yield root[len(self._base):] + '/' +  f

    
    def iterassemblies(self):
        for release in os.listdir(os.path.join(self._base,'releases')):
            for lang in self._publangs:
                if os.path.exists(os.path.join(self._base,'releases',release,'sources', lang, 'assemblies', release + '_asm.html')):
                    yield '/'.join(['releases', release,'sources', lang, 'assemblies', release + '_asm.html'])

        
    def parse(self, path):
        return ET.parse(self.__makepath(path))
    
    def parse_html(self, path):
        return ET.parse(self.__makepath(path), parser = htmlparser)

    # extractors
    def extract(self, path):
        return u"",self.read(path).decode(LOCAL_ENCODING)
    
    def xhtml_extract(self, path):
        xtopic = self.parse_html(path)
        logger.debug(xtopic)
        try:
            title = unicode(xtopic.xpath("/html/head/title/text()",namespaces={'h':htmlns})[0])
        except IndexError:
            title = u"unknown"
        content = u" ".join(xtopic.xpath("/html/body//text()",namespaces={'h':htmlns}))
        return title, content

    def xml_var_extract(self, path):
        xvars = self.parse(path)
        title = unicode(os.path.splitext(path.split('/')[-1])[0])
        content = u" ".join(xvars.xpath("//content//text()"))
        return title, content

    def post_save(self, path):
        logger.debug("post save index")
        if path[:8] == "/drafts/":
            return
        restype = self.guess_restype(path)
        logger.debug("index %s %s"%(restype, path))
        with self.ix.writer() as writer:
            self.indexresource(writer, path, restype)

    def move_resource(self, src, dst):
        ossrc = os.path.join(self._base, src)
        osdst = os.path.join(self._base, dst)
        

    def copy_resource(self, src, dst):
        ossrc = os.path.join(self._base, src)
        osdst = os.path.join(self._base, dst)
            
    def delete_resource(self, path):
        with self.ix.writer() as writer:
            writer.delete_by_term('path',unicode(path))


        
                                
class extractor(object):
    def parse(self, path):
        return self.read(path)

    def read(self, path):
        with open(path) as f:
            return f.read()
    
    def extract(self, path):
        return self.read(path)
        
class xhtml_extractor(extractor):
    def extract(self, path):
        xtopic = self.parse(path)
        title = unicode(xtopic.xpath("/h:html/h:head/h:title/text()",namespaces={'h':htmlns})[0])
        content = unicode(" ".join(xtopic.xpath("/h:html/h:body//text()",namespaces={'h':htmlns})))
        return title, content
    
class xml_var_extractor(extractor):
    def extract(self, path):
        xvars = self.parse(path)
        title = unicode(os.path.splitext(path.split('/')[-1])[0])
        content = unicode(" ".join(xvars.xpath("//content//text()")))
        return title, content
    



class Searcher(object):
    def __init__(self, projectspath, projectdir):
        indexpath = os.path.join(projectspath, '.index', projectdir)
        self.ix = index.open_dir(indexpath)

    def search(self, query, page=1):
        qp = QueryParser("content", schema=self.ix.schema)
        q = qp.parse(query)
        res = []
        with self.ix.searcher() as searcher:
            results = searcher.search_page(q, page, pagelen=20)
            for r in results:
                yield dict(r)
