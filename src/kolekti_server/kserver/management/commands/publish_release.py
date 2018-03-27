import os
from copy import deepcopy as copy
import time
import shutil
from django.core.management.base import BaseCommand, CommandError
from kolekti.searchindex import IndexManager
import logging
import pysvn
import json
from lxml import etree as ET

ns ={"namespaces": {"h":"http://www.w3.org/1999/xhtml"}}
parser  = ET.XMLParser(load_dtd = True)

release_info = {
    "assembly_dir" : None,
    "lang" : None,
    "datetime" : 0,
    "toc" : None,
    "releaseindex" : None,
    "releasename" : None,
    "pubname" : None,
    "job" : None,
    "releasedir" : None,
    "releaseprev" : None
}
    


class Command(BaseCommand):
    help = 'publish release'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('release', type=str)
        parser.add_argument('lang', type=str, nargs="*")
        
    def handle(self, *args, **options):
        logging.debug(options)
        from django.conf import settings
        user = options['user']
        project = options['project']
        release = options['release']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        langs = options['lang']
        if len(langs) == 0:
            langs = list(self._get_release_langs(projectpath, release))

        self.stdout.write(str(langs))

        self._publish_release(projectpath, release, list(langs))

        self.stdout.write("done.")

    def _get_release_langs(self, projectpath, releasename):
        srp = os.path.join(projectpath, 'releases', releasename, 'sources')
        for l in os.listdir(srp):
            if l != 'share':
                yield l
        
    def _publish_release(self, projectpath, releasename, langs):

        from kolekti import publish
        try:
            release = '/releases/' + releasename
            p = publish.ReleasePublisher(release, projectpath, langs=langs)
            self.stderr.write('lang %s'%str(langs))
            for event in p.publish_assembly(releasename + "_asm"):
                if event['event'] == "job":
                    self.stderr.write('Publishing Job %s'%event['label'])
                if event['event'] == "profile":
                    self.stderr.write(' profile %s'%event['label'])
                if event['event'] == "result":
                    self.stderr.write('%s complete'%event['script'])
                    for doc in event['docs']:
                        self.stderr.write('[%s] %s'%(doc['type'],doc.get('url','')))

                if event['event'] == "error":
                    self.stderr.write(' [E] %s\n%s'%(event['msg'], event['stacktrace']) )
                if event['event'] == "warning":
                    self.stderr.write(' [W] %s\n%s'%(msg) )

            self.stderr.write("Release publication complete")
        except:
            self.stderr.write("Release publication ended with errors")
            import traceback
            self.stderr.write(traceback.format_exc())
