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
    help = 'rename release'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('-o', '--old', type=str)
        parser.add_argument('-n', '--new', type=str)
        parser.add_argument('-f', '--file', type=str)
        parser.add_argument('-c', action="store_true")
        
    def handle(self, *args, **options):
        user = options['user']
        project = options['project']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        if options['file'] is None:
            releases = [(options['old'], options['new'])]
        else:
            releases = []
            with open(options['file']) as csvfile:
                for line in csv.reader(csvfile):
                    releases.append(line)
                
        for old, new in releases:
            self._rename_release(projectpath, old, new)
            self._process_release_info(projectpath, old, new)
            self.stdout.write("%s -> %s"%(old, new))
            
        if options['c']:
            client = pysvn.Client()
            client.checkin(projectpath, "releases renaming")
            for old, new in releases:
                self._update_translations(project, old, new)
                
        self.stdout.write("done.")

    def _rename_release(self, projectpath, release, newname):
        client = pysvn.Client()
        client.move(
            os.path.join(projectpath,'releases', release),
            os.path.join(projectpath,'releases', newname)
            )
        for lang in os.listdir(os.path.join(projectpath, 'releases', newname, 'sources')):
            if os.path.exists(os.path.join(projectpath,'releases', newname,'sources', lang, 'assembly', release + '_asm.html')):
                client.move(
                    os.path.join(projectpath,'releases', newname,'sources', lang, 'assembly', release + '_asm.html'),
                    os.path.join(projectpath,'releases', newname,'sources', lang, 'assembly', newname + '_asm.html')
                    )
                self._process_assembly(projectpath,newname,lang)
                
        client.move(
            os.path.join(projectpath,'releases', newname, 'kolekti', 'publication-parameters', release + '_asm.xml'),
            os.path.join(projectpath,'releases', newname, 'kolekti', 'publication-parameters', newname + '_asm.xml')
            )
        self._process_pubparam(projectpath , newname)

    def _process_pubparam(self, projectpath , newname):
        client = pysvn.Client()
        ppfile = os.path.join(projectpath,'releases', newname, 'kolekti', 'publication-parameters', newname + '_asm.xml')
        pp = ET.parse(ppfile)
        job = pp.getroot()
        job.set('pubdir',newname)
        job.set('id',newname+"_asm")
        with open(ppfile, 'w') as f:
            f.write(ET.tostring(pp))
        try:
            client.add(ppfile)
        except:
            pass
        
    def _guess_release_date(self, projectpath, release):
        c = pysvn.Client()
        def callback_get_login(realm, username, may_save):
            name = ""
            password = ""
            return True, name, password, False
        c.callback_get_login = callback_get_login
        try:
            logs = c.log(os.path.join(projectpath,'releases', release))
            return int(logs[-1].get('date'))
        except:
            import traceback
            self.stderr.write('W Could not get release datetime from svn, using now')
            return time.time()
        
    def _process_release_info(self, projectpath, release, newname):
        releasename, releaseindex = newname.rsplit('_', 1)
        infofile = os.path.join(projectpath,'releases', newname, 'release_info.json')
        try:
            mf = json.load(open(infofile))
        except:
            mf = copy(release_info)

        date = self._guess_release_date(projectpath, release)
            
        mf.update({
        "assembly_dir" : '/releases/{}'.format(newname),
        "datetime" : self._guess_release_date(projectpath, release),
        "releaseindex" : releaseindex,
        "releasename" : releasename,
        "releasedir" : newname,
        })
        json.dump(mf, open(infofile,'w'))
        
    def _process_assembly(self, projectpath, newname, lang):
        releasename, releaseindex = newname.rsplit('_', 1)
        _, project = projectpath.rsplit('/', 1)
        assembly = ET.parse(os.path.join(projectpath,'releases', newname,'sources', lang, 'assembly', newname + '_asm.html'), parser = parser)
        head = assembly.xpath('/h:html/h:head', **ns)[0]
        self._set_meta(head, "kolekti.project", project)
        self._set_meta(head, "kolekti.releasedir", newname)
        self._set_meta(head, "kolekti.releasename", releasename)
        self._set_meta(head, "kolekti.releaseindex", releaseindex)

            
    def _set_meta(self, head, name, content):
        try:
            meta = head.xpath('h:meta[@name="{}"]'.format(name), **ns)[0]
            meta.set("content", content)
        except IndexError:
            meta = ET.SubElement(head, '{http://www.w3.org/1999/xhtml}meta', {"name":name, "content":content})

    def _update_translations(self, project, release, newname):
        client = pysvn.Client()
        tr = TranslatorRelease.objects.filter(project__directory = project, release_name = release)
        for t in tr:
            user = t.user
            user_release_directory = os.path.join(settings.KOLEKTI_BASE, user.username, project, 'releases', release)
            new_release_directory = os.path.join(settings.KOLEKTI_BASE, user.username, project, 'releases', newname)              
            if os.path.exists(user_release_directory):
                shutil.rmtree(user_release_directory)
                client.checkout(
                    "file:///svn/%s/releases/%s"%(project,newname),
                    os.path.join(settings.KOLEKTI_BASE, user.username, project, 'releases')
                    )
                
            t.release_name = newname
            t.save()
