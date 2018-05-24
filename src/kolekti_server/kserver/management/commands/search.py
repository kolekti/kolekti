import os
from django.core.management.base import BaseCommand, CommandError
from kolekti.searchindex import Searcher
import logging

class Command(BaseCommand):
    help = 'search project'
        
    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('query', type=str)
        
    def handle(self, *args, **options):
        from django.conf import settings
        user = options['user']
        project = options['project']
        query = options['query']
        projectspath = os.path.join(settings.KOLEKTI_BASE, user)
        indexmgr = Searcher(projectspath, project)
        for result in indexmgr.search(query):
            self.stdout.write(str(result))
