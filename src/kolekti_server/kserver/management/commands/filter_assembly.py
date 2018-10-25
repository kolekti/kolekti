import logging
import os
from django.core.management.base import BaseCommand, CommandError

from kolekti.release import Release

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
        release = Release(projectpath, release)
        for lang in langs:
            release.apply_filters(lang)
