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
    


class Command(BaseCommand):
    help = 'publish release'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('toc', type=str)
        parser.add_argument('job', type=str)
        
    def handle(self, *args, **options):
        logging.debug(options)
        from django.conf import settings
        user = options['user']
        project = options['project']
        toc = options['toc']
        job = options['job']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        
        lang = self._get_source_lang(projectpath)
  
        self._publish_toc(projectpath, toc, job, lang)

        self.stdout.write("done.")

    def _get_source_lang(self, projectpath):
        xset = ET.parse(os.path.join(projectpath, 'kolekti', 'settings.xml'))
        return xset.getroot().get('sourcelang')
        
    def _publish_toc(self, projectpath, toc, job, lang):

        tocpath = "/sources/" + lang + "/tocs/" + toc + ".html"
        jobpath = "/kolekti/publication-parameters/" + job + ".xml"
        
        from kolekti import publish
        try:
            p = publish.DraftPublisher(projectpath, lang=lang, cleanup=False)

            for event in p.publish_draft(tocpath, jobpath):
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

            self.stderr.write("Publication complete")
        except:
            self.stderr.write("Publication ended with errors")
            import traceback
            self.stderr.write(traceback.format_exc())
