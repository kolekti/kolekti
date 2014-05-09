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


"""
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolekti.exceptions import exceptions as EXC
from kolekti.http import statuscodes as HS
from kolekti.logger import debug

from kolektiserver.views.WWWView import WWWView

class UploadView (WWWView):

    def format_resource(self):
        xslf='%s.xsl' % self.__module__
        xslfile = os.path.join(conf.get('appdir'),'views', 'xsl', xslf)
        xsl  = self._xsl(xslfile)
        try:
            r = xsl(self.http.xml)
            d = self._dialogs(r)
            l = self._localize(d)
            self._serialize(l)
        except AttributeError:
            super(WWWView, self).format_resource()
        except ET.XSLTApplyError, e:
            debug( xsl.error_log )
            raise EXC.Error(HS.STATUS_CODES[500], xsl.error_log)

