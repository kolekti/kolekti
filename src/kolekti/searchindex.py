import sys
import os
import mimetypes
import urllib2
import logging
from lxml import etree as ET

from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
#from whoosh.analysis import StemmingAnalyser
from whoosh.qparser import QueryParser
from whoosh import index, writing
#from common import kolektiBase

mimetypes.init()
htmlns="http://www.w3.org/1999/xhtml"
LOCAL_ENCODING=sys.getfilesystemencoding()

class IndexManager(object):

    def __init__(self, base):
        self._base = base
        indexpath = os.path.join(base,'kolekti/index')
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
        if restype in ['directory',None]:
            return
        elif restype in ['topic','assembly','pivot','toc']:
            ext = self.xhtml_extract(path)
        elif restype in ['variables']:
            ext = self.xml_var_extract(path)
        else:
            ext = self.extract(path)
            
        title, content = ext
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
            for topic in self.itertopics:
                self.indexresource(writer, topic, 'topic')

            for varfile in self.itervariables:
                self.indexresource(writer, varfile, 'variables')
                
            for assembly in self.iterassemblies:
                self.indexresource(writer, assembly, 'assembly')
                
            for pivot in self.iterpivots:
                self.indexresource(writer, pivot, 'pivot')


    def parse(self, path):
        return ET.parse(self.__makepath(path))

    # extractors
    def extract(self, path):
        return u"",self.read(path).decode(LOCAL_ENCODING)
    
    def xhtml_extract(self, path):
        xtopic = self.parse(path)
        try:
            title = unicode(xtopic.xpath("/h:html/h:head/h:title/text()",namespaces={'h':htmlns})[0])
        except IndexError:
            title = u"unknown"
        content = u" ".join(xtopic.xpath("/h:html/h:body//text()",namespaces={'h':htmlns}))
        return title, content

    def xml_var_extract(self, path):
        xvars = self.parse(path)
        title = unicode(os.path.splitext(path.split('/')[-1])[0])
        content = u" ".join(xvars.xpath("//content//text()"))
        return title, content

    def post_save(self, path):
        logging.debug("post save index")
        if path[:8] == "/drafts/":
            return
        restype = self.guess_restype(path)
        logging.debug("index %s %s"%(restype, path)
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
    



class searcher(object):
    def __init__(self, base):
        self._base = base
        indexpath = os.path.join(base,'kolekti/index')        
        self.ix = index.open_dir(indexpath)

    def search(self, query):
        qp = QueryParser("content", schema=self.ix.schema)
        q = qp.parse(query)
        res = []
        with self.ix.searcher() as searcher:
            results = searcher.search(q)
            for r in results:
                yield dict(r)
