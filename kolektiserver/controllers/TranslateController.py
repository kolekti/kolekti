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



"""controller for modules"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

import time
import urllib2

from kolekti.logger import dbgexc,debug

from kolektiserver.controllers.PublishController import *

from kolektiserver.publication.publication import MasterPublisher

class TranslateController(PublishController):
    def __init__(self, httpRequest):
        PublishController.__init__(self, httpRequest)

    def genPOST(self):
        debug("http params %s"%self.http.params)
        yield self.view.startdoc()
        try:
            ufile = self.http.params.getall('file')[0]
            if self.http.params.get('publish') == "1":
                for msg in self.__publish(self.model.abstractIO.getpath(ufile)):
                    yield msg
                self.model.log_save(ufile)
            elif self.http.params.get('uploadform') == "1":
                mpath = self.model.savemaster(ufile)
                fileurl = '/projects/%s/translate?upload=1&file=%s' %(self.model.project.get('directory', ''), mpath.encode('utf-8'))
                yield '<script type="text/javascript">'
                yield "window.frameElement.src='%s';" %fileurl
                yield '</script>' 
        except:
            dbgexc()
            yield self.view.error(self._setmessage(u"[0012]Echec lors de la lecture de l'enveloppe"))
            yield self.view.finalize()
            return
        yield self.view.finalizedoc()

    def __publish(self, zipfile):
        self.model.setzip(zipfile)
        params = self.model.params()
        yield self.view.start()
        debug("params %s"%params)
        debug("getting params")

        pubparams = {'pubdir': params.get('pubdir', ''),
                     'pubtitle': params.get('pubtitle', ''),
                     'trame': params.get('trame', ''),
                     'profiles': params.get('profiles', []),
                     'scripts': params.get('scripts', []),
                     'do_master': '0',
                     'filter_master': params.get('filtermaster', ''),
                     'master_name': params.get('mastername', '')}

        try:
            publisher = MasterPublisher(self.view, self.model)

            for msg in publisher.setpubparams(pubparams):
                yield msg

            for msg in publisher.publish():
                yield msg
            self.model.generateManifest(pubparams['trame'])
        except:
            dbgexc()

        self.model.closezip()

        yield self.view.finalize()

