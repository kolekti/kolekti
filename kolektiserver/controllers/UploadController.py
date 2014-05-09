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



"""controller for upload"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''


from lxml import etree as ET

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc,debug

from kolektiserver.controllers.ProjectsController import ProjectsController

class UploadController(ProjectsController):

    def ctrGET(self):
        try:
            if self.http.params.has_key('uploadform'):
                form = self.http.params.get('form')
                if self.model.isResource(form):
                    (data,mime,etag) = self.model.getResource(form)
                    mimetype=mime[0]
                    if mimetype == "application/xml":
                        data = ET.XML(data)
                    self._setdata('http','body',data)
                    self._setdata('http','mime',mimetype)
                    self._setdata('http','etag',etag)
                    self.view.format_resource()
                    raise EXC.OK
                else:
                    raise
        except not EXC.OK:
            dbgexc()
            raise EXC.NotFound()

    def ctrPOST(self):
        error = False
        debug("http params %s"%self.http.params)
        try:
            if self.http.params.has_key('file'):
                ufiles = self.http.params.getall('file')
            else:
                ufiles = self.http.params.getall('upload')
            for ufile in ufiles:
                try:
                    self.model.import_file(ufile)
                    self.model.setmessage(u"[0014]Import du fichier %(filename)s réalisé avec succès.", {'filename': ufile.filename.encode('utf-8')})
                except:
                    dbgexc()
                    debug("Failed to upload file")
                    self.model.setmessage(u"[0015]Echec lors de l'import du fichier %(filename)s.", {'filename': ufile.filename.encode('utf-8')})
                    error = True
            self.http.response.unicode_body = self.model.getResponse(self.http.params.getone('upload'))
        except:
            dbgexc()
            error = True

        if not error:
            self._setdata('status', "ok", '')

