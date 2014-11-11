import os.path
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
#from whoosh.analysis import StemmingAnalyser
from whoosh.qparser import QueryParser
from whoosh import index, writing
from common import kolektiBase
htmlns="http://www.w3.org/1999/xhtml"

class indexer(kolektiBase):

    def __init__(self, *args, **kargs):
        super(indexer,self).__init__(*args, **kargs)        

        indexpath = self.syspath('kolekti/index')
        if os.path.exists(indexpath):
            self.ix = index.open_dir(indexpath)
        else:
            self.makedirs('kolekti/index')
            schema = Schema( 
                path = ID(stored=True),
                type = ID(stored=True),
                title = TEXT(stored=True),
                content = TEXT(field_boost=2.0),
            )
            self.ix = index.create_in(indexpath, schema)             


    def indexresource(self, writer, path, restype):
        if restype in ['topic','assembly','pivot']:
            ext = xhtmlExtractor(self._path)
        if restype in ['variables']:
            ext = xmlVarExtractor(self._path)
            
        title, content = ext.extract(path)
        
        writer.add_document(path = unicode(path),
                            type = unicode(restype),
                            title = title,
                            content = content)

    
        
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



                
class Extractor(kolektiBase):
    pass

class xhtmlExtractor(Extractor):
    def extract(self, path):
        xtopic = self.parse(path)
        title = unicode(xtopic.xpath("/h:html/h:head/h:title/text()",namespaces={'h':htmlns})[0])
        content = unicode(" ".join(xtopic.xpath("/h:html/h:body//text()",namespaces={'h':htmlns})))
        return title, content
    
class xmlVarExtractor(Extractor):
    def extract(self, path):
        xvars = self.parse(path)
        title = unicode(os.path.splitext(path.split('/')[-1])[0])
        content = unicode(" ".join(xvars.xpath("//content//text()")))
        return title, content
    
    
class searcher(kolektiBase):
    def __init__(self, *args, **kargs):
        super(searcher,self).__init__(*args, **kargs)        
        
        indexpath = self.syspath('kolekti/index')
        self.ix = index.open_dir(indexpath)

    def search(self, query):
        qp = QueryParser("content", schema=self.ix.schema)
        q = qp.parse(query)
        res = []
        with self.ix.searcher() as searcher:
            results = searcher.search(q)
            for r in results:
                yield dict(r)
