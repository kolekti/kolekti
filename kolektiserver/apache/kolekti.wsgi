#     -*- coding:utf8 -*-
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stephane Bonhomme (stephane@exselt.com)
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


import os, sys
import locale

#from repoze.profile.profiler import AccumulatingProfileMiddleware

class NullStream:
      def __init__(self,f=None):
          self.f=None
          if f is not None:
              self.f=open(f,'a')
      def write(self, text):
          try:
              self.f.write(text)
              self.f.flush()
          except:
              pass

sys.stdout = NullStream('/tmp/kolektiout')
sys.stderr = NullStream('/tmp/kolektierr')


# magic python path
from os.path import abspath, dirname

dir = dirname(dirname(abspath(__file__)))
sys.path.append(dir)
sys.path.append(dirname(dir))
#sys.path.append('/home/waloo/Projets/kolekti')
os.environ['KOLEKTI_APPDIR']='/usr/share/pyshared/kolektiserver'
os.environ['KOLEKTI_APP']='kolektiserver'
#os.environ['appdir']='/home/waloo/Projets/kolekti/applications/trunk/kolektiserver'

from kolekti.http.wsgirequesthandler import KolektiHandler

application = KolektiHandler()

# application = AccumulatingProfileMiddleware(
#                application,
#                log_filename='/tmp/kolekti-profile.log',
#                cachegrind_filename='/tmp/cachegrind.out.bar',
#                discard_first_request=True,
#                flush_at_shutdown=True,
#                path='/__profile__'
#               )

