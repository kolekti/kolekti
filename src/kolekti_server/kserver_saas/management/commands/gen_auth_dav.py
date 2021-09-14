import os
from django.core.management.base import BaseCommand, CommandError
from kserver_saas.svnutils import SVNUtils

class Command(BaseCommand):
    help = 'regenerate htgroup file for svn auth'
        
    
    def handle(self, *args, **options):
        u = SVNUtils()
        u.generate_htgroup()
        self.stdout.write("done.")
