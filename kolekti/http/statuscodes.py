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



"""status codes for DAV services
"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

STATUS_CODES = {
        102:    "Processing",
        200:    "Ok",
        201:    "Created",
        204:    "No Content",
        207:    "Multi-Status",
        201:    "Created",
        304:    "Not Modified",
        400:    "Bad Request",
        401:    "Authorizarion Required",
        403:    "Forbidden",
        404:    "Not Found",
        405:    "Method Not Allowed",
        409:    "Conflict",
        412:    "Precondition failed",
        415:    "Unsupported Media Type",
        422:    "Unprocessable Entity",
        423:    "Locked",
        424:    "Failed Dependency",
        500:    "Internal Error",
        501:    "Unsupported method",
        502:    "Bad Gateway",
        507:    "Insufficient Storage"
}
