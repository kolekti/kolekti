import os
from django.core.management.base import BaseCommand, CommandError
from kolekti.publish import ReleasePublisher


class Command(BaseCommand):
        help = 'publish translator release'
        
        def add_arguments(self, parser):
            parser.add_argument('user', type=str)
            parser.add_argument('project', type=str)
            parser.add_argument('release', type=str)
            parser.add_argument('lang', type=str)

        def handle(self, *args, **options):
            from django.conf import settings
            user = options['user']
            project = options['project']
            release = options['release']
            release_path = '/releases/'+ release
            lang = options['lang']
            projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
            publisher = ReleasePublisher(release_path, projectpath, langs = [lang])
            for res in publisher.publish_assembly(release + "_asm"):
                self.stdout.write(str(res))
