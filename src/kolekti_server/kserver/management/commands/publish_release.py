import os
import shutil
from copy import deepcopy as copy
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from kolekti.searchindex import IndexManager
import logging
import pysvn
import json
import csv
from lxml import etree as ET

from translators.models import TranslatorRelease

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
        
    def handle(self, *args, **options):
        user = options['user']
        project = options['project']
        release = options['release']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        publisher = ReleasePublisher(release_path, projectpath, langs = [lang])
        res = list(publisher.publish_assembly(assembly_name + "_asm"))
        self.stdout.write("done.")

