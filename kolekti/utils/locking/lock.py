# -*- coding: utf-8 -*-
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


import uuid
from time import time

from kolekti.utils.locking.constants import *

class Lock:
    """A lock object"""
    INFINITE_TIMEOUT=4100000000
    def __init__(self,principal,owner,depth=LOCK_DEPTH_INFINITE,scope=LOCK_SCOPE_EXCLUSIVE,timeout=INFINITE_TIMEOUT,locktype=LOCK_TYPE_WRITE):

        self.token=uuid.uuid4()
        self.owner=owner
        self.principal=principal
        self.depth=depth         # 0 or Infinity       LOCK_DEPTH_INFINITE|LOCK_DEPTH_ZERO
        self.scope=scope         # shared or exclusive LOCK_SCOPE_EXCLUSIVE|LOCK_SCOPE_SHARED
        self.type=locktype       # write               LOCK_TYPE_WRITE
        self.timeout=timeout
        self.expires=int(timeout)+int(time())

    def refresh(self,timeout=INFINITE_TIMEOUT):
        self.timeout=timeout
        self.expires=int(timeout)+int(time())
