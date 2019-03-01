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
from django.conf import settings

ns ={"namespaces": {"h":"http://www.w3.org/1999/xhtml"}}
parser  = ET.XMLParser(load_dtd = True)
    


class Command(BaseCommand):
    help = 'publish release'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('toc', type=str)
        parser.add_argument('job', type=str)
        parser.add_argument('-l', '--lang', type=str)
        parser.add_argument('-a', '--all' , action='store_true')
        
    def handle(self, *args, **options):
        logging.debug(options)
        from django.conf import settings
        user = options['user']
        project = options['project']
        toc = options['toc']
        job = options['job']
        allprofiles = options['all']
        lang = options['lang']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        if lang is None:
            lang = self._get_source_lang(projectpath)

        

  
        self._publish_toc(user, project, toc, job, lang, allprofiles)

        self.stdout.write("done.")

    def _get_source_lang(self, projectpath):
        xset = ET.parse(os.path.join(projectpath, 'kolekti', 'settings.xml'))
        return xset.getroot().get('sourcelang')
        
    def _publish_toc(self, user, project, toc, job, lang, allprofiles=False):

        tocpath = "/sources/" + lang + "/tocs/" + toc + ".html"
        jobpath = "/kolekti/publication-parameters/" + job + ".xml"
        
        from kolekti import publish
        try:
            p = publish.DraftPublisher(settings.KOLEKTI_BASE, user, project, lang=lang, cleanup=False)
            fsjob = os.path.join(settings.KOLEKTI_BASE, user, project, jobpath[1:])
            xjob = ET.parse(fsjob)
            if  allprofiles:
                for profile in xjob.xpath("/job/profiles/profile"):
                    profile.set('enabled','1')
            for event in p.publish_draft(tocpath, xjob):
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
                    self.stderr.write(' [W] %s\n%s'%(event['msg'], event['stacktrace']) )

            self.stderr.write("Publication complete")
        except:
            self.stderr.write("Publication ended with errors")
            import traceback
            self.stderr.write(traceback.format_exc())
