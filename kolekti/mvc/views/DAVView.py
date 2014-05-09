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

""" view dav class"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.mvc.views.View import View
from kolekti.http import statuscodes as HS

class DAVView(View):

    def error(self, code, msg, stack=""):
        if code == 403:
            code = 401
        super(DAVView, self).error(code, HS.STATUS_CODES[code])
        self.http.response.headers.update({"DAV": "1,2"})

