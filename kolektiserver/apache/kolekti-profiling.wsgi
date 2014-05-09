import os, sys
import mimetypes

from repoze.profile.profiler import AccumulatingProfileMiddleware


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

mimetypes.init()

# magic python path
from os.path import abspath, dirname

dir = dirname(dirname(abspath(__file__)))
sys.path.append(dir)
sys.path.append(dirname(dir))
sys.path.append('/home/waloo/Projets/kolekti')
os.environ['appdir']='/home/waloo/Projets/kolekti/applications/trunk/kolektiserver'

from kolekti.http.wsgirequesthandler import KolektiHandler

application = KolektiHandler()

application = AccumulatingProfileMiddleware(
               application,
               log_filename='/tmp/kolekti-profile.log',
               cachegrind_filename='/tmp/cachegrind.out.bar',
               discard_first_request=True,
               flush_at_shutdown=True,
               path='/__profile__'
              )

