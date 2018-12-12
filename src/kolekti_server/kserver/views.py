# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import re
import os
from copy import copy
import shutil
import json
import random
import traceback
from datetime import datetime
import time
from lxml import etree as ET
import base64
from PIL import Image
import urllib, urllib2
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from zipfile import ZipFile

import logging
logger = logging.getLogger('kolekti.'+__name__)

from kserver_saas.models import Project, UserProfile, UserProject
from forms import UploadFileForm, SearchForm

from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.static import serve 
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.cache import add_never_cache_headers

# kolekti imports
from kolekti.common import kolektiBase
from kolekti.publish_utils import PublisherExtensions
from kolekti import convert06, publish
from kolekti.searchindex import Searcher
from kolekti.exceptions import ExcSyncNoSync
from kolekti.variables import OdsToXML, XMLToOds
from kolekti.import_sheets import Importer, Templater

fileicons= {
    "application/zip":"fa-file-archive-o",
    'application/x-tar':"fa-file-archive-o",
    "audio/mpeg":"fa-file-audio-o",
    "audio/ogg":"fa-file-audio-o",
    "application/xml":"fa-file-code-o",
    "application/vnd.ms-excel":"fa-file-excel-o",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':"fa-file-excel-o",
    'application/vnd.oasis.opendocument.spreadsheet':"fa-file-excel-o",
    'image/png':"fa-file-image-o",
    'image/gif':"fa-file-image-o",
    'image/jpeg':"fa-file-image-o",
    'image/tiff':"fa-file-image-o",
    "application/pdf":"fa-file-pdf-o",
    'application/vnd.oasis.opendocument.presentation':"fa-file-powerpoint-o",
    'application/vnd.ms-powerpoint':"fa-file-powerpoint-o",
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':"fa-file-powerpoint-o",
    'text/html':"fa-file-text-o",
    'text/plain':"fa-file-text-o",
    'video/mpeg':"fa-file-video-o",
    'application/vnd.oasis.opendocument.text':"fa-file-word-o",
    'application/msword':"fa-file-word-o",
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':"fa-file-word-o",
    "application/octet-stream":"fa-file-o",
    "text/directory":"fa-folder-o",
    }


ns = {'namespaces':{'html':'http://www.w3.org/1999/xhtml'}}
    
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        if settings.KOLEKTI_MULTIUSER:
            return login_required(view)
        else:
            return view

class kolektiMixin(LoginRequiredMixin):

    def get(self, request, **kwargs):
        context, kolekti = self.get_context_data(data = kwargs)
        return self.render_to_response(context)
    
    def get_context_data(self, data={}, **kwargs):
        try:
            context = super(kolektiMixin, self).get_context_data(**kwargs)
        except AttributeError:
            context = {}
        kolekti = None
        if 'project' in data.keys():
            try:
                project = data['project']
                project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
                kolekti = kolektiBase(project_path)
                userproject = UserProject.objects.get(user = self.request.user, project__directory = project)
                context.update({
                    'user_project' : userproject,
                    'default_lang' : kolekti.project_default_language(),
                })

                if not 'lang' in data.keys():
                    context.update({
                        'lang' : kolekti.project_default_language()
                    })
                
            except UserProject.DoesNotExist:
                raise Http404
            
        userprojects = UserProject.objects.filter(user = self.request.user)
        context.update({'user_projects': userprojects,
                        'user_groups': self.request.user.groups.all()
                        })
        
        context.update(data)
        return context, kolekti

    
    def config(self):
        return self._config

    def process_svn_url(self, url):
        localpath = "file://%s/"%(settings.KOLEKTI_SVN_ROOT,)
        remotepath = "http://%s/svn/"%(settings.HOSTNAME,)
        return url.replace(localpath, remotepath)
    
    def projects_OLD(self):
        """List projects available for user"""
        projects = []
#        logger.debug(self.request.user.username)
        if settings.KOLEKTI_MULTIUSER:
            userprojects = UserProject.objects.filter(user = self.request.user)
        else:
            userprojects = UserProject.objects.all()
        for up in userprojects:
            project={
                'userproject':up,
                'name':up.project.name,
                'id':up.project.pk,
            }
            try:
                project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, up.project.directory)
                project_settings = ET.parse(os.path.join(project_path, 'kolekti', 'settings.xml')).getroot()
                if project_settings.xpath('string(/settings/@version)') != '0.7':
                    continue
                project.update({'languages':[l.text for l in project_settings.xpath('/settings/languages/lang')],
                                'defaultlang':project_settings.xpath('string(/settings/@sourcelang)')})
            except:
                continue


            try:
                from kolekti.synchro import SynchroManager
                synchro = SynchroManager(project_path)
                projecturl = synchro.geturl()
                project.update({"status":"svn","url":self.process_svn_url(projecturl)})
            except ExcSyncNoSync:
                project.update({"status":"local"})
            projects.append(project)
            
        return sorted(projects, key=lambda p: p.get('name').lower())

    def get_sync_manager(self, kolekti):
        from kolekti.synchro import SynchroManager
        sync = SynchroManager(kolekti.syspath(''))
        return sync
        
    def localname(self,e):
        return re.sub('\{[^\}]+\}','',e.tag)
    
    def get_jobs(self, kolekti):
        res = []
        for job in kolekti.iterjobs:
            xj = kolekti.parse(job['path'])
            profiles = []
            scripts  = []
            
            for p in xj.xpath('/job/profiles/profile'):
                label = p.find('label').text
                enabled = p.get('enabled')
                profiles.append((label, enabled))
                
            for s in xj.xpath('/job/scripts/script'):
                try:
                    label = s.find('label').text
                except:
                    continue
                enabled = s.get('enabled')
                scripts.append((label, enabled))
                
            job.update({'profiles': profiles,
                        'scripts':scripts,
                        })
            res.append(job)
        return sorted(res, key = lambda j: j['name'])

    def format_iterator(self, sourceiter, project):
        template = get_template('publication-iterator.html')
        nbchunck = 0
        for chunck in sourceiter:
            logger.debug(chunck)
            nbchunck += 1
            chunck.update({'id':nbchunck,'project':project})
            yield template.render(chunck)
        

    def set_extension(self, path, default):
        if os.path.splitext(path)[1] == "":
            path = path + default
        return path
    
class HomeView(kolektiMixin, TemplateView):
    template_name = "home.html"
    def get(self, request):
        context, kolekti = self.get_context_data()
        projects = context['user_projects']
        for project in projects:
            project_dir = project.project.directory
            project_path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project_dir)
            if os.path.exists(os.path.join(project_path, '.svn')):
                try:
                    from kolekti.synchro import SynchroManager
                    synchro = SynchroManager(project_path)
                    projecturl = synchro.geturl()
                    
                    project.extra = {"status":"svn", "url":self.process_svn_url(projecturl)}
                except ExcSyncNoSync:
                    project.extra = {"status":"local"}

            else:
                project.extra = {'status':'local'}
                                  
        try:
            request.user.groups.get(name=u'translator')
            return HttpResponseRedirect(reverse('translators_home')) 
        except ObjectDoesNotExist:
            return self.render_to_response(context)

class ProjectHomeView(kolektiMixin, TemplateView):
    template_name = "project_home.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        return self.render_to_response(context)


class ProjectsView(kolektiMixin, TemplateView):
    template_name = "projects.html"

    def post(self, request):
        # create new project
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username)

        if project_url=="":
        # create local project
            #sync.export_project(project_folder)
            try:
                self.create_project(project_folder, settings.KOLEKTI_BASE)
                self.project_activate(project_folder)
            except:
                logger.exception('unable to create new project')
                return self.get(request,project_folder=project_folder, error="Erreur à la création du projet")
        else:
            try:
                sync.checkout_project(project_folder, project_url)
            except ExcSyncNoSync:
                logger.exception('unable to checkout project')
                return self.get(request, require_svn_auth=True, project_folder=project_folder, project_url=project_url, error="Erreur à la récupération du projet")
            
        project = Project(
            name = project_folder,
            description = "Kolekti project %s"%project_folder,
            directory = project_folder,
            owner = User.objects.get(),
            template = None,
            )
        project.save()
                              
        up = UserProject(
            user = User.objects.get(),
            project = project,
            is_saas = False,
            is_admin = True,
            )
        up.save()
        
        return self.get(request)
        
            

# class ProjectsConfigView(kolektiMixin, TemplateView):
class ProjectLanguagesView(ProjectsView):
    template_name = "project-languages.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        
        context.update({
            "languages"   :kolekti.project_languages_labels(),
            "default_lang":kolekti.project_default_language()
            })
        return self.render_to_response(context)

    def post(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        
        project_settings = kolekti.project_settings
        langs = request.POST.getlist('sources[]',[])
        project_settings.set('sourcelang', request.POST.get('default_source','en'))
        xlangs = project_settings.find('languages')
        if xlangs is None:
            xlangs = ET.SubElement(project_settings, 'languages')
        else:
            for l in xlangs:
                xlangs.remove(l)
        for lang in langs:
            xl = ET.SubElement(xlangs,'lang')
            code, label = lang.split(':')
            xl.text = code
            xl.set('label', label)

        kolekti.write_project_config()
        
        return HttpResponse('ok',content_type="text/plain")
#        return HttpResponseRedirect(reverse('kolekti_languages_edit', kwargs={'project': project}))

        
class PublicationsListJsonView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        kolekti = context['kolekti']
        context.update({
        "publications":  kolekti.get_publications()
            })
        return HttpResponse(json.dumps(context),content_type="application/json")

class PublicationsZipView(kolektiMixin, View):
    def get(self,request, project):
        context, kolekti = self.get_context_data({'project':project})
        kolekti = context['kolekti']
        path = request.GET.get('path')
        zipname = path.split('/')[-1]
        try:
            response = HttpResponse(self.zip_publication(path),content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename=%s.zip'%zipname
            return response
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=404)

class ReleaseLangPublicationsListJsonView(kolektiMixin, View):

    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        publications = kolekti.get_releases_publications()
        return HttpResponse(json.dumps(publications),content_type="application/json")
        

class ReleaseZipException(Exception):
    pass
    
class ReleaseArchiveView(kolektiMixin, TemplateView):
    def get(self, request, project, release):
        context, kolekti = self.get_context_data({'project':project})
        now = time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
        meta = ET.XML('<meta/>')
        ET.SubElement(meta, 'zipdate').text = now
        ET.SubElement(meta, 'ziptime').text = str(time.time())
        ET.SubElement(meta, 'project').text = project
        try:
            response = HttpResponse(kolekti.zip_release_full('/releases/'+release, meta), content_type="application/zip")#, meta = meta.getroot())
            response['Content-Disposition'] = 'attachment; filename=%s_%s.zip'%(release, now)
            add_never_cache_headers(response)
            return response
        except:
            logger.exception('error while creating zip')
            return HttpResponse(status=404)

    template_name = 'releases/publish-archive.html'


    def post(self, request, project):
        form = UploadFileForm(request.POST, request.FILES)
        context, kolekti = self.get_context_data({'project':project})
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            path = '/tmp'
            if kolekti.exists(path):
                kolekti.rmtree(path)
            kolekti.makedirs(path)
            zippath = path +'/'+ uploaded_file.name
            kolekti.write_chunks(uploaded_file.chunks, zippath, mode = "wb", sync=False)
            try:
#                logger.debug(kolekti.getOsPath(zippath))
                with ZipFile(kolekti.getOsPath(zippath)) as zippy:
                    for f in zippy.namelist():
                        zippy.extract(f, kolekti.getOsPath(path))
                        
                if not kolekti.exists(path + "/kolekti"):
                    newpath = None
                    if kolekti.exists(path + "/config/config.xml"):
                        lang = kolekti.read(path +'/lang').strip()
                        converter = convert06.Converter(lang, kolekti.getOsPath(path))
                        releasename = converter.convert_enveloppe({
                            'enveloppe': kolekti.getOsPath(zippath),
                            'target_project':kolekti.getOsPath('/')
                            }, 'tmp')
                        newpath = "/tmp/" + releasename

                    else:
                        for f in kolekti.list_directory(path):
                            if kolekti.exists(path + "/" + f + "/kolekti"):
                                newpath = "/tmp/"+f
                                break;
                        
                            if kolekti.exists(path + "/" + f + "/config/config"):
                                newpath = "/tmp/"+f
                                lang = kolekti.read(newpath +'/lang').strip()
                                converter = convert06.Converter(lang, kolekti.getOsPath(path))
                                converter.convert_enveloppe({
                                    'enveloppe': kolekti.getOsPath(zippath),
                                    'target_project': kolekti.getOsPath('/')
                                    }, "tmp/"+f)
                            break;

                    if newpath is None:
                        context.update({'error':"Dossier kolekti non trouvé dans l'archive"})
                        raise ReleaseZipException
                    else:
                        path = newpath

                if not kolekti.exists(path + "/sources"):
                    context.update({'error':"Dossier sources non trouvé dans l'archive"})
                    raise ReleaseZipException
                    
                release_name = None
                for f in kolekti.list_directory(path + '/kolekti/publication-parameters'):
                    if f[-8:] == '_asm.xml':
                        release_name = f[:-8]
                        break
                    
                if release_name is None:
                    context.update({'error':"Paramètres de publication non trouvés dans l'archive"})
                    raise ReleaseZipException
                
                if not (path == '/tmp/' + release_name):
                    kolekti.makedirs('/tmp/' + release_name)
                    kolekti.move_resource(path + '/kolekti', '/tmp/' + release_name)
                    kolekti.move_resource(path + '/sources', '/tmp/' + release_name)
                    path = '/tmp/'+release_name
                
                try:
                    pp = kolekti.parse(path + '/kolekti/publication-parameters/' +release_name + "_asm.xml")
                except:
                    context.update({'error':"Paramètres de publication non valides"})
                    raise ReleaseZipException
                    
                langs = []
                for ll in kolekti.list_directory(path + "/sources"):
                    if ll == "share":
                        continue
                    if kolekti.exists(path + "/sources/" + ll + "/assembly/" + release_name + "_asm.html"):
                        langs.append(ll)
                if len(langs) == 0:
                    context.update({'error':"Aucun assemblage trouvé dans l'archive"})
                    raise ReleaseZipException

                
                
                context.update({
                    "path":path,
                    "langs":langs,
                    "release_name":release_name,
                    "profiles":pp.xpath('/job/profiles/profile[@enabled="1"]/label/text()'),
                    "scripts":pp.xpath('/job/scripts/script[@enabled="1"]/label/text()'),
                    })
                
            except ReleaseZipException:
                logger.exception('Invalid Zip structure')
                return self.render_to_response(context)
            except convert06.ConvertException, e:
                logger.exception('Unable to convert master')
                context.update({'error':e.msg})
                return self.render_to_response(context)
            except:
                logger.exception('could not unzip')
                context.update({'error':"Impossible de décompresser l'archive"})
                return self.render_to_response(context)            
        else:
            context.update({'error':form.errors})
        return self.render_to_response(context)            
        
class TocsListView(kolektiMixin, TemplateView):
    template_name = 'tocs/list.html'
    
class TocEditView(kolektiMixin, TemplateView):
    template_name = "tocs/detail.html"

    def get(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        toc_file = toc_path.split('/')[-1]
        toc_display = os.path.splitext(toc_file)[0]
        toc_path_project = '/'.join(['/sources', lang, 'tocs', toc_path])
        xtoc = kolekti.parse(toc_path_project)
        toc_meta = {}
        toc_title = xtoc.xpath('string(/html:html/html:head/html:meta[@name="DC.title"]/@content)', **ns)
        toc_author = xtoc.xpath('string(/html:html/html:head/html:meta[@name="DC.author"]/@content)', **ns)
        if len(toc_title) == 0:
            toctitle = xtoc.xpath('string(/html:html/html:head/html:title)', **ns)
        for meta in xtoc.xpath('/html:html/html:head/html:meta', **ns):
            if meta.get('name',False):
                toc_meta.update({meta.get('name').replace('.','_'): meta.get('content')})
        toc_job = xtoc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', **ns)
        xsl = kolekti.get_xsl('django_toc_edit', extclass = PublisherExtensions, lang = lang)
        try:
            etoc = xsl(xtoc)
        except:
            logger.exception('error: toc edit \n %s \n', xsl.error_log)
            raise Exception, xsl.error_log

        context.update({'toc_file':toc_file,
                        'toc_display':toc_display,
                        'toc_title':toc_title,
                        'toc_author':toc_author,
                        'toc_content':etoc,
                        'toc_path':toc_path,
                        'toc_meta':toc_meta})
        context.update({'jobs':self.get_jobs(kolekti)})
        return self.render_to_response(context)
    
    def post(self, request, project, lang, toc_path):
        try:
            context, kolekti = self.get_context_data({'project':project, 'lang':lang})
            xtoc = kolekti.parse_string(request.body)
            toc_path_project = '/'.join(['/sources', lang, 'tocs', toc_path])
            xtoc_save = kolekti.get_xsl('django_toc_save')
            xtoc = xtoc_save(xtoc)
            kolekti.write(str(xtoc), toc_path_project)
            return HttpResponse(json.dumps({"status":"ok"}),content_type="application/json")
        except:
            import traceback
            logger.exception('could not save toc')
            return HttpResponse(json.dumps({'status':'error', 'message':'erreur lors de la sauvegarde de la trame', 'stacktrace':traceback.format_exc()}),content_type="application/json")

class TocCreateView(kolektiMixin, View):
    def post(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        toc_path_project = '/'.join(['/sources', lang, 'tocs', toc_path])
        tocpath = self.set_extension(toc_path_project, ".html")
        toc = kolekti.parse_html_string("""<?xml version="1.0"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>toc</title></head>
  <body></body>
</html>""")
        kolekti.xwrite(toc, tocpath)
        return HttpResponse(json.dumps(kolekti.path_exists(tocpath)),content_type="application/json")


class TocUsecasesView(kolektiMixin, View):
    def get(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project': project, 'lang': lang})
        pathes = request.GET.getlist('pathes[]',[])
        result = {}
        for toc in kolekti.itertocs:
            xtoc = kolekti.parse(toc)
            for path in pathes:
                if len(xtoc.xpath('//html:a[@href="%s"]'%path, **ns)):
                    try:
                        result[path].append(toc)
                    except:
                        result[path]=[toc]
        return HttpResponse(json.dumps(result), content_type="application/json")



        
class TocPublishView(kolektiMixin, TemplateView):
    template_name = "publication.html"
    def post(self, request, project, lang, toc_path):
        try:
            logger.debug('publish')
            context, kolekti = self.get_context_data({'project': project, 'lang':lang})
            jobpath = request.POST.get('job')
            pubdir  = request.POST.get('pubdir')
            pubtitle= request.POST.get('pubtitle')
            profiles = request.POST.getlist('profiles[]',[])
            scripts = request.POST.getlist('scripts[]',[])
            context={}
            xjob = kolekti.parse(jobpath)
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
                else:
                    jprofile.set('enabled',"1")
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.find('label').text in scripts:
                    jscript.getparent().remove(jscript)
                else:
                    jscript.set('enabled',"1")

            xjob.getroot().set('pubdir',pubdir)
            
            p = publish.DraftPublisher(kolekti.syspath(), lang=lang)
            toc_project_path = "/".join(['','sources', lang, 'tocs', toc_path])
            return StreamingHttpResponse(self.format_iterator(p.publish_draft(toc_project_path, xjob, pubtitle), project), content_type="text/html")
        
        except:
            import traceback
            logging.exception('publication error')
            context.update({'success':False})
            context.update({'stacktrace':traceback.format_exc()})
            return self.render_to_response(context)

class ReleaseMixin(object):
    def release_iter(self, kolekti, lang, tocpath, xjob):
        r = publish.Releaser(kolekti.syspath(), lang = lang)
        pp = r.make_release(tocpath, xjob)
        release_dir = pp[0]['assembly_dir'][:-1]
        yield {
            'event':'release',
            'ref':release_dir,
            'release':pp[0]['releasedir'],
            'time':pp[0]['datetime'],
            'lang':lang,
        }
        if r.syncMgr is not None :
            r.syncMgr.propset("release_state","sourcelang","/".join([release_dir,"sources",lang,"assembly",pp[0]['releasedir']+'_asm.html']))
        else:
            logger.debug('no sync manager to set assembly property')
        p = publish.ReleasePublisher(release_dir, kolekti.syspath(), langs=[lang])
        for e in p.publish_assembly(pp[0]['pubname']):
            yield e

    def release_statuses(self, kolekti, release):
        release_languages = kolekti.project_languages()
        states = []
        for lang in release_languages:
            asfilename = "/".join(['/releases',release,"sources",lang,"assembly",release+'_asm.html'])
            sync = self.get_sync_manager(kolekti)
            state = sync.propget("release_state",asfilename)
            asfilename = "/".join(['/releases',release,"sources",lang,"assembly",release+'_asm.html'])
            try:
                state = sync.propget("release_state",asfilename)
            except:
                logger.exception('could not get release state')
                state = None
            if state is None:
                if kolekti.exists(asfilename):
                    states.append((lang, "local"))

            if state == "source_lang":
                states.insert(0,(lang, state))
            else:
                states.append((lang, state))
        return states
        
class TocReleaseView(kolektiMixin, ReleaseMixin, TemplateView):
    template_name = "publication.html"                                                                              
    def post(self, request, project, lang, toc_path):
        logger.debug('create release')
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        jobpath = request.POST.get('job')
        release_name  = request.POST.get('release_name')
        release_index  = request.POST.get('release_index')
        release_prev_index  = request.POST.get('release_prev_index')
        pubdir  = "%s_%s"%(release_name, release_index)
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        xjob = kolekti.parse(jobpath)
        
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
                else:
                    jprofile.set('enabled',"1")

            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.find('label').text in scripts:
                    jscript.getparent().remove(jscript)
                else:
                    jscript.set('enabled',"1")

            xjob.getroot().set('pubdir',pubdir)
            xjob.getroot().set('releasename',release_name)
            xjob.getroot().set('releaseindex',release_index)
            if not (release_prev_index is None):
                xjob.getroot().set('releaseprevindex',release_prev_index)
            toc_project_path = "/".join(['','sources', lang, 'tocs', toc_path])                        
            return StreamingHttpResponse(self.format_iterator(self.release_iter(kolekti, lang, toc_project_path, xjob), project))
        except:
            logger.exception('Error when creating release')
            import traceback
            context.update({'success':False})
            context.update({'stacktrace':traceback.format_exc()})
            return self.render_to_response(context)



        
class ReleaseListView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"

class ReleaseStatesView(kolektiMixin, ReleaseMixin, TemplateView):
    def get(self, request, project, release):
        context, kolekti = self.get_context_data({'project':project})
        states = self.release_statuses(kolekti, release)
        return HttpResponse(json.dumps(states),content_type="application/json")

class ReleaseDeleteView(kolektiMixin, View):
    def post(self, request, project, release):
        context, kolekti = self.get_context_data({'project': project})
        try:
            kolekti.delete_resource('/releases/%s'%(release,))
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            logger.exception("Could not delete release")
            return HttpResponse(status=500)
            
class ReleaseLangDeleteView(kolektiMixin, View):
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            kolekti.delete_resource('/releases/%s/sources/%s'%(release, lang))
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            logger.exception("Could not delete release lang")
            return HttpResponse(status=500)
            
    
class ReleaseLangStateView(kolektiMixin, TemplateView):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        sync = self.get_sync_manager(kolekti)

        if sync is None:
            state = "unknown"
        else:
            state = sync.propget("release_state","/".join(['/releases',release,"sources",lang,"assembly",release+'_asm.html']))
        return HttpResponse(state)

    def post(self,request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        sync = self.get_sync_manager(kolekti)

        try:
            state = request.POST.get('state')
            assembly = "/".join(['/releases', release, "sources", lang, "assembly", release + '_asm.html'])
            sync.propset("release_state",state, assembly)
            return HttpResponse(state)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
                    
class ReleaseLangFocusView(kolektiMixin, TemplateView):
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            state = request.POST.get('state')
            try:
                rf = ReleaseFocus.objects.get(release = release, assembly = release, lang = lang)
            except ReleaseFocus.DoesNotExist:
                rf = ReleaseFocus(release = release, assembly = release, lang = lang)
            rf.state = (state == "true")
            rf.save()
            return HttpResponse(json.dumps({"status":"OK"}), content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
                    
class ReleaseLangCopyView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        dstlang = lang
        try:
            srclang = request.POST.get('release_copy_from_lang')
            #            return StreamingHttpResponse(
            for copiedfiles in kolekti.copy_release(release, srclang, dstlang):
                pass
            assembly = "/".join(['/releases', release , "sources" , dstlang , "assembly" , release+'_asm.html'])

            sync = self.get_sync_manager(kolekti)

            sync.propset("release_state",'edition', assembly)
            sync.propset("release_srclang", srclang, assembly)
            # self.syncMgr.commit(path,"Revision Copy %s to %s"%(srclang, dstlang))

        except:
            logger.exception('could not copy source release')
    
        return HttpResponseRedirect(reverse('kolekti_release_lang_detail', kwargs={
            'project':project,
            'release':release,
            'lang':dstlang
            }))

class ReleaseLangAssemblyView(kolektiMixin, TemplateView):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            assembly_path = '/'.join(['','releases',release,"sources",lang,"assembly",release+"_asm.html"])
            xassembly = kolekti.parse(assembly_path.replace('{LANG}', lang))
            body = xassembly.xpath('/html:html/html:body/*', **ns)
            xsl = kolekti.get_xsl('django_assembly_edit')
            content = ''.join([str(xsl(
                t,
                path="'/%s/releases/%s'"%(project, release),
                release ="'%s'"%release,
                project ="'%s'"%project,
                )) for t in body])
        except:
            logger.exception('could get release assembly')
            
        return HttpResponse(content)
    

class ReleaseLangPublicationsView(kolektiMixin, TemplateView):
    template_name = "releases/publications.html"
    
    def __release_publications(self, kolekti, release, lang):
        publications = []
        try:
            mf = json.loads(self.read("/releases/" + release_path + "/manifest.json"))
            for event in mf:
                if event.get('event','') == "release_publication":
                    for event2 in event.get('content'):
                        if event2.get('event','') == "lang" and event2.get('label','') == lang:
                            publications.extend(event2.get('content'))
        except:
            import traceback
            print traceback.format_exc()
        return publications

    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({
            'project': project,
            'lang':lang
            })
        context.update({'publications':self.__release_publications(kolekti, release, lang)})

        return self.render_to_response(context)
                
class ReleaseLangDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"

    def __has_valid_actions(self,  kolekti, release):
        xjob = kolekti.parse('/releases/' + release + '/kolekti/publication-parameters/'+ release +'_asm.xml')
        return len(xjob.xpath('/job/scripts/script[@enabled="1"]/validation/script')) > 0

    def __release_indices_(self,  kolekti, release, lang):
        current = release
        try:
            while True:
                logger.debug('previous %s', str(current))
                release_info = json.loads(kolekti.read('/releases/'+current+'/release_info.json'))
                current = release_info['releaseprev']
                if current is None:
                    return               
                yield current
                
        except IOError:
            return

    def __release_indices(self,  kolekti, release, lang):
        release_info = json.loads(kolekti.read('/releases/'+ release +'/release_info.json'))
        release_name = release_info['releasename']
        for r in kolekti.list_directory('/releases'):
            if r == release:
                continue
            try:
                other_release_info = json.loads(kolekti.read('/releases/'+r+'/release_info.json'))
                if other_release_info['releasename'] == release_name:
                    a = '/releases/'+ r +'/sources/' + lang + "/assembly/" + r + "_asm.html"
                    logger.debug(a)
                    if kolekti.exists(a):
                        yield r 
            except IOError:
                pass
        return
    
    def get_context_data(self, data={}, **kwargs):
        context, kolekti = super(ReleaseLangDetailsView, self).get_context_data(data, **kwargs)
        states = []
        focus = []
        release = context.get('release')
        langstate = None
        sync = self.get_sync_manager(kolekti)
        release_languages = kolekti.project_languages()
        default_srclang = kolekti.project_default_language()
        for lang in release_languages:
            tr_assembly_path = '/'.join(['','releases',release,"sources",lang,"assembly",release+'_asm.html'])
#            logger.debug(kolekti.path_exists(tr_assembly_path))
#            logger.debug(tr_assembly_path)
            if kolekti.path_exists(tr_assembly_path):
                if (sync is not None):
                    states.append(sync.propget('release_state',tr_assembly_path))
                else:
                    states.append("local")
                    
            else:
                states.append("unknown")
            if lang == context.get('lang', default_srclang):
                langstate = states[-1]
            try:
                focus.append(ReleaseFocus.objects.get(release = release, assembly = assembly_name, lang = lang).state)
            except:
                focus.append(False)
                #        logger.debug(release_languages)
                #        logger.debug(states)
                #        logger.debug(focus)
        indices = list(self.__release_indices(kolekti, release, context.get('lang', default_srclang)))

        context.update({
            'langstate':langstate,
            'langstates':zip(release_languages,states,focus),
            'release_indices':sorted(indices)
            })

        return context, kolekti
    
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project, 'release':release, 'lang':lang})
#        logger.debug(context)
        assembly_path = '/'.join(['','releases',release,"sources",lang,"assembly",release+"_asm.html"])
        assembly_meta = {}
        variables_path = '/'.join(['','releases',release,"sources",lang,"variables"])
        pictures_path = '/'.join(['','releases',release,"sources",lang,"pictures"])
        try:
            xassembly = kolekti.parse(assembly_path)
            for meta in xassembly.xpath("/h:html/h:head/h:meta",namespaces = {"h":"http://www.w3.org/1999/xhtml"}):
                if meta.get('name') is not None:
                    assembly_meta.update({meta.get('name').replace('.','_'):meta.get('content')})
        except IOError:
            pass
        except ET.XMLSyntaxError, e:
            context, kolekti = self.get_context_data({
                'project':project,
                'lang':lang,                
                'success':False,
                'release_path':release_path,
                'assembly_name':assembly_name,
                'error':e,
            })
            return self.render_to_response(context)

        try:
            sync = self.get_sync_manager(kolekti)
            srclang = sync.propget('release_srclang', assembly_path)
        except:
            srclang = kolekti.project_default_language()

        if srclang is None:
            srclang = kolekti.project_default_language()
            
        parameters = kolekti.parse('/'.join(['/releases',release,"kolekti","publication-parameters",release+"_asm.xml"]))
        profiles = []
        for profile in parameters.xpath('/job/profiles/profile[@enabled="1"]'):
            profiles.append({
                'label':profile.find('label').text,
                'criteria':kolekti.get_criteria_dict(profile)
                })
        scripts = []
        for script in parameters.xpath('/job/scripts/script[@enabled="1"]'):
            scripts.append(script.find('label').text)
            #print self.get_assembly_edit(assembly_path)
            
        context.update({
            'releasesinfo':kolekti.release_details(release, lang),
            'releaseparams':{'profiles':profiles, 'scripts':scripts},
            'success':True,
            'release_path':release,
            'assembly_name':release,
            'assembly_meta':assembly_meta,
            'relang':lang,
            'lang':'en',
            'srclang':srclang,
            'validactions':self.__has_valid_actions(kolekti, release),
            'has_variables':kolekti.exists(variables_path),
            'has_pictures':kolekti.exists(pictures_path),
            
        })
        
        return self.render_to_response(context)
    
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})

        assembly_path = '/'.join(['/releases/',release,'sources',lang,'assembly',release+'_asm.html'])
        payload = request.FILES.get('upload_file').read()
        try:
            xassembly = kolekti.parse_string(payload)

        except ET.XMLSyntaxError, e:
            context, kolekti = self.get_context_data({
                'project':project,
                'lang':lang,
                'release_path':release_path,
                'assembly_name':assembly_name,
                'error':e,
            })
            return self.render_to_response(context)
            
        xsl = self.get_xsl('django_assembly_save')
        xassembly = xsl(xassembly, prefixrelease='"%s"'%release)
        
        kolekti.update_assembly_lang(xassembly, lang)
        kolekti.xwrite(xassembly, assembly_path)

        sync = self.get_sync_manager(kolekti)
        try:
            srclang = sync.propget('release_srclang', assembly_path)
        except:
            srclang = kolekti.project_srclang

        context.update({
            'releasesinfo':kolekti.release_details(release, lang),
            'success':True,
            'release_path':release,
            'assembly_name': release,
            'lang':lang,
            'srclang':srclang,
        })
        return self.render_to_response(context)


class ReleasePublishView(kolektiMixin, TemplateView):
    template_name = "publication.html"
    def post (self, request, project, release):        
        context, kolekti = self.get_context_data({'project':project})
        langs = request.POST.getlist('langs[]')
        prefix = request.POST.get('prefix', '/releases/')
        try:
            logger.debug(langs)
            p = publish.ReleasePublisher(prefix + release, kolekti.syspath(), langs=langs)
            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(release + "_asm"), project), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)
    
class ReleaseLangPublishView(kolektiMixin, TemplateView):
    template_name = "publication.html"
    def post (self, request, project, release, lang):        
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        try:
            p = publish.ReleasePublisher('/releases/'+release, kolekti.syspath(), langs=[lang])
            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(release + "_asm"), project), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

class ReleaseLangValidateView(kolektiMixin, View):
    def post (self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project,'lang':lang})

#        jobpath = release + '/kolekti/publication-parameters/' + assembly + '.xml'
#        print jobpath
#        xjob = kolekti.parse(jobpath)
        try:
            p = publish.ReleasePublisher(release_path, kolekti.syspath(), langs=[lang])
            return StreamingHttpResponse(self.format_iterator(p.validate_release(), project), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)


class ReleaseUpdateView(kolektiMixin, ReleaseMixin, View):
    def post(self, request, project, release):
        new_index = request.POST.get('index')
        from_sources = (request.POST.get('from_sources', 'false') == "true")
        logger.debug(from_sources)
        context, kolekti = self.get_context_data({'project': project})
        releaseinfo = json.loads(kolekti.read('/releases/'+release+'/release_info.json'))
        majorname = releaseinfo.get('releasename')
        old_index = releaseinfo.get('releaseindex')
        
        new_release = '%s_%s'%(majorname, new_index)
        
        if kolekti.exists('/releases/%s'%(new_release,)):
            logger.warning("Already exists")
            return HttpResponse(
                json.dumps({'status':'E', "msg":'l´indice %s existe' }),
                content_type="application/json",
                status=403
                )
                    
        tocpath = releaseinfo.get('toc')        
        states = self.release_statuses(kolekti, release)
       
        for key, val in states:
            logger.debug("state %s, %s",key, val)
            if val == "sourcelang":
                srclang = key
        try:
            if from_sources:
                jobpath = '/releases/' + release + '/kolekti/publication-parameters/' + release + '_asm.xml'
                xjob = kolekti.parse(jobpath)
                rootjob = xjob.getroot()
                rootjob.set('pubdir', new_release)
                rootjob.set('releasename',majorname)
                rootjob.set('releaseindex' , new_index)
                rootjob.set('id', '%s_asm.xml'%(new_release,))
                self.release_iter(kolekti, srclang, tocpath, xjob)
                r = publish.Releaser(kolekti.syspath(), lang = srclang)
                r.make_release(tocpath, xjob)
            else:
                kolekti.duplicate_release(majorname, old_index, new_index)
                
        except:
            logger.exception("Could not update release")
            return HttpResponse(status=500)

        # initialise les langues
        assembly = "/".join(['/releases', new_release , "sources" , srclang , "assembly" , new_release+'_asm.html'])
        
        sync = self.get_sync_manager(kolekti)
        
        sync.propset("release_state",'sourcelang', assembly)
        
        for key, val in states:
            if val == "sourcelang":
                continue
            if val is None:
                continue

            dstlang = key

            logger.debug("state %s, %s",key, val)
            
            for copiedfile in kolekti.copy_release(new_release, srclang, dstlang):
                logger.debug(copiedfile)
            assembly = "/".join(['/releases', new_release , "sources" , dstlang , "assembly" , new_release+'_asm.html'])

            sync.propset("release_state",'edition', assembly)
            sync.propset("release_srclang", srclang, assembly)
            # self.syncMgr.commit(path,"Revision Copy %s to %s"%(srclang, dstlang))

        return HttpResponse(json.dumps("ok"), content_type="text/javascript")


        
class TopicsListView(kolektiMixin, TemplateView):
    template_name = "topics/list.html"

class TopicTemplateListView(kolektiMixin, TemplateView):
    template_name = "topics/templates.html"

class PicturesListView(kolektiMixin, TemplateView):
    template_name = "illustrations/list.html"

class PictureUploadView(kolektiMixin, TemplateView):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            path = request.POST['path']
            kolekti.write_chunks(uploaded_file.chunks, path +'/'+ uploaded_file.name, mode = "wb") 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class PictureDetailsView(kolektiMixin, TemplateView):
    template_name = "illustrations/details.html"
    def get(self, request, project, lang, picture_path):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        name = picture_path.rsplit('/',1)[-1]
        project_path =  '/sources/' + lang + '/pictures/' + picture_path
        ospath = kolekti.syspath(project_path)
        logger.debug(ospath)
        try:
            im = Image.open(ospath)
            context.update({
                'fileweight':"%.2f"%(float(os.path.getsize(ospath)) / 1024),
                'name':name,
                'path':'/' + project + project_path,
                'format':im.format,
                'mode':im.mode,
                'size':im.size,
                'info':im.info,
                })
        except:
            logger.exception('get image info failed')
            context.update({
                'name':name,
                'path':picture_path,
                })
        return self.render_to_response(context)




    
class VariablesListView(kolektiMixin, TemplateView):
    template_name = "variables/list.html"
    
class VariablesMixin(kolektiMixin):
    def getval(self, val):
        try:
            return val.find('content').text
        except AttributeError:
            return ""
        
    def variable_details(self, context, kolekti, release, lang, path, include_values = False):
        name = path.rsplit('/',1)[-1]
        variable_file = self.variables_file(release, lang, path) 
        xmlvar = kolekti.parse(variable_file) #'/sources/%s/variables/%s'%(lang, path))
        crits = [c.text[1:] for c in xmlvar.xpath('/variables/critlist/crit')]
        variables = xmlvar.xpath('/variables/variable/@code')
        values = xmlvar.xpath('/variables/variable[1]/value')
        conditions = [{
            'label':", ".join(["=".join((c.get('name'),c.get('value')))  for c in v.findall('crit')]) ,
            'expr':dict([(c.get('name'),c.get('value')) for c in v.findall('crit')])
            } for v in values]
            
        vardata = {
            "crits" : crits,
            "variables" : variables,
            "conditions" : conditions,
            "criteria" : kolekti.get_criteria_def_dict(include_lang = True),
            }
        if include_values:
            vardata.update({"values": [[self.getval(v) for v in var.xpath('value') ] for var in xmlvar.xpath('/variables/variable')]})
            
        context.update({
            "release" : release,
            'lang': lang,
            'name': name,
            'path': path,
            'vardata' : json.dumps(vardata),
            })
        context.update(vardata)
        return context

    def variables_file(self, release, lang, path):
        if release is None:
            path = "/sources/%s/variables/%s.xml"%(lang, path)
        else:
            path = "/releases/%s/sources/%s/variables/%s.xml"%(release, lang, path)
        return path

    
class VariablesPostMixin(VariablesMixin):        
    def post(self, request, project, lang, variable_path, release = None):
        try:
            context, kolekti = self.get_context_data({'project':project, 'lang':lang})
            variables_file = self.variables_file(release, lang, variable_path) 
            payload = json.loads(request.body)
#            varpath = payload.get('path')
            xvar = kolekti.parse(variables_file)
            for var, mvar in zip(xvar.xpath('/variables/variable'), payload.get('data')):
                for (val, mval) in zip(var.xpath('value/content'), mvar):
                    val.text = mval
            kolekti.xwrite(xvar, variables_file)
            return HttpResponse('ok')
        except:
            logger.exception('Could not save variable')
            return HttpResponse(status=500)
    
class VariablesDetailsView(VariablesMixin, TemplateView):
    template_name = "variables/details.html"
    def get(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang})
        try:
            self.variable_details( context, kolekti, release, lang, variable_path)
            return self.render_to_response(context)
        except:
            logger.exception('unable to process variable file')
            raise
        
    def post(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        variables_file = self.variables_file(release, lang, variable_path) 
        try:
            action = request.POST.get('action')
#            path = request.POST.get('path')

            xvar = kolekti.parse(variables_file)
            if action == "newvar":
                varname = request.POST.get('varname')
                varvalue = request.POST.get('varvalue')
                try:
                    firstvar = xvar.xpath('/variables/variable[1]')
                    newvar = ET.SubElement(xvar.xpath('/variables')[0],'variable', {"code":varname})
                    if len(firstvar):
                        for value in firstvar[0]:
                            newval = ET.SubElement(newvar, 'value')
                            for crit in value.xpath('crit'):
                                ET.SubElement(newval, 'crit',{
                                    "name":crit.get("name"),                            
                                    "value":crit.get("value")
                                    })
                            xcontent = ET.SubElement(newval,'content')
                            xcontent.text = request.POST.get('varvalue','')

                    else:
                        newval = ET.SubElement(newvar, 'value')
                        
                        xcontent = ET.SubElement(newval,'content')
                        xcontent.text = request.POST.get('varvalue','')
                except:
                    logger.exception('could not add variable')
                    
            if action == "delvar":
                index = int(request.POST.get('index'))
                delvar = xvar.xpath('/variables/variable[%d]'%index)[0]
                delvar.getparent().remove(delvar)
                
            if action == "renamevar":
                index = int(request.POST.get('index'))
                newname = request.POST.get('varname')
                var = xvar.xpath('/variables/variable[%d]'%index)[0]
                var.set('code', newname)
            
            if action == "newcond":
                crits = [c.text[1:] for c in xvar.xpath('/variables/critlist/crit')]
                for var in xvar.xpath('/variables/variable'):
                    if len(var.xpath('value/crit')):
                        xvalue = ET.SubElement(var,'value')
                        xcontent = ET.SubElement(xvalue,'content')
                        xcontent.text = request.POST.get('varvalue','')
                    else:
                        xvalue = var.find('value')
                    for entry in crits:
                        ET.SubElement(xvalue,'crit',{'name':entry, 'value':request.POST.get(entry)})

            if action == "editcond":
                index = int(request.POST.get('condindex'))
                for var in xvar.xpath('/variables/variable'):
                    for crit in var.xpath('value[%d]/crit'%index):
                        critcode = crit.get('name')
                        crit.set('value',request.POST.get(critcode))
                    
            if action == "delcond":
                index = int(request.POST.get('index'))
                if len(xvar.xpath('/variables/variable[1]/value')) == 1:
                    for xcond in xvar.xpath('/variables/variable/value/crit'):
                        xcond.getparent().remove(xcond)
                else:
                    for xcond in xvar.xpath('/variables/variable/value[%d]'%index):
                        xcond.getparent().remove(xcond)
                    
            if action == "newcrit":
                try:
                    critlist = xvar.xpath('/variables/critlist')[0]
                except IndexError:
                    critlist = ET.SubElement(xvar.xpath('/variables')[0],'critlist')
                critdecl = ET.SubElement(critlist, 'crit')
                critdecl.text = ":" + request.POST.get("crit")
                for xcond in xvar.xpath('/variables/variable/value'):
                    ET.SubElement(xcond, 'crit',{
                        "name":request.POST.get("crit"),                            
                        "value":request.POST.get("val")
                        })


            kolekti.xwrite(xvar, variables_file)                     
            return HttpResponseRedirect('')
        except:
            logger.exception('var action failed')                     
            raise
#        return self.render_to_response(self.variable_details(path))
        
class VariablesEditvarView(VariablesPostMixin, TemplateView):
    template_name = "variables/editvar.html"
    def get(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        self.variable_details(context, kolekti, release, lang, variable_path, True)
        index = int(request.GET.get('index',1)) - 1
        context.update({
            "method":"line",
            "current":index,
            })
        return self.render_to_response(context)
    

class VariablesEditcolView(VariablesPostMixin, TemplateView):
    template_name = "variables/editvar.html"
    def get(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
#        path = request.GET.get('path')

        index = int(request.GET.get('index', 1)) - 1
#        project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)
        self.variable_details(context, kolekti, release, lang, variable_path, True)
        context.update({
            "method":"col",
            "current":index,
            })
        return self.render_to_response(context)
    
    
class VariablesUploadView(VariablesMixin, TemplateView):
    def post(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            variables_file = self.variables_file(release, lang, variable_path) 

#            path = request.POST['path']
            converter = OdsToXML(kolekti.syspath())
            converter.convert(uploaded_file, variables_file)
            # self.write_chunks(uploaded_file.chunks,path +'/'+ uploaded_file.name) 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class VariablesCreateView(VariablesMixin, TemplateView):
    def post(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            variables_file = self.variables_file(release, lang, variable_path) 
            varx = kolekti.parse_string('<variables><critlist></critlist></variables>')
            kolekti.xwrite(varx, variables_file)
            return HttpResponse(json.dumps(kolekti.path_exists(variables_file)),content_type="application/json")
        except:
            logger.exception('could not create variable file')
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)

class VariablesODSView(VariablesMixin, View):
    def get(self, request, project, lang, variable_path, release=None):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        variables_file = self.variables_file(release, lang, variable_path)
        ods_path = variables_file.replace('.xml','.ods')
        filename = ods_path.rsplit('/',1)[-1]
        ods_file = StringIO()
        converter = XMLToOds(kolekti.syspath())
        converter.convert(ods_file, variables_file)
        response = HttpResponse(ods_file.getvalue(),
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        ods_file.close()
        return response


    
class ImportView(kolektiMixin, TemplateView):
    template_name = "import.html"
    def get(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        tpls = kolekti.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        
        context.update({'templates':tnames})
        return self.render_to_response(context)

    def post(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            uploaded_file = request.FILES[u'upload_file']
            filename = str(uploaded_file)

            importer = Importer(kolekti.syspath(), lang = lang)
            if(os.path.splitext(filename)[1] == '.ods'):
                events =  importer.importOds(uploaded_file)
            elif(os.path.splitext(filename)[1] == '.xlsx'):
                events =  importer.importXlsx(uploaded_file)
            else:
                import traceback
                events = [{
                'event':'error',
                'msg':"Erreur lors de l'import : type de fichier non supporté %s"%filename,
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }]
        else:
            import traceback
            events = [{
                'event':'error',
                'msg':"Erreur lors de l'import : pas de tableur",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }]
        context.update({'events':events})
        return self.render_to_response(context)
            
class ImportTemplateView(kolektiMixin, TemplateView):
    def get(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        template = request.GET.get('template')
        filename = "import_template.ods"
        odsfile = StringIO()
        tplter = Templater(kolekti.syspath(), lang=lang)
        tplter.generate("/sources/" + lang + "/templates/" + template, odsfile)
        response = HttpResponse(odsfile.getvalue(),                            
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response

    
class SettingsJsView(kolektiMixin, TemplateView):

    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})

        project_path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project)
        try:
            sync = self.get_sync_manager(kolekti)
            project_svn_url = sync.geturl()
        except ExcSyncNoSync:
            project_svn_url = "N/A"
            
        settings_js="""
        var kolekti = {
        "lang":"%s",
        "project":"%s",
        "project_svn_url":"%s"
        }
        """%(
            context.get('lang',''),
            project,
            self.process_svn_url(project_svn_url))
        return HttpResponse(settings_js,content_type="text/javascript")
    
class SettingsJsonView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"
    def get(self, request, project):
        context.get_context_data({
            'project': project,
            'kolekti':self._config,
            'kolektiversion' : self._kolektiversion
            })
        if request.kolekti_userproject is not None:
            context.update({
                'srclangs' : languages,
                'releaselangs' : kolekti.project_languages(),
                'default_srclang': kolekti.project_default_language(),
                'active_project_name' : self.request.kolekti_userproject.project.name,
                'active_srclang' : self.request.kolekti_userproject.srclang,
            })

        return HttpResponse(json.dumps(context),content_type="application/json")
        

class SettingsView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"

    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        return self.render_to_response(context)



class PublicationTemplatesView(kolektiMixin, TemplateView):
    template_name = "publication-templates/list.html"

class JobListView(kolektiMixin, TemplateView):
    template_name = "publication-parameters/list.html"


class JobCreateView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            path = request.POST.get('path')
            path = self.set_extension(path, ".xml")
            job = kolekti.parse_string('<job><criteria/><profiles/><scripts/></job>')
            kolekti.xwrite(job, path)
            return HttpResponse(json.dumps(kolekti.path_exists(path)),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
        

class JobEditView(kolektiMixin, TemplateView):
    template_name = "publication-parameters/job.html"

    def get(self, request, project, job_path):
        context, kolekti = self.get_context_data({'project': project})
        xjob = kolekti.parse('/kolekti/publication-parameters/' + job_path)
        xjob.getroot().append(copy(kolekti.project_settings))
        xjob.getroot().find('settings').append(copy(kolekti.get_scripts_defs()))
        ejob = None
        try:
            xscripts = kolekti.parse('/kolekti/pubscripts.xml').getroot()
            for pubscript in xscripts.xpath('/scripts/pubscript'):
                pubscript.set('type',"multi")
            xjob.getroot().find('settings').append(copy(xscripts))
        except:
            logger.exception('unable to get local script definitions')

        xsl = kolekti.get_xsl('django_job_edit', extclass=PublisherExtensions, lang=self.request.kolekti_userproject.srclang)
        try:
            ejob = xsl(xjob, path="'/kolekti/publication-parameters/%s'"%job_path, jobname="'%s'"%kolekti.basename(job_path))
        except:
            kolekti.log_xsl(xsl.error_log)
            logger.exception("could not apply xslt")
#            raise Exception, xsl.error_log
            
        context.update({'job':str(ejob)})
        context.update({'path':job_path})
        context.update({'name':kolekti.basename(job_path)})
        return self.render_to_response(context)

    def post(self, request, project, job_path):
        context, kolekti = self.get_context_data({'project': project})
        try:
            xjob = kolekti.parse_string(request.body)
            kolekti.xwrite(xjob, '/kolekti/publication-parameters/' + job_path)
            return HttpResponse('ok')
        except:
            logger.exception('job save failed')
            return HttpResponse(status=500)


class CriteriaView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        return HttpResponse(kolekti.project_settings, content_type="text/xml")

class CriteriaCssView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            xsl = kolekti.get_xsl('django_criteria_css')            
            return HttpResponse(str(xsl(kolekti.project_settings)), "text/css")
        except:
            logger.exception('generate criteria css failed')
            return HttpResponse(status=500)
        
class CriteriaJsonView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            criterias = kolekti.get_criteria_def_dict()
            return HttpResponse(json.dumps(criterias),content_type="application/json")
        except:
            logger.exception('generate criteria json failed')
            return HttpResponse(status=500)

    
                
class CriteriaEditView(kolektiMixin, TemplateView):
    template_name = "settings/criteria.html"

    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        criteria = []
        for xcriterion in kolekti.project_settings.xpath('/settings/criteria/criterion'):
            criteria.append(
                {'code':xcriterion.get('code'),
                'type':xcriterion.get('type'),
                'values':[str(v.text) for v in xcriterion.findall("value")]
                })
        context.update({'criteria':criteria})
        return self.render_to_response(context)
    
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            settings = kolekti.project_settings
            xcriteria = kolekti.parse_string(request.body)
            xsettingscriteria=settings.xpath('/settings/criteria')[0]
            for xcriterion in xsettingscriteria:
                xsettingscriteria.remove(xcriterion)
                
            for xcriterion in xcriteria.xpath('/criteria/criterion'):
                xsettingscriteria.append(xcriterion)
            kolekti.write_project_config()
            return HttpResponse('ok')
        except:
            logger.exception('criteria save failed')
            return HttpResponse(status=500)
   
class BrowserExistsView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        path = request.GET.get('path','/')
        
        return HttpResponse(json.dumps(kolekti.path_exists(path)),content_type="application/json")
        
class BrowserMkdirView(kolektiMixin, View):
    def post(self,request, project):
        context, kolekti = self.get_context_data({'project': project})
        path = request.POST.get('path','/')
        kolekti.makedirs(path, sync=True)
        return HttpResponse(json.dumps(kolekti.path_exists(path)),content_type="application/json")

class BrowserMoveView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        
        kolekti.move_resource(src, dest)
        return HttpResponse(json.dumps(kolekti.path_exists(dest)),content_type="text/plain")


class BrowserCopyView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        kolekti.copy_resource(src, dest)
        return HttpResponse(json.dumps(kolekti.path_exists(dest)),content_type="application/json")


class BrowserDeleteView(kolektiMixin, View):
    def post(self,request, project):
        context, kolekti = self.get_context_data({'project': project})
        path = request.POST.get('path','/')
        try:
            kolekti.delete_resource(path)
        except:
            logger.exception('delete resource failed')
            return HttpResponse(status=500)
        return HttpResponse(json.dumps(not(kolekti.path_exists(path))),content_type="application/json")

class BrowserView(kolektiMixin, TemplateView):
    template_name = "browser/main.html"
    def __browserfilter(self, entry):
        for exc in settings.RE_BROWSER_IGNORE:
            if re.search(exc, entry.get('name','')):
                return False
        return True

    def release_filter(self, entry):
        if entry.get('type','') == 'text/directory':
            pass
        return entry

    def get_directory(self, kolekti, path):
        return kolekti.get_directory(path)
    
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            path = request.GET.get('path','/')
            if not kolekti.exists(path):
                return self.render_to_response({'error':"Le chemin %s n'existe pas"%path})
            
            mode = request.GET.get('mode','select')
            try:
                files = filter(self.__browserfilter, self.get_directory(kolekti, path))
            
                for f in files:
                    fpath =  path[1:] + f.get('name')
                    if f.get('type','') == 'text/directory':
                        fpath = fpath + '/' 
                    f.update({                                               
                        'icon': fileicons.get(f.get('type'),"fa-file-o"),
                        'path': fpath,
                    })
                    context.update({'files':files})
            except OSError:
                logger.exception('Browser:Error getting files')
                context.update({'error':'%s does not exists'%path})
    
            pathsteps = []
            startpath = ""
            endpath = ""
            for step in path.split("/")[1:-1]:
                pathspec = {'parentpath':startpath}
                endpath = endpath + "/" + step
                if startpath == '/sources':
                    pathkind = path.split("/")[3]
                    pathspec.update({'langs': kolekti.context_languages('/sources', pathkind)})
                    endpath = ""
                startpath = startpath + "/" + step
                pathspec.update({'label':step, 'path': startpath})
                pathsteps.append(pathspec)
#            logger.debug(pathsteps)
            context.update({'pathsteps':pathsteps})
            context.update({'endpath':endpath})
            context.update({'mode':mode})
            context.update({'path':path})
#            context.update({'project':self.request.kolekti_userproject.project.directory})
            context.update({'id':'browser_%i'%random.randint(1, 10000)})
            response = self.render_to_response(context)
            
        except:
            logger.exception('unable to get directory')
            import traceback
            context={'error':True, 'stacktrace': traceback.format_exc() }
            response = self.render_to_response(context)
            
        add_never_cache_headers(response)
        return response
            
class BrowserReleasesView(BrowserView):
    template_name = "browser/releases.html"
    def get_directory(self, kolekti, path):
        try:
            releases = {}
#            logger.debug(kolekti)
            for assembly, date in kolekti.get_release_assemblies(path):
                item = {'name':assembly,
                        'type':"text/xml",
                        'date':date}
                try:
                    found = False
                    mf = json.loads(kolekti.read('/'.join([path, assembly, 'release_info.json'])))
                    releasename = mf.get('releasename')
                    releaseindex = mf.get('releaseindex')
                    
                    r = {'name':releaseindex, 'type':"text/xml", 'date':date}
                    try:
                        releases[releasename]['indexes'].append(r)
                        if date > releases[releasename]['date']:
                            releases[releasename]['date'] = date
                    except KeyError:
                        releases[releasename] = {
                            'name':releasename,
                            'type':"text/xml",                                   
                            'date':date,
                            'indexes':[r]}
                        found = True
                except:
                    releases[assembly]=item
#                    logger.exception('release list error')
#            logger.debug(releases)
            return releases.values()
#            return res
        except:
            logger.exception('release list error')
            return super(BrowserReleasesView, self).get_directory(kolekti, path)
        
            
class BrowserCKView(kolektiMixin, TemplateView):
    template_name = "browser/browser.html"
    def __browserfilter(self, entry):
        for exc in settings.RE_BROWSER_IGNORE:
            if re.search(exc, entry.get('name','')):
                return False
        return True
                         
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        path = request.GET.get('path','/')
        mode = request.GET.get('mode','select')
        client_filter_name = request.GET.get('filter',None)
        client_filter = None
        if client_filter_name is not None:
            client_filter = getattr(self, client_filter_name)
        try:
            files = filter(self.__browserfilter, kolekti.get_directory(path,client_filter))
            
            for f in files:
                f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
            context.update({'files':files})
            context.update({'status':'ok'})
        except OSError:
            context.update({'status':'error'})
            context.update({'msg':'%s does not exists'%path})
            
        pathsteps = []
        startpath = ""
        for step in path.split("/")[1:]:
            startpath = startpath + "/" + step
            pathsteps.append({'label':step, 'path': startpath})

        context.update({'pathsteps':pathsteps})
        context.update({'mode':mode})
        context.update({'path':path})
        context.update({'editor':request.GET.get('CKEditor','_')})
        context.update({'funcnum':request.GET.get('CKEditorFuncNum','_')})
        
        context.update({'id':'browser_%i'%random.randint(1, 10000)})
        return self.render_to_response(context)

class BrowserCKUploadView(kolektiMixin, TemplateView):
    template_name = "browser/main.html"

class BrowserUploadView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            path = request.POST['path']
            name = request.POST['name']
            payload = request.POST['file']
            data = base64.decodestring(payload)
            kolekti.write(data, path + "/" + name, mode="wb")
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


        

class TopicEditorView(kolektiMixin, TemplateView):
    template_name = "topics/edit-ckeditor.html"
    ttdir = "topics"
    
    def get(self, request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        topic_project_path = '/sources/%s/%s/%s'%(lang, self.ttdir, topic_path)
        topic = kolekti.read(topic_project_path)
        
        context.update({
            "body":topic,
            "title": kolekti.basename(topic_path),
            })
        return self.render_to_response(context)

    def post(self,request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            topic_project_path = '/sources/%s/%s/%s'%(lang, self.ttdir, topic_path)
            topic = request.body
            xtopic = kolekti.parse_string(topic)
            kolekti.write(topic, topic_project_path)
            return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")

        except:
            logger.exception('invalid topic structure')
            import traceback
            msg = traceback.format_exc().split('\n')[-2]
            return HttpResponse(json.dumps({'status':'error', 'msg':msg}), content_type="application/json")

class TopicMetaJsonView(kolektiMixin, View):
    def get(self, request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        xtopic = kolekti.parse(path.replace('{LANG}', lang))
        metaelts = xtopic.xpath('/h:html/h:head/h:meta[@name][@content]', namespaces={'h':'http://www.w3.org/1999/xhtml'})
        meta = [{'name':m.get('name'),'content':m.get('content')} for m in metaelts]
        return HttpResponse(json.dumps(meta), content_type="application/json")
    
class TopicCreateView(kolektiMixin, View):
    def post(self, request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            model_path = '/sources/'+ lang + "/templates/" + request.POST.get('model')
            topic_path = self.set_extension(topic_path, ".html")
            topic_project_path = '/sources/%s/topics/%s'%(lang, topic_path)
            topic = kolekti.parse_html(model_path)
            kolekti.xwrite(topic, topic_project_path)
        except XMLSyntaxError:
            logger.exception("Create topic error")
            import traceback
            return HttpResponse(json.dumps({'path':topic_path, 'error':traceback.format_exc()}), status = 500, content_type="application/json")
        except:
            logger.exception("Create topic error")
            import traceback
            return HttpResponse(json.dumps({'path':topic_path, 'error':traceback.format_exc()}), status = 500, content_type="application/json")
        
        return HttpResponse(json.dumps(topic_path), content_type="application/json")



class TopicTocView(kolektiMixin, View):
    def get(self, request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        topic_project_path = '/sources/%s/topics/%s'%(lang, topic_path)
        topic = kolekti.read(topic_project_path)

        xtopic = kolekti.parse(topic_project_path)
        body = xtopic.xpath('/html:html/html:body/*', **ns)
        xsl = kolekti.get_xsl('django_topic_toc')
        content = str(xsl(xtopic, path="'/%s/sources/%s/topics/%s'"%(project, lang, topic_path)))
        return HttpResponse(content,content_type="text/xml")
    
class TopicTemplatesView(kolektiMixin, View):
    def get(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            tpls = kolekti.get_directory(root = "/sources/"+lang+"/templates")
            tnames = [t['name'] for t in tpls]
        except OSError:
            tnames=[]
        return HttpResponse(json.dumps(tnames),content_type="application/json")

class TopicTemplateCreateView(kolektiMixin, View):
    def post(self, request):
        try:
            templatepath = request.POST.get('templatepath')
            templatepath = self.set_extension(templatepath, ".html")
            logger.debug(templatepath)
            topic = """<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta content="application/xhtml+xml; charset=UTF-8" http-equiv="content-type" />
      <title>Titre du module</title>
      <meta name="kolekti:version" content="0.8" />
      <link rel="stylesheet" type="text/css" href="/kolekti/stylesheets/editor.css" />
    </head>
<body>
</body>
"""
            self.write(topic, templatepath)
        except:
            import  traceback
            print traceback.format_exc()
        return HttpResponse(json.dumps(templatepath), content_type="application/json")

class TopicTemplateEditorView(TopicEditorView):
    ttdir = "templates"
    def get(self, request, project, lang, template_path):
        return super(TopicTemplateEditorView, self).get(request, project, lang, template_path)

    def post(self,request, project, lang, template_path):
        return super(TopicTemplateEditorView, self).post(request, project, lang, template_path)

class SearchFormView(kolektiMixin, TemplateView):
    template_name = "search/form.html"
    def get(self, request):
        context = self.get_context_data()
        form = SearchForm()
        context.update({'form':form})
        return self.render_to_response(context)
    
class SearchView(kolektiMixin, TemplateView):
    template_name = "search/results.html"
    def get(self, request, project, query, page=1):
        context, kolekti = self.get_context_data({'project':project})
        
        s = Searcher(kolekti.projectpath)
        results = s.search(q, page)
        context.update({"results":results})
        context.update({"page":page})
        context.update({"query":q})
        return self.render_to_response(context)



class SyncView(kolektiMixin, TemplateView):
    template_name = "synchro/main.html"
    def get(self, request, project):
        try:
            context, kolekti = self.get_context_data({'project':project})
            sync = self.get_sync_manager(kolekti)
            statuses = sync.statuses(recurse = False)
#            root_statuses = [statuses[i]['__self']['kolekti_status'] for i in statuses.keys()]
            context.update({
                    "history": sync.history(),
                    "changes": statuses,
#                    "root_statuses":root_statuses,
                    })
            logger.debug('render')
            
        except ExcSyncNoSync:
            logger.exception("Synchro unavailable")
            context.update({'status':'nosync'})
            
        except :
            logger.exception("Error in synchro")
            context.update({'status':'error'})
            
        return self.render_to_response(context)

    def post(self, request, project):
        try:
            context, kolekti = self.get_context_data({'project':project})
            sync = self.get_sync_manager(kolekti)
            action = request.POST.get('action')
            commitmsg = request.POST.get('commitmsg',u"").encode('utf-8')
            if len(commitmsg) == 0:
                commitmsg = "unspecified"
                
            if action == "conflict":
                resolve = request.POST.get('resolve')
                files = request.POST.getlist('fileselect',[])
                if resolve == "local":
                    sync.update(files)
                    for cfile in files:
                        if kolekti.exists(cfile+'.mine'):
                            kolekti.copyFile(cfile+'.mine', cfile)
                            self.delete_resource(cfile+'.mine', sync=False)
                        else:
                            raise Exception('impossible de trouver la version locale')
                        try:
                            sync.resolved(cfile)
                        except:
                            logger.exception('error while resolving conflict [use local]')
                            
                    sync.commit(files, commitmsg)
                
                if resolve == "remote":
                    try:
                        sync.revert(files)
                    except:
                        logger.exception('impossible to revert')
                        return HttpResponseRedirect(reverse('kolekti_sync', kwargs={'project': project}))
                    sync.update(files)

            elif action == "merge":
                resolve  = request.POST.get('resolve',None)
                files = request.POST.getlist('fileselect',[])
                if resolve =="merge":
                    sync.update(files)
                    sync.commit(files,commitmsg)
                if resolve == "remote":
                    sync.revert(files)
                
            elif action == "update":
                sync.update_all()
                
            elif action == "commit":
                resolve = request.POST.get('resolve')
                files = request.POST.getlist('fileselect',[])
                if resolve == "commit":
                    sync.update_all()
                    sync.commit(files,commitmsg)
                else: # revert
                    sync.revert(files)
            return HttpResponseRedirect(reverse('kolekti_sync', kwargs={'project': project}))            
        except:
            logger.exception("Unable to get sync tree")
            return HttpResponse(json.dumps({'status':'E', "action":action, 'stacktrace':traceback.format_exc()}), content_type="application/json", status=403)
            
class SyncStatusTreeView(kolektiMixin, View):
    def get(self, request, project):
        try:
            context, kolekti = self.get_context_data({'project':project})
            sync = self.get_sync_manager(kolekti)
            state = sync.statuses()
            return HttpResponse(json.dumps(state),content_type="application/json")
        except:
            logger.exception("Unable to get sync tree")
            return HttpResponse(json.dumps({'status':'E', 'stacktrace':traceback.format_exc()}), content_type="application/json", status=403)
    
class SyncRevisionView(kolektiMixin, TemplateView):
    template_name = "synchro/revision.html"
    def get(self, request, project, rev):
        context, kolekti = self.get_context_data({'project':project})
        sync = self.get_sync_manager(kolekti)
        revsumm, revinfo, difftext = sync.revision_info(rev)
        context, kolekti = self.get_context_data({
            "project":project,
            "history": sync.history(),
            'revsumm':revsumm,
            'revinfo':revinfo,
            'revnum':rev,
            'difftext':difftext,
            })
        
        return self.render_to_response(context)


class SyncDiffView(kolektiMixin, TemplateView):
    template_name = "synchro/diff.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        entry = request.GET.get("file")
        sync = self.get_sync_manager(kolekti)
        diff,  headdata, workdata = sync.diff(entry) 
        import difflib
        #htmldiff = hd.make_table(headdata.splitlines(), workdata.splitlines())
        context, kolekti = self.get_context_data({
            'diff':difflib.ndiff(headdata.splitlines(), workdata.splitlines()),
            'headdata':headdata,
            'workdata':workdata,
            })
        
        return self.render_to_response(context)

class SyncStatusView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            states = dict(sync.rev_state())
            return HttpResponse(json.dumps(states),content_type="application/json")
        except:
            logger.exception("Unable to get project sync status")
            return HttpResponse(json.dumps({'revision':{'status':'E'}}),content_type="application/json")

class SyncRemoteStatusView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            syncnum = dict(sync.rev_number())
            return HttpResponse(json.dumps(syncnum),content_type="application/json")
        except:
            logger.exception("Unable to get project remote sync status")
            return HttpResponse(json.dumps({'revision':{'number':'!'}}),content_type="application/json")
            
class SyncResStatusView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            path = request.GET.get("path")
            sync = self.get_sync_manager(kolekti)
            state = sync.statuses(path, recurse = False)
            return HttpResponse(json.dumps(state),content_type="application/json")
        except:
            logger.exception("Unable to get file sync status : %s"%path)
            return HttpResponse(json.dumps({'revision':{'status':'E'}}),content_type="application/json")

class SyncAddView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            path = request.POST.get('path')
            sync.add_resource(path)
            return HttpResponse(json.dumps('ok'),content_type="application/json")
        except:
            logger.exception("Unable to add file to synchro : %s"%path)
                        
class SyncRemoveView(kolektiMixin, View):
    def post(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            path = request.POST.get('path')
            sync.remove_resource(path)
            return HttpResponse(json.dumps('ok'),content_type="application/json")
        except:
            logger.exception("Unable to remove file to synchro : %s"%path)


class ProjectStaticView(kolektiMixin, View):
    def get(self, request, project, path):
        context, kolekti = self.get_context_data({'project':project})
        response =  serve(request, path, kolekti.syspath('/'))
        return response

class ProjectHistoryView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            hist = sync.history()
            hisrecords = [{"timestamp":r.date,"date":r.date,"user":r.author,"message":r.message,"rev":r.revision.number} for r in hist]
            return HttpResponse(json.dumps(hisrecords),content_type="application/json")
        except:
            logger.exception("Unable to get project history")

class AboutView(kolektiMixin, TemplateView):
    template_name = "about.html"

class ChangelogView(kolektiMixin, TemplateView):
    template_name = "changelog.html"
    def get(self, request):
        context, kolekti = self.get_context_data()
        changelog = ""
        appdir=os.path.dirname(os.path.dirname(os.path.realpath( __file__ )))
        with open(os.path.join(os.path.dirname(appdir), 'changelog')) as f:
            for changelogline in f.readlines():
                changelog += self.process(changelogline)
        context.update({'log':changelog})
        return self.render_to_response(context)

    def process(self, line):
        line = re.sub(
            r'\[fix #(\d+)\]', 
            r'[fix <a href="https://github.com/kolekti/kolekti/issues/\1" target="_blanck">\1</a>]',
            line)
        line = line +"<br/>"
        return line
    
class WidgetView(kolektiMixin, TemplateView):
    template_name = "widgets/default.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        return self.render_to_response(context)

class WidgetPublishArchiveView(WidgetView):
    template_name = "widgets/publish-archive.html"

    
class WidgetSearchView(WidgetView):
    template_name = "widgets/search.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        form = SearchForm()
        context.update({'form':form})
        return self.render_to_response(context)

    def post(self, request, project, page=1):
        context, kolekti = self.get_context_data({'project': project})
        q = request.POST.get('query')

        projectspath = os.path.join(settings.KOLEKTI_BASE, request.user.username)
        
        s = Searcher(projectspath, project)
        results = s.search(q, page)
        context.update({"results":results})
        context.update({"page":page})
        context.update({"query":q})
        return self.render_to_response(context)

    
class WidgetProjectHistoryView(WidgetView):
    template_name = "widgets/project-history.html"
    
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            context.update({'history':sync.history()})
        except:
            logger.exception("Unable to get project history")
            context.update({'history':[]})
        return self.render_to_response(context)


class WidgetPublicationsListView(kolektiMixin, TemplateView):
    template_name = "widgets/publications.html"

    def get(self, request, project):
        context, kolekti = self.get_context_data({
            'project':project,
            })
        context.update({
            "publications": [p for p in sorted(kolekti.get_publications(), key = lambda a: a['time'], reverse = True) ]
        })
        return self.render_to_response(context)

class WidgetReleasePublicationsListView(kolektiMixin, View):

    def get(self, request, project):
        context, kolekti = self.get_context_data({
            'project':project
            })
        context.update({
            "publications": [p for p in sorted(kolekti.get_releases_publications(), key = lambda a: a['time'], reverse = True) ]
        })
        return HttpResponse(json.dumps(context),content_type="application/json")



class ReleaseLangEditTopicView(kolektiMixin, TemplateView):
    template_name = "topics/edit-ckeditor.html"
    ttdir = "releases"
    
    def get(self, request, project, release, lang, topic_id):
        context, kolekti = self.get_context_data({
            'project':project,
            'lang':lang,
            })
        
        xsl = kolekti.get_xsl('django_edit_topic_assembly')
        
        assembly = kolekti.parse('/releases/{r}/sources/{l}/assembly/{r}_asm.html'.format(r=release, l=lang))

        topic = xsl(assembly, topic_id= "'%s'"%topic_id)

        context.update({
            "body":ET.tostring(topic),
            "release":release,
            "topic_id":topic_id,
            "title": release,
            })
        return self.render_to_response(context)

            
    def post(self, request, project, release, lang, topic_id):
        logger.debug('save topic assembly')
        context, kolekti = self.get_context_data({'project': project, 'lang':lang})
        try:
            topic = request.body
            xtopic = kolekti.parse_string(topic)
            assembly_path = '/releases/{r}/sources/{l}/assembly/{r}_asm.html'.format(r=release, l=lang)
            assembly = kolekti.parse(assembly_path)

            assembly_topic = assembly.xpath('//*[@id="%s"]'%topic_id)[0]
            for e in assembly_topic:
                if e.get('class') == 'topicinfo':
                    continue
                else:
                    assembly_topic.remove(e)

            saved_topic = xtopic.xpath('/html:html/html:body', **ns)[0]
            for e in saved_topic:
                assembly_topic.append(e)
                
            
            kolekti.xwrite(assembly, assembly_path)
            return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")

        except:
            logger.exception('invalid topic structure')
            import traceback
            msg = traceback.format_exc().split('\n')[-2]
            return HttpResponse(json.dumps({'status':'error', 'msg':msg}), content_type="application/json")

            

            
class CompareReleaseTopicSource(kolektiMixin, View):

    def filter_release(self, tree, release, kolekti):
        from kolekti.release import Release
        release = Release(kolekti.syspath('/'), release)
        modified = False
        for elt in tree.xpath('.//*[contains(@class, "=")]'):
            logger.debug(elt)
            modified = release.apply_filters_element(elt, profile_filter=False, assembly_filter=True, setPI = True) or modified
            logger.debug(modified)            
        return modified

    
    
    def post(self, request, project):
        class ParseTopicException(Exception):
            pass
        try:
            from xmldiff import formatting,main
            context, kolekti = self.get_context_data({
                'project':project
                })
            release = request.POST['release']
            cmp_release = request.POST.get('cmprelease', None)
            lang = request.POST['lang']
            topic = request.POST['topic']

            
            xsl = kolekti.get_xsl('django_diff_topic')
            xsl_result = kolekti.get_xsl('django_diff_topic_result')
            if cmp_release is None:
                try:
                    xtopic = kolekti.parse(topic)
                except:
                    raise ParseTopicException(topic)
                self.filter_release(xtopic, release, kolekti)
                diff_topic = xtopic.xpath("/html:html/html:body", **ns)[0]
                
            else:
                cmp_assembly = kolekti.parse('/releases/{r}/sources/{l}/assembly/{r}_asm.html'.format(r=cmp_release, l=lang))
                diff_topic = cmp_assembly.xpath("//html:div[@class='topic'][html:div[@class='topicinfo']/html:p[html:span[@class='infolabel'][.='source']]/html:span[@class='infovalue'][. = '{topic}']]".format(topic = topic), **ns)[0]
            assembly = kolekti.parse('/releases/{r}/sources/{l}/assembly/{r}_asm.html'.format(r=release, l=lang))
            assembly_topic = assembly.xpath("//html:div[@class='topic'][html:div[@class='topicinfo']/html:p[html:span[@class='infolabel'][.='source']]/html:span[@class='infovalue'][. = '{topic}']]".format(topic = topic), **ns)[0]
            logger.debug("filter -------------------")

            
            tree1 = xsl(diff_topic)
            tree2 = xsl(assembly_topic)
            logger.debug("tree 1 -------------------")
            logger.debug(tree1)
            logger.debug("tree 2 -------------------")
            logger.debug(tree2)

            logger.debug("diff   -------------------")
            formatter = formatting.XMLFormatter(normalize=formatting.WS_BOTH)
            diff = main.diff_trees(
                tree1, tree2,
                formatter=formatter,
                diff_options={'F': 0.4, 'ratio_mode': 'accurate'})
#                diff_options={'F': 0.5, 'ratio_mode': 'fast'})

            xdiff = xsl_result(ET.XML(diff), path="'/%s/releases/%s'"%(project, release))
            logger.debug(diff)
            logger.debug("done   -------------------")            
#            return HttpResponse(json.dumps(diff),content_type="application/json")
#            return HttpResponse(ET.tostring(xdiff), content_type="text/xml")
            return HttpResponse(ET.tostring(xdiff), content_type="text/xml")
        except ParseTopicException as reason:
            logger.exception('could not calculate diff : parse topic failed %s', str(reason))
            
            return HttpResponse(json.dumps({'reason' : 'parsetopic', 'topic':str(reason), 'message':'Impossible de lire le module %s'%str(reason)}), content_type='application/json', status=403)
        except Exception as reason:
            logger.exception('could not calculate diff')
            return HttpResponse(json.dumps({'reason' : 'unknown', "message":"could not calculate diff"}), content_type='application/json', status=500)


    
