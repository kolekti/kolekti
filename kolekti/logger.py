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



"""Kolekti logging services"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import logging
import traceback
import time

from kolekti.kolekticonf import conf

logging.basicConfig(level=logging.DEBUG)

def debug(msg):
    if conf.get('debug'):
        logging.debug("%s %s" %(time.strftime("[%y-%m-%d %H:%M:%S]"), msg))

def dbgexc():
    msg=traceback.format_exc()
    logging.debug("%s %s" %(time.strftime("[%y-%m-%d %H:%M:%S]"), msg))

def shutdown():
    logging.shutdown()

