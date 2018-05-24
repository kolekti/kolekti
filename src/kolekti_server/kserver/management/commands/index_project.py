import os
from django.core.management.base import BaseCommand, CommandError
from kolekti.searchindex import IndexManager
import logging

class Command(BaseCommand):
    help = 'rebuild search index for project'
        
    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        
    def handle(self, *args, **options):
        from django.conf import settings
        user = options['user']
        project = options['project']
        projectspath = os.path.join(settings.KOLEKTI_BASE, user)
        indexmgr = IndexManager(projectspath, project)
        indexmgr.indexbase()
        self.stdout.write("done.")
