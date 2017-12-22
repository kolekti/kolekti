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
    help = 'copy release'

    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('project', type=str)
        parser.add_argument('-s', '--source', type=str)
        parser.add_argument('-i', '--index', type=str)
#        parser.add_argument('-f', '--file', type=str)
        
    def handle(self, *args, **options):
        from django.conf import settings
        self.stdout.write(str(args))
        self.stdout.write(str(options))
        user = options['user']
        project = options['project']
        release = options['source']
        newindex = options['index']
        projectpath = os.path.join(settings.KOLEKTI_BASE, user, project)
        #self._copy_release(projectpath, release, newindex)
        #self._copy_properties(projectpath, release, newindex)
        #self._process_release_info(projectpath, release, newindex)
        self.stdout.write("done.")
        
    def _copy_properties(self, projectpath, release, newindex):
        releasename, releaseindex = release.rsplit('_', 1)
        newrelease = releasename + '_' + newindex
        properties = {}
        client = pysvn.Client()
        checkin = []
        for lang in os.listdir(os.path.join(projectpath, 'releases', release, 'sources')):
            assembly = os.path.join(projectpath,'releases', release,'sources', lang, 'assembly', release + '_asm.html')
            newassembly = os.path.join(projectpath,'releases', newrelease,'sources', lang, 'assembly', newrelease + '_asm.html')
            if os.path.exists(assembly):
                props = client.proplist(assembly)
                for prop, value in props[1].iteitems():
                    client.propset(prop, value, newassembly)
            checkin.append(newassembly)
            
    def _copy_release(self, projectpath, release, newindex):
        releasename, releaseindex = release.rsplit('_', 1)
        newrelease = releasename + '_' + newindex
        client = pysvn.Client()
        shutil.copytree(
            os.path.join(projectpath,'releases', release),
            os.path.join(projectpath,'releases', newrelease)
            )
        for lang in os.listdir(os.path.join(projectpath, 'releases', newrelease, 'sources')):
            if os.path.exists(os.path.join(projectpath,'releases', newrelease,'sources', lang, 'assembly', release + '_asm.html')):
                shutil.move(
                    os.path.join(projectpath,'releases', newrelease,'sources', lang, 'assembly', release + '_asm.html'),
                    os.path.join(projectpath,'releases', newrelease,'sources', lang, 'assembly', newrelease + '_asm.html')
                    )
                self._process_assembly(projectpath, newrelease, lang)
                
        shutil.move(
            os.path.join(projectpath,'releases', newrelease, 'kolekti', 'publication-parameters', release + '_asm.xml'),
            os.path.join(projectpath,'releases', newrelease, 'kolekti', 'publication-parameters', newrelease + '_asm.xml')
            )
        self._process_pubparam(projectpath , newrelease)

    def _process_pubparam(self, projectpath , newrelease):
        ppfile = os.path.join(projectpath,'releases', newrelease, 'kolekti', 'publication-parameters', newrelease + '_asm.xml')
        pp = ET.parse(ppfile)
        job = pp.getroot()
        job.set('pubdir',newrelease)
        job.set('id',newrelease+"_asm")
        with open(ppfile, 'w') as f:
            f.write(ET.tostring(pp))
            
    def _guess_release_date(self, projectpath, release):
       return int(time.time())
                    
    def _process_release_info(self, projectpath, release, newindex):
        releasename, releaseindex = release.rsplit('_', 1)
        newrelease = releasename + '_' + newindex
        infofile = os.path.join(projectpath,'releases', newrelease, 'release_info.json')
        try:
            mf = json.load(open(infofile))
        except:
            mf = copy(release_info)

        date = self._guess_release_date(projectpath, release)
            
        mf.update({
        "assembly_dir" : '/releases/{}'.format(newrelease),
        "datetime" : self._guess_release_date(projectpath, release),
        "releaseindex" : newindex,
        "releasename" : releasename,
        "releasedir" : newrelease,
        })
        json.dump(mf, open(infofile,'w'))
        
    def _process_assembly(self, projectpath, newrelease, lang):
        releasename, releaseindex = newrelease.rsplit('_', 1)
        _, project = projectpath.rsplit('/', 1)
        assembly = ET.parse(os.path.join(projectpath,'releases', newrelease,'sources', lang, 'assembly', newrelease + '_asm.html'), parser = parser)
        head = assembly.xpath('/h:html/h:head', **ns)[0]
        self._set_meta(head, "kolekti.project", project)
        self._set_meta(head, "kolekti.releasedir", newrelease)
        self._set_meta(head, "kolekti.releasename", releasename)
        self._set_meta(head, "kolekti.releaseindex", releaseindex)

            
    def _set_meta(self, head, name, content):
        try:
            meta = head.xpath('h:meta[@name="{}"]'.format(name), **ns)[0]
            meta.set("content", content)
        except IndexError:
            meta = ET.SubElement(head, '{http://www.w3.org/1999/xhtml}meta', {"name":name, "content":content})
