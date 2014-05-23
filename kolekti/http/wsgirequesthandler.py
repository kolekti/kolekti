# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.




""" WSGI Request handling for kolekti
"""


import locale
import sys
import traceback
import os
import copy
from kolekti.kolekticonf import conf
from kolekti.logger import dbgexc,debug
from kolekti.mvc.controllerfactory import ControllerFactory as CF
from kolekti.mvc.viewfactory import ViewFactory as VF
from kolekti.mvc.modelfactory import ModelFactory as MF
from kolekti.http.httprequest import WebObRequest as Context

from webob import Request,Response

import kolekti.http.statuscodes as HS
from kolekti.exceptions import exceptions as EXC
from webob.exc import *

def KolektiHandlerFct(environ, start_response):
    h=KolektiHandler()
    return h(environ, start_response)

class  KolektiHandler_test_environ(object):
    def __call__(self, environ, start_response):
        import webob
        r=webob.Response()
        r.body="OK"
        r.body+= sys.getfilesystemencoding()
        r.body+="<br/>"
        r.body+= locale.getpreferredencoding()
        r.body+="<br/>"
        r.body+= str(os.environ)
        r.body+="<br/>"
        r.body+= str(environ)

        return r(environ, start_response)


class  KolektiHandler(object):
    ctrFact   = CF()

    def __call__(self, environ, start_response):
        #debug("------------------------------------------------")
        robj = None
#        http = Request(environ=environ)
        http = context = Context(environ = environ)

#        print http.headers
#        context = Context()
#        context.headers = {}
#        context.cookies = {}
#        context.params = {}
#        context.environ = {}


#        print "---------------------------------"
#        for k,v in http.headers.iteritems():
#            print k,":",v
#            context.headers.update({k:v})

#        for k,v in http.cookies.iteritems():
#            print k,":",v
#            context.cookies.update({k:v})

#        context.params = http.params
#        for k in http.params:
#            v = http.params.getall(k)
#            print k,":",v
#            context.params.update({k:v})
        
#        for k,v in http.environ.iteritems():
#            print k,":",v
#            context.environ.update({k:v})
        
#        context.method = http.method
#        context.upath_info = http.upath_info
#        context.path_info = http.path_info
#        context.host = http.host
        #context.port = http.port
        #context.server = http.server
#        context.url = http.url
        
#        context.body = http.body

#        print "---------------------------------"
        debug("%s %s"%(http.method, http.path))

        command=http.method
        if command=='HEAD':
            mname = 'ctrGET'
        else:
            mname = 'ctr' + command

        try:
            ctrs=self.ctrFact.getControllers(context)
            for ctr in ctrs:
                if not hasattr(ctr, mname) and not hasattr(ctr,'ctrALL'):
                    raise EXC.UnsupportedMethod, "Unsupported method (%r)" % command
                try:
                    method = getattr(ctr, mname)
                except AttributeError:
                    method = getattr(ctr, 'ctrALL')
#                print http.method,http.path,"calling  %s.%s"%(ctr.__class__.__name__,method.__name__)

                #self.http.ctrmark(str(ctr))
                method()
                #debug((http.method,http.path,"done  %s.%s"%(ctr.__class__.__name__,method.__name__)))

                #debug("headers %s"%context.response.headers)


        # exceptions handling

        # all went fine, a controller may have raised these exceptions if it wants to prevent the processing
        # by further controllers
        except EXC.OK:
            pass

        except EXC.Status, (ec,dd):
            #debug(("Status",ec,dd))
            context.response.status=ec

        except EXC.Multistatus, (body,):
            if not http is None:
                context.response.status=207
                context.response.content_type='application/xml'
                context.response.body=body


        except EXC.Forbidden, (ec,dd):
            debug(("forbidden",ec,dd))
            if not http is None:
                if int(http.userId) == 0:
                    r = HTTPUnauthorized("Authorization Requested",[('WWW-Authenticate', 'Basic realm="kolekti"')])
                    robj = r(environ, start_response)
                    #http.view.error(401, "Authorization Requested")
                else:
                    r = HTTPForbidden("Authorization Requested")
                    robj = r(environ, start_response)
                    #http.view.error(ec,dd)

        except EXC.AuthError, (ec,dd):
            import traceback
            print traceback.format_exc()
            debug("Auth Error")
            r= HTTPUnauthorized("Authorization Requested",[('WWW-Authenticate', 'Basic realm="kolekti"')])
            robj = r(environ, start_response)

        except EXC.PreconditionFailed:
            debug("PreconditionFailed")
            r= HTTPPreconditionFailed()
            robj = r(environ, start_response)

        except EXC.Error, (ec,dd):
            debug("HTTP ERROR %s %s"%(ec,dd))
            if not http is None:
                context.view.error(ec,dd)

        except HTTPException:
            debug("webob exception")
            raise

        except Exception:
            debug("Exception")
            import traceback
            print traceback.format_exc()
            t=context.view.error(500,"Internal Error", traceback.format_exc())
            r=HTTPInternalServerError(t)
            robj = r(environ, start_response)

        # if not response object
        if not robj:
#            print "result"
            robj = context.response(environ, start_response)

        # print robj
        
        # if request has sql object, delete it
        if context._sql:
            context._sql.close()
        
        # Send response
#        print "-----------------------------------"
        return robj
