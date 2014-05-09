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


"""constants definition for lock service"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''


# definition for resourcetype
COLLECTION=1
OBJECT=None
DAV_PROPS=['creationdate', 'displayname', 'getcontentlanguage', 'getcontentlength', 'getcontenttype', 'getetag', 'getlastmodified', 'lockdiscovery', 'resourcetype', 'source', 'supportedlock']
PROP_XML=1
PROP_TEXT=2
PROP_LXML=3

# Request classes in propfind

RT_ALLPROP=1
RT_PROPNAME=2
RT_PROP=3

# Locks types
LOCK_TYPE_WRITE=1

# Locks scopes
LOCK_SCOPE_EXCLUSIVE=1
LOCK_SCOPE_SHARED=2

# Locks Depth
LOCK_DEPTH_ZERO=0
LOCK_DEPTH_INFINITE=2

#Locks search direction
LOCK_SEARCH_RESOURCE=1
LOCK_SEARCH_ANCESTORS=2
LOCK_SEARCH_DESCENDANTS=4
LOCK_SEARCH_PARENT=8
