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


import pluginBase
import os
import base64

from lxml import etree as ET

from kolektiserver.publication.publication import PublisherError
from kolekti.logger import dbgexc,debug

htmlns="http://www.w3.org/1999/xhtml"

helpname="WebHelp5"

class plugin(pluginBase.plugin):

    def postpub(self):
        """
        main publication function
        """
        try:
            sql = self.publisher.model.http.dbbackend
            RemoteService = sql.get_model('RemoteService')

            projectid = int(self.publisher.model.project.get("id", "0"))

            service = sql.select(RemoteService, "foreignid=%d and servicetype='coment' and serviceid='%s'" %(projectid, self.params['serviceid']))[0]

            #base64.b64encode("string")
            #base64.b64decode("Qzdfq5z4")
        except:
            yield (self.publisher.view.error(self.publisher.setmessage(u"[0340]Problème lors de l'exécution du script coment")))
            raise Exception

        linkurl = self.publisher.model.local2url(self.publisher.model.pubpath)
        yield(self.publisher.view.publink('index.html', self.label, '/'.join((linkurl, self.label, 'index.html'))))

