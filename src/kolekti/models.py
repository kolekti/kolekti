objpathes = {
    "0.6":{
        "module" : "modules",
        "trame"  : "trames",
        "publication" : "publication",
        "variables" : "sheets/xml",
        "styles" : "design/publication",
        "orders" : "configuration/orders",
        "profiles" : "configuration/profiles"
        }
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


class KolektiManager(object):
    def __init__(self):
        
        if self.kolektiversion == "0.6":
            url =  'file://'+urllib.pathname2url(self.path)+'/'+urlf
        else:
            url =  'file://'+urllib.pathname2url(self.path)+"/sources/"+self.publang+"/"+urlf
        return url
    
class KolektiObject(object):
    def __init__(self, *args, **kwargs):
        if 'uri' in kwargs:
            self.__uri = kwargs['uri']
            self.
        elif 'id' in kwargs:
            self.__id = kwargs['id']
        elif 'file' in kwargs:
            self.__filname  = kwargs['file']
        if revision in kwargs:
            self.rev = None
        
    @property
    def uri(self):
        pass
    
    @property
    def url(self):
        pass
    
    @property
    def file(self):
        pass

    @property
    def __kid(self):
        pass
    
    @property
    def manager(self):
        


class ModuleManager(KolektiManager):
    pass

class Module(KolektiObject):
    pass
