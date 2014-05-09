#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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

import sys
import os
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-d", "--directory", dest="appdir",
                      help="Kolekti application directory")
    parser.add_option("-p", "--port", dest="port",
                      help="Kolekti server port number")
    parser.add_option("-s", "--serverhost", dest="host",
                      help="Kolekti server hostname/ip")

    (options, args) = parser.parse_args()
    if options.appdir:
        os.environ['KOLEKTI_APPDIR']=options.appdir
    else:
        this=os.path.abspath(os.path.join(os.environ.get('PWD'),sys.argv[0]))
        os.environ['KOLEKTI_APPDIR']=os.path.dirname(this)

    os.environ['KOLEKTI_APP']='kolektiserver'

    from kolektiserver.kolekticonf import conf
    from kolekti.logger import dbgexc
    from kolekti.http.wsgirequesthandler import KolektiHandlerFct
    from kolekti.bootstrap import BootstrapLib
    from paste import httpserver
    
    try:
        bootstrap = BootstrapLib()
        bootstrap.copy_libs()
        bootstrap.copy_base_template()
    except:
        dbgexc()
    if options.host:
        host=options.host
    else:
        host=conf.get('host')

    if options.port:
        port=options.port
    else:
        port=conf.get('port')

    httpserver.serve(KolektiHandlerFct,
                     host,
                     port)
