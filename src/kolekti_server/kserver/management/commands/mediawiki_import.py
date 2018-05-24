import os
from django.core.management.base import BaseCommand, CommandError
from kolekti.common import kolektiBase
from kolekti.adapters.mediawiki import AdapterMediawiki
import logging

class _Adapter(AdapterMediawiki, kolektiBase):
    pass

class Command(BaseCommand):
    help = 'import topics from mediawiki'
        
    def add_arguments(self, parser):
        parser.add_argument('url', type=str)
        parser.add_argument('--recurse', action="store_true", dest="recurse", default=False)
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('import_dir', type=str)
        parser.add_argument('lang', type=str)
        parser.add_argument('--adapter', default=None, type=str)
        
    def handle(self, *args, **options):
        from django.conf import settings
        wikiurl = options['url']
        recurse = options['recurse']
        adapter = options['adapter']
        user = options['user']
        project = options['project']
        import_dir = options['import_dir']
        lang = options['lang']
        projectdir = os.path.join(settings.KOLEKTI_BASE, user, project)
        mw = _Adapter(projectdir)
        if adapter is None:
            ads = "kolekti:mediawiki"
        else:
            ads = "kolekti:mediawiki:" + adapter
        topic = mw.gettopic_mediawiki(None, wikiurl, ads)
        for link in topic.xpath('//a[@href]'):
            logging.debug(link.get('href'))
        ET.tostring(topic)
        self.stdout.write(str(res))
