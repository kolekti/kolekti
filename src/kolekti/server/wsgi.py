import os
import json

import mimetypes
mimetypes.init()
from kolekti.common import kolektiBase
from kolekti.server.templates import render

class wsgiclass:
    def __init__(self, path):
        self.kolekti = kolektiBase(path)
        self.routes = None
        
    def servefile(self, root, environ, start_response):
        if os.path.isfile(root):
            headers = []
            mt, enc = mimetypes.guess_type(root)
            if mt is None :
                mt = "application/octet-stream"
                headers.append(('Content-type', mt))
            if enc is not None:
                headers.append(('Content-Encoding', enc))
            start_response("200 OK", headers)
            with open(root) as fd:
                yield fd.read()
        else:
            start_response("404 NotFound",[])
            yield "nope"
            print "ERROR",root
        return


    def __call__(self,environ, start_response):
        pathparts = environ['PATH_INFO'].split('/')[1:]
        if pathparts[0] =='static':
            # serve project file
            root = os.path.dirname(os.path.dirname(__file__))
            root = os.path.join(root, 'web', 'static', *pathparts[1:])
            for c in self.servefile(root, environ, start_response):
                yield c

        elif pathparts[0] =='ui':
            if environ['REQUEST_METHOD'] == 'PUT':
                payload = environ['wsgi.input'].read()
                j = json.loads(payload)
                b = j['content']['mainpanel']['value']
                path =  "/".join(pathparts[1:])
                self.kolekti.save(path, b)
                start_response("200 OK", [])
            else:
                try:
                    lang = pathparts[2]
                except:
                    lang = 'fr'
                    
                headers = []            
                context = {'kolekti':self.kolekti, "lang":lang}
                template ="mainpage"
                if len(pathparts) > 1:
                    context.update({'path': "/".join(pathparts[1:]),
                                })
                else:
                    context.update({'path':""})
                headers.append(('Content-type', 'text/html'))
                start_response("200 OK", headers)
                yield render(template, context)

        elif pathparts[0] == 'xhr':
            headers = []
            if pathparts[1] == 'languages':
                pass

            if pathparts[1] == 'tree':
                try:
                    root = "/".join(pathparts[2:])
                except IndexError:
                    root = ""
                print "Tree",pathparts
                json_obj = self.kolekti.get_tree(root)
            headers.append(('Content-type', 'application/json'))
            start_response("200 OK", headers)
            yield json.dumps(json_obj)
        else:
            root = self.kolekti.getOsPath('/'.join(pathparts))        
            for c in self.servefile(root, environ, start_response):
                yield c
        return
