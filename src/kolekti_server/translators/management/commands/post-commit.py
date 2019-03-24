import os
import pysvn
import subprocess
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from kolekti.publish import ReleasePublisher
from translators.models import TranslatorRelease


import logging
logger = logging.getLogger('kolekti.'+__name__)

class Command(BaseCommand):
    help = 'auto updates translators source trees after commit'

    def add_arguments(self, parser):
        parser.add_argument('repo', type=str)
        parser.add_argument('revision', type=int)
        
    def get_changed(self, revision, repo):
        cmd = subprocess.Popen(['/usr/bin/svnlook', 'changed', '-r', str(revision), repo], stdout = subprocess.PIPE)
        for line in cmd.stdout.readlines():
            yield line
        
    def get_author(self, revision, repo):
        cmd = subprocess.Popen(['/usr/bin/svnlook', 'author', '-r', str(revision), repo], stdout = subprocess.PIPE)
        author = cmd.stdout.read()
        return author.strip()
                
    def release_langs(self, user, project, release):
        path = os.path.join(settings.KOLEKTI_BASE, user, project, 'releases', release, 'sources')
        for lang in os.listdir(path):
            if lang == "share":
                continue
            assembly = os.path.join(path, lang, 'assembly', release + '_asm.html')
            status = self.client.propget('release_state', assembly)
            logger.debug(status)
            if status[assembly] in ('sourcelang', 'translation', 'validation'):
                yield lang
                
    def update_all_kolekti(self, project):
        userprojects = set()
        try:
            acllist = TranslatorRelease.objects.filter(project = project)
            for update in acllist:
                path = os.path.join(settings.KOLEKTI_BASE, update.user.username, project, 'kolekti')
                self.client.update(path)
        except TranslatorRelease.DoesNotExist:
            pass

    def register_publish(self, user,  chunks):
        logger.debug('register %s %s', user, chunks)
        try:
            self.republish_list[user]
        except KeyError:
            self.republish_list[user] = {}
        release = chunks[1]
        
        if len(chunks)>3 and chunks[2] == "kolekti":
            self.republish_list[user][release] = "*"
        elif len(chunks)>3 and chunks[2] == "sources":
            self.republish_list[user][release] = set()
            if chunks[3] == "share":                                
                self.republish_list[user][release] = "*"
            if type(self.republish_list[user][release]) is set:
                self.republish_list[user][release].add(chunks[3])
        
    def republish(self, project):
        for user, releases_info in self.republish_list.iteritems():
            for release, lang_info in releases_info.iteritems():
                logger.debug('republish %s %s %s %s', user, project, release, str(lang_info))
                if type(lang_info) is not set:
                    lang_info = self.release_langs(user, project, release)
                publisher = ReleasePublisher('/releases/'+release, settings.KOLEKTI_BASE, user, project, langs = lang_info)
                for item in publisher.publish_assembly(release + "_asm"):
                    logger.debug(item)

    def handle(self, *args, **options):
        logger.debug('handle')
        self.republish_list = {}
        self.client = pysvn.Client()
        
        try:
            self.stdout.write(str(datetime.datetime.now()))
            revision = options['revision']
            repo = options['repo']
            project = repo.split('/')[-1]
            user = self.get_author(revision, repo)
            
            self.stdout.write("author : [%s]"%user)
            
            try:
                acllist = TranslatorRelease.objects.exclude(user__username = user).filter(project__directory = project)
            except TranslatorRelease.DoesNotExist:
                raise CommandError('No update for "%d" ' % revision)
            
            seen = set()
            republish = {}
            
            for mf in self.get_changed(revision, repo):
                logger.debug(mf)
                mf = mf[4:]
                chunks = mf.split('/')
                if len(chunks) > 1 and chunks[0] == "releases":
                    release = chunks[1]
                    updates = acllist.filter(release_name = release)
                    for update in updates:
                        path = os.path.join(settings.KOLEKTI_BASE, update.user.username, update.project.directory, 'releases', release)
                        # register things to be republished
                        if os.path.exists(path):
                            self.register_publish(update.user.username, chunks)
                        else:
                            self.register_publish(update.user.username, ['releases', release, 'share'])
                        if not release in seen:
                            # update local copy of release
                            seen.add(release)

                            if os.path.exists(path):
                                self.client.update(path)
                                logger.debug(path+" updated")
                                self.stdout.write(path+" updated")
                            else:
                                url = "file://%s/%s/releases/%s"%(settings.KOLEKTI_SVN_ROOT, update.project.directory,release)
                                self.client.checkout(url, path)

            self.republish(project)
            logger.debug('update succesfully completed')
            self.stdout.write(self.style.SUCCESS('update succesfully completed'))
        except:
            logger.exception('update command failed')
                
