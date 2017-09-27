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

import logging
logger = logging.getLogger('kolekti.'+__name__)
       
from kserver_saas.models import Project, UserProfile, UserProject
from forms import UploadFileForm

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

# kolekti imports
from kolekti.common import kolektiBase
from kolekti.publish_utils import PublisherExtensions
from kolekti import publish
from kolekti.searchindex import searcher
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
            project = data['project']
            try:
                if settings.KOLEKTI_MULTIUSER:
                    userproject = UserProject.objects.get(user = self.request.user, project__directory = project)
                    project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
                else:
                    userproject = UserProject.objects.get(project__directory = project)
                    project_path = os.path.join(settings.KOLEKTI_BASE, project)
                    
            except UserProject.DoesNotExist:
                raise Http404
            
            if 'lang' in data.keys():
                userproject.srclang = data['lang']
                userproject.save()
            else:
                context.update({'lang':userproject.srclang})

            context.update({
                'user_project' : userproject
            })

            kolekti = kolektiBase(project_path)
            
        if settings.KOLEKTI_MULTIUSER:
            userprojects = UserProject.objects.filter(user = self.request.user)
        else:
            userprojects = UserProject.objects.all()
                
        context.update({'user_projects': userprojects,})
        context.update(data)
        return context, kolekti

    
    def config(self):
        return self._config

    def process_svn_url(self, url):
        localpath = "file://%s/"%(settings.KOLEKTI_SVN_ROOT,)
        remotepath = "http://%s/svn/"%(settings.HOSTNAME,)
        return url.replace(localpath, remotepath)
    
    def projects(self):
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


    # TODO
    def project_langs(self, kolekti):
        try:
            return ([l.text for l in kolekti.project_settings.xpath('/settings/languages/lang')],
                    [l.text for l in kolekti.project_settings.xpath('/settings/releases/lang')],
                    kolekti.project_settings.xpath('string(/settings/@sourcelang)'))
        except IOError:
            return ['en'],['en','fr','de'],'en'
        except AttributeError:
            return ['en'],['en','fr','de'],'en'

    def get_sync_manager(self, kolekti):
        from kolekti.synchro import SynchroManager
        sync = SynchroManager(kolekti.syspath(''))
        return sync
        
    def localname(self,e):
        return re.sub('\{[^\}]+\}','',e.tag)
    
    def get_tocs(self):
        return self.itertocs

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

    def project_activate(self,userproject):
        # TO BE REMOVED
        if settings.KOLEKTI_MULTIUSER:
            self.request.user.userprofile.activeproject = userproject
            self.request.user.userprofile.save()
            self.request.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, userproject.project.directory)
        else:
            userprofile = UserProfile.objects.get()
            userprofile.activeproject = userproject
            userprofile.save()
            self.request.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, userproject.project.directory)        
        self.request.kolekti_userproject = userproject
        self.set_project(self.request.kolekti_projectpath)
        try:
            languages, rlang, defaultlang = self.project_langs()
            if not self.request.kolekti_userproject.srclang in languages:
                self.request.kolekti_userproject.srclang = defaultlang
                self.request.kolekti_userproject.save()
        except:
            self.request.kolekti_userproject.srclang='en'
            self.request.kolekti_userproject.save()

       
    def language_activate(self,language):
        # get userdir
        self.request.kolekti_userproject.srclang = language
        self.request.kolekti_userproject.save()

    def format_iterator(self, sourceiter):
        template = get_template('publication-iterator.html')
        nbchunck = 0
        for chunck in sourceiter:
            nbchunck += 1
            chunck.update({'id':nbchunck})
            yield template.render(chunck)
        

    def set_extension(self, path, default):
        if os.path.splitext(path)[1] == "":
            path = path + default
        return path
    
class HomeView(kolektiMixin, TemplateView):
    template_name = "home.html"
    def get(self, request):
        context, kolekti = self.get_context_data()
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
    def get(self, request, require_svn_auth=False, project_folder="", project_url="", error = None):
        context, kolekti = self.get_context_data({
                    "require_svn_auth":require_svn_auth,
                    "projectfolder":project_folder,
                    "projecturl":project_url,
                    "error":error,
                    })
        
        if hasattr(self,'_project_starters'):
            context.update({'project_starters':self._project_starters(request.user)})
        return self.render_to_response(context)

    def post(self, request):
        # create new project
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username,password)

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
            "source_langs" :[l.text for l in settings.xpath('/settings/languages/lang')],
            "release_langs" :[l.text for l in settings.xpath('/settings/releases/lang')],
            "default_srclang":settings.xpath('string(/settings/@sourcelang)'),
            })
        return self.render_to_response(context)

    def post(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        settings = kolekti.parse('/kolekti/settings.xml').getroot()
        srclangs = request.POST.getlist('sources[]',[])
        rellangs = request.POST.getlist('releases[]',[])
        settings.set('sourcelang', request.POST.get('default_source','en'))
        xlangs = settings.find('languages')
        if xlangs is None:
            xlangs = ET.SubElement(settings, 'languages')
        else:
            for l in xlangs:
                xlangs.remove(l)
        for l in srclangs:
            xl = ET.SubElement(xlangs,'lang')
            xl.text = l
    
        xlangs = settings.find('releases')
        if xlangs is None:
            xlangs = ET.SubElement(settings, 'releases')
        else:
            for l in xlangs:
                xlangs.remove(l)
        for l in set(rellangs).union(set(srclangs)):
            xl = ET.SubElement(xlangs,'lang')
            xl.text = l
            
        kolekti.xwrite(settings,'/kolekti/settings.xml')
        return HttpResponseRedirect(reverse('kolekti_project_languages', kwargs={'project': project}))

        
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

class ReleasesPublicationsListJsonView(kolektiMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        publications = kolekti.get_releases_publications()
        return HttpResponse(json.dumps(publications),content_type="application/json")
        
class TocsListView(kolektiMixin, TemplateView):
    template_name = 'tocs/list.html'
    
class TocEditView(kolektiMixin, TemplateView):
    template_name = "tocs/detail.html"

    def get(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project':project})
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
            context, kolekti = self.get_context_data({'project':project})
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
        context, kolekti = self.get_context_data({'project':project})
        toc_path_project = '/'.join(['/sources', lang, 'tocs', toc_path])
        tocpath = self.set_extension(toc_path_project, ".html")
        toc = kolekti.parse_html_string("""<?xml version="1.0"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>toc</title></head>
  <body></body>
</html>""")
        kolekti.xwrite(toc, tocpath)
        return HttpResponse(json.dumps(self.path_exists(tocpath)),content_type="application/json")


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

    
# class PublicationView(kolektiMixin, TemplateView):
#     template_name = "publication.html"
#     def __init__(self, *args, **kwargs):
#         super(PublicationView, self).__init__(*args, **kwargs)

#     @classmethod
#     def as_view(cls, **initkwargs):
#         view = super(PublicationView, cls).as_view(**initkwargs)
#         return condition(etag_func=None)(view)
    
class TocPublishView(kolektiMixin, TemplateView):
    template_name = "publication.html"
    def post(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project': project})
        jobpath = request.POST.get('job')
        pubdir  = request.POST.get('pubdir')
        pubtitle= request.POST.get('pubtitle')
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        context={}
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

            p = publish.DraftPublisher(kolekti.syspath(), lang=lang)
            return StreamingHttpResponse(self.format_iterator(p.publish_draft(toc_path, xjob, pubtitle)), content_type="text/html")

        except:
            import traceback
            logging.exception('publication error')
            context.update({'success':False})
            context.update({'stacktrace':traceback.format_exc()})
            return self.render_to_response(context)
        
class TocReleaseView(kolektiMixin, TemplateView):
    template_name = "publication.html"                                                                              
    def post(self, request, project, lang, toc_path):
        context, kolekti = self.get_context_data({'project': project})
        jobpath = request.POST.get('job')
        release_name  = request.POST.get('release_name')
        release_index  = request.POST.get('release_index')
        release_prev_index  = request.POST.get('release_prev_index')
        pubdir  = "%s_%s"%(release_name, release_index)
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = kolekti.parse(jobpath)
        
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                print ET.tostring(jprofile)
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
                        
            return StreamingHttpResponse(self.format_iterator(self.release_iter(kolekti.syspath(), toc_path, xjob)))
        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
            context.update({'stacktrace':traceback.format_exc()})
            
            return self.render_to_response(context)

    def release_iter(self, projectpath, tocpath, xjob):
        lang=self.request.kolekti_userproject.srclang
        r = publish.Releaser(projectpath, lang = lang)
        pp = r.make_release(tocpath, xjob)
        release_dir = pp[0]['assembly_dir'][:-1]
        yield {
            'event':'release',
            'ref':release_dir,
            'releasedir':pp[0]['releasedir'],
            'time':pp[0]['datetime'],
            'lang':lang,
        }
        
        if self.syncMgr is not None :
            self.syncMgr.propset("release_state","sourcelang","/".join([release_dir,"sources",lang,"assembly",pp[0]['releasedir']+'_asm.html']))
        p = publish.ReleasePublisher(release_dir, projectpath, langs=[self.request.kolekti_userproject.srclang])
        for e in p.publish_assembly(pp[0]['pubname']):
            yield e

    
class ReleaseListView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"

class ReleaseAllStatesView(kolektiMixin, TemplateView):
    def get(self, request, project, release):
        context, kolekti = self.get_context_data({'project':project})
        languages, release_languages, default_srclang = self.project_langs(kolekti)
        states = []
        for lang in release_languages:
            asfilename = "/".join(['/releases',release,"sources",lang,"assembly",release+'_asm.html'])
            sync = self.get_sync_manager(kolekti)
            state = sync.propget("release_state",asfilename)
            if state is None:
                if kolekti.exists(asfilename):
                    states.append((lang, "local"))

            if state == "source_lang":
                states.insert(0,(lang, state))
            else:
                states.append((lang, state))
        return HttpResponse(json.dumps(states),content_type="application/json")

    
class ReleaseStateView(kolektiMixin, TemplateView):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project})
        sync = self.get_sync_manager(kolekti)

        if sync is None:
            state = "unknown"
        else:
            state = sync.propget("release_state","/".join(['/releases',release,"sources",lang,"assembly",release+'_asm.html']))
        return HttpResponse(state)

    def post(self,request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project})
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
                    
class ReleaseFocusView(kolektiMixin, TemplateView):
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project})
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
                    
class ReleaseCopyView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project})
        try:
            dstlang = request.POST.get('target_lang')

            #            return StreamingHttpResponse(
            for copiedfiles in self.copy_release(path, release, lang, dstlang):
                pass
            assembly = "/".join(['/releases', release , "sources" , dstlang , "assembly" , release+'_asm.html'])

            sync = self.get_sync_manager(kolekti)

            sync.propset("release_state",'edition', assembly)
            sync.propset("release_srclang", srclang, assembly)
            # self.syncMgr.commit(path,"Revision Copy %s to %s"%(srclang, dstlang))

        except:
            import traceback
            print traceback.format_exc()
    #    return HttpResponse("ok")
        return HttpResponseRedirect('/releases/detail/?release=%s&lang=%s'%(path,dstlang))
    
class ReleaseDeleteView(kolektiMixin, View):
    def post(self, request, project, release):
        context, kolekti = self.get_context_data({'project': project})
        try:
            release = request.POST.get('release')
            lang = request.POST.get('lang')
            self.delete_resource('%s/sources/%s'%(release, lang))
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            logger.exception("Could not delete release")
            return HttpResponse(status=500)
            
class ReleaseAssemblyView(kolektiMixin, TemplateView):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project': project})
        try:
            release_path = request.GET.get('release')
            assembly_name = release_path.rsplit('/',1)[1]
            lang = request.GET.get('lang', self.request.kolekti_userproject.srclang)
            assembly_path = '/'.join([release_path,"sources",lang,"assembly",assembly_name+"_asm.html"])
            xassembly = kolekti.parse(path.replace('{LANG}', lang))
            body = xassembly.xpath('/html:html/html:body/*', **ns)
            xsl = kolekti.get_xsl('django_assembly_edit')
            content = ''.join([str(xsl(t, path="'%s'"%release_path)) for t in body])
        except:
            import traceback
            print traceback.format_exc()
        return HttpResponse(content)
    

class ReleasePublicationsView(kolektiMixin, TemplateView):
    template_name = "releases/publications.html"
    
    def __release_publications(self, lang, release_path):
        publications = []
        try:
            mf = json.loads(self.read(release_path + "/manifest.json"))
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
            'publications':self.__release_publications(lang, release_path)
        })
        return self.render_to_response(context)
                
class ReleaseDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"

    def __has_valid_actions(self,  release_path):
        assembly = release_path.rsplit('/',1)[1]
        xjob = kolekti.parse(release_path + '/kolekti/publication-parameters/'+ assembly +'_asm.xml')
        print xjob.xpath('/job/scripts/script[@enabled="1"]/validation/script')
        return len(xjob.xpath('/job/scripts/script[@enabled="1"]/validation/script')) > 0

    
    def get_context_data(self, data={}, **kwargs):
        context, kolekti = super(ReleaseDetailsView, self).get_context_data(data, **kwargs)
        states = []
        focus = []
        release_path = context.get('release_path')
        assembly_name = context.get('assembly_name')
        assembly_lang = context.get('lang')
        langstate = None
        
        sync = self.get_sync_manager(kolekti)

        for lang in context.get('releaselangs',[]):
            tr_assembly_path = release_path+"/sources/"+lang+"/assembly/"+assembly_name+'_asm.html'
            if kolekti.path_exists(tr_assembly_path):
                states.append(sync.propget('release_state',tr_assembly_path))
            else:
                states.append("unknown")
            if lang == assembly_lang:
                langstate = states[-1]
            try:
                focus.append(ReleaseFocus.objects.get(release = release_path, assembly = assembly_name, lang = lang).state)
            except:
                #import traceback
                #print traceback.format_exc()
                focus.append(False)
        context.update({'langstate':langstate,'langstates':zip(context.get('releaselangs',[]),states,focus)})
        return context, kolekti
    
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project})
        assembly_path = '/'.join(['/releases',release,"sources",lang,"assembly",release+"_asm.html"])
        assembly_meta = {}
        try:
            xassembly = kolekti.parse(assembly_path)
            for meta in xassembly.xpath("/h:html/h:head/h:meta",namespaces = {"h":"http://www.w3.org/1999/xhtml"}):
                if meta.get('name') is not None:
                    assembly_meta.update({meta.get('name').replace('.','_'):meta.get('content')})
        except IOError:
            pass
    
        sync = self.get_sync_manager(kolekti)

        srclang = sync.propget('release_srclang', assembly_path)
        if srclang is None:
            srclang = self.project_langs()[2]        
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
            'releasesinfo':kolekti.release_details(release_path, lang),
            'releaseparams':{'profiles':profiles, 'scripts':scripts},
            'success':True,
            'release_path':release_path,
            'assembly_name':assembly_name,
            'assembly_meta':assembly_meta,
            'lang':lang,
            'srclang':srclang,
            'validactions':self.__has_valid_actions(release_path)
        })
        logger.debug(context)
        logger.debug(context.get('srclang','not defined'))
        return self.render_to_response(context)
    
    def post(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project})

        assembly_path = '/'.join(['/releases/',release,'sources',lang,'assembly',release+'_asm.html'])
        payload = request.FILES.get('upload_file').read()
        xassembly = kolekti.parse_string(payload)
        
        xsl = self.get_xsl('django_assembly_save')
        xassembly = xsl(xassembly, prefixrelease='"%s"'%release)
        self.update_assembly_lang(xassembly, lang)
        kolekti.xwrite(xassembly, assembly_path)

        sync = self.get_sync_manager(kolekti)
        srclang = sync.propget('release_srclang', assembly_path)

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
    def post (self, request, project, release, lang):        
        context, kolekti=self.get_context_data({'project':project})
        try:
            p = publish.ReleasePublisher(release_path, kolekti.syspath(), langs=[lang])
            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(assembly_name + "_asm")), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

class ReleaseValidateView(kolektiMixin, View):
    def post (self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project})

#        jobpath = release + '/kolekti/publication-parameters/' + assembly + '.xml'
#        print jobpath
#        xjob = kolekti.parse(jobpath)
        try:
            p = publish.ReleasePublisher(release_path, kolekti.syspath(), langs=[lang])
            return StreamingHttpResponse(self.format_iterator(p.validate_release()), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

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
        context, kolekti = self.get_context_data({'project':project})
        name = picture_path.rsplit('/',1)[1]
        logger.debug(picture_path)
        ospath = kolekti.syspath('/sources/' + lang + '/pictures/' + picture_path)
        logger.debug(ospath)
        try:
            im = Image.open(ospath)
            context.update({
                'fileweight':"%.2f"%(float(os.path.getsize(ospath)) / 1024),
                'name':name,
                'path':picture_path,
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


class VariablesMixin(kolektiMixin, TemplateView):

    def getval(self, val):
        try:
            return val.find('content').text
        except AttributeError:
            return ""
        
    def variable_details(self, kolekti, path, include_values = None):
        name = path.rsplit('/',1)[1]
        xmlvar = kolekti.parse(path)
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
            
        context, kolekti = self.get_context_data({
            'name':name,
            'path':path,
            'vardata' : json.dumps(vardata),
            })
        context.update(vardata)
        return context

    def post(self, request, project, lang, variable_path):
        try:
            context, kolekti = self.get_context_data({'project':project, 'lang':lang, 'variable_path':variable_path})
            payload = json.loads(request.body)
            varpath = payload.get('path')
            xvar = kolekti.parse(varpath)
            for var, mvar in zip(xvar.xpath('/variables/variable'), payload.get('data')):
                for (val, mval) in zip(var.xpath('value/content'), mvar):
                    val.text = mval
            kolekti.xwrite(xvar, varpath)
            return HttpResponse('ok')
        except:
            logger.exception('Could not save variable')
            return HttpResponse(status=500)
    
class VariablesDetailsView(VariablesMixin):
    template_name = "variables/details.html"
    def get(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project':project, 'lang':lang, 'variable_path':variable_path})
        try:
            logger.debug(variable_path)
            project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)
            context.update(self.variable_details(kolekti, project_variable_path))
            return self.render_to_response(context)
        except:
            logger.exception('unable to process variable file')
            raise
        
    def post(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        try:
            action = request.POST.get('action')
            path = request.POST.get('path')
            xvar = kolekti.parse(path)
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
                    
                
        except:
            logger.exception('var action failed')
            
        kolekti.xwrite(xvar, path)
        return HttpResponseRedirect('?path='+path)
#        return self.render_to_response(self.variable_details(path))
        
class VariablesEditvarView(VariablesMixin):
    template_name = "variables/editvar.html"
    def get(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        index = int(request.GET.get('index',1)) - 1
        project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)
        context.update(self.variable_details(kolekti, project_variable_path, True))
        context.update({
            "variable_path":variable_path,
            "method":"line",
            "current":index,
            })
        return self.render_to_response(context)
    

class VariablesEditcolView(VariablesMixin):
    template_name = "variables/editvar.html"
    def get(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        path = request.GET.get('path')
        index = int(request.GET.get('index', 1)) - 1
        project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)
        context.update(self.variable_details(kolekti, project_variable_path, True))
        context.update({
            "variable_path":variable_path,                                          
            "method":"col",
            "current":index,
            })
        return self.render_to_response(context)
    
    
class VariablesUploadView(kolektiMixin, TemplateView):
    def post(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)

            path = request.POST['path']
            converter = OdsToXML(kolekti.syspath())
            converter.convert(uploaded_file, project_variable_path)
            # self.write_chunks(uploaded_file.chunks,path +'/'+ uploaded_file.name) 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class VariablesCreateView(kolektiMixin, TemplateView):
    def post(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        try:
            project_variable_path = "/sources/%s/variables/%s"%(lang, variable_path)
            project_variable_path = self.set_extension(project_variable_path, ".xml")
            varx = kolekti.parse_string('<variables><critlist></critlist></variables>')
            kolekti.xwrite(varx, project_variable_path)
            return HttpResponse(json.dumps(kolekti.path_exists(project_variable_path)),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)

class VariablesODSView(kolektiMixin, View):
    def get(self, request, project, lang, variable_path):
        context, kolekti = self.get_context_data({'project': project})
        path = request.GET.get('path')
        filename = path.rsplit('/',1)[1].replace('.xml','.ods')
        odsfile = StringIO()
        converter = XMLToOds(kolekti.syspath())
        converter.convert(odsfile, path)
        response = HttpResponse(odsfile.getvalue(),
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response


    
class ImportView(kolektiMixin, TemplateView):
    template_name = "import.html"
    def get(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project})
        tpls = kolekti.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        
        context, kolekti = self.get_context_data({'templates':tnames})
        return self.render_to_response(context)

    def post(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project})
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
        context, kolekti = self.get_context_data({'project': project})
        template = request.GET.get('template')
        filename = "import_template.ods"
        odsfile = StringIO()
        tplter = Templater(kolekti.syspath)
        tplter.generate("/sources/"+self.request.kolekti_userproject.srclang+"/templates/"+template, odsfile)
        response = HttpResponse(odsfile.getvalue(),                            
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response

    
class SettingsJsView(kolektiMixin, TemplateView):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})

        project_path = os.path.join(settings.KOLEKTI_BASE, project)
        try:
            sync = self.get_sync_manager(kolekti)
            project_svn_url = sync.geturl()
        except ExcSyncNoSync:
            project_svn_url = ""
            
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
            languages, release_languages, default_srclang = self.project_langs()
            context.update({
                'srclangs' : languages,
                'releaselangs' : release_languages,
                'default_srclang':default_srclang,
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
        return HttpResponse(kolekti.read('/kolekti/settings.xml'),content_type="text/xml")

class CriteriaCssView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            settings = kolekti.parse('/kolekti/settings.xml')
            xsl = kolekti.get_xsl('django_criteria_css')
            #print xsl(settings)
            return HttpResponse(str(xsl(settings)), "text/css")
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
        settings = kolekti.parse('/kolekti/settings.xml')
        criteria = []
        for xcriterion in settings.xpath('/settings/criteria/criterion'):
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
            settings = kolekti.parse('/kolekti/settings.xml')
            xcriteria = kolekti.parse_string(request.body)
            xsettingscriteria=settings.xpath('/settings/criteria')[0]
            for xcriterion in xsettingscriteria:
                xsettingscriteria.remove(xcriterion)
                
            for xcriterion in xcriteria.xpath('/criteria/criterion'):
                xsettingscriteria.append(xcriterion)
            kolekti.xwrite(settings, '/kolekti/settings.xml')
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
        self.copy_resource(src, dest)
        return HttpResponse(json.dumps(kolekti.path_exists(path)),content_type="application/json")


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
            
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project': project})
        try:
            path = request.GET.get('path','/')
            mode = request.GET.get('mode','select')
            try:
                files = filter(self.__browserfilter, kolekti.get_directory(path))
            
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
                context.update({'status':'error'})
                context.update({'msg':'%s does not exists'%path})
    
            pathsteps = []
            startpath = ""
            for step in path.split("/")[1:-1]:
                startpath = startpath + "/" + step
                pathsteps.append({'label':step, 'path': startpath})

            context.update({'pathsteps':pathsteps})
            context.update({'mode':mode})
            context.update({'path':path})
#            context.update({'project':self.request.kolekti_userproject.project.directory})
            context.update({'id':'browser_%i'%random.randint(1, 10000)})
            return self.render_to_response(context)
        except:
            logger.exception('browser error')
            raise 

class BrowserReleasesView(BrowserView):
    template_name = "browser/releases.html"
    def get_directory(self, path):
        try:
            releases = {}
            res = []
            for assembly, date in self.get_release_assemblies(path):
                item = {'name':assembly,
                        'project':projectdir,
                        'type':"text/xml",
                        'date':date}
                res.append(item)
                try:
                    found = False
                    mf = json.loads(self.read('/'.join([path, assembly, 'release_info.json'])))
                    releasename = mf.get('releasename')
                    releaseindex = mf.get('releaseindex')
                    
                    r = {'name':releaseindex, 'type':"text/xml", 'date':date}
                    try:
                        releases[releasename]['indexes'].append(r)
                    except KeyError:
                        releases[releasename] = {
                            'name':releasename,
                            'type':"text/xml",                                   
                            'date':None,
                            'indexes':[r]}
                        found = True
                except:
                    releases[assembly]=item
                    # logger.exception('release list error')
            # logger.debug(releases)
            return releases.values()
#            return res
        except:
            logger.exception('release list error')
            return super(BrowserReleasesView, self).get_directory(path)
                      
            
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

    
    def get(self, request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project})
        topic_project_path = '/sources/%s/topics/%s'%(lang, topic_path)
        topic = kolekti.read(topic_project_path)
        
        context.update({
            "body":topic,
            "title": kolekti.basename(topic_path),
            })
        return self.render_to_response(context)

    def post(self,request, project, lang, topic_path):
        context, kolekti = self.get_context_data({'project': project})
        try:
            topic_project_path = '/sources/%s/topics/%s'%(lang, topic_path)
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
        context, kolekti = self.get_context_data({'project': project})
        xtopic = kolekti.parse(path.replace('{LANG}', lang))
        metaelts = xtopic.xpath('/h:html/h:head/h:meta[@name][@content]', namespaces={'h':'http://www.w3.org/1999/xhtml'})
        meta = [{'name':m.get('name'),'content':m.get('content')} for m in metaelts]
        return HttpResponse(json.dumps(meta), content_type="application/json")
    
class TopicCreateView(kolektiMixin, View):
    def post(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project})
        try:
            model_path = '/sources/'+ lang + "/templates/" + request.POST.get('model')
            topic_path = self.set_extension(topic_path, ".html")
            topic_project_path = '/sources/%s/topics/%s'%(lang, topic_path)
            topic = kolekti.parse(model_path)
            kolekti.xwrite(topic, topic_project_path)
        except:
            logger.exception("Create topic error")
        return HttpResponse(json.dumps(topicpath), content_type="application/json")

class TopicTemplatesView(kolektiMixin, View):
    def get(self, request, project, lang):
        context, kolekti = self.get_context_data({'project': project})
        try:
            tpls = kolekti.get_directory(root = "/sources/"+lang+"/templates")
            tnames = [t['name'] for t in tpls]
        except OSError:
            tnames=[]
        return HttpResponse(json.dumps(tnames),content_type="application/json")

class TemplateEditorView(TopicEditorView):
    pass

class TemplateCreateView(TopicCreateView):
    pass


    


class SearchView(kolektiMixin, TemplateView):
    template_name = "search/results.html"
    def get(self, request):
        context, kolekti = self.get_context_data()
        q = request.GET.get('query')
        s = searcher(self.request.kolekti_projectpath)
        results = s.search(q)
        context.update({"results":results})
        context.update({"query":q})
        return self.render_to_response(context)



class SyncView(kolektiMixin, TemplateView):
    template_name = "synchro/main.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        try:
            sync = self.get_sync_manager(kolekti)
            context.update({
                    "history": sync.history(),
                    "changes": sync.statuses(),
                    })
        except ExcSyncNoSync:
            logger.exception("Synchro unavailable")
            context.update({'status':'nosync'})
        return self.render_to_response(context)

    def post(self, request, project):
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
                for file in files:
                    if self.exists(file+'.mine'):
                        self.copyFile(file+'.mine', file)
                    else:
                        raise Exception('impossible de trouver la version locale')
                    try:
                        sync.resolved(file)
                    except:
                        logger.exception('error while resolving conflict [use local]')
                        
                sync.commit(files, commitmsg)
            if resolve == "remote":
                try:
                    sync.revert(files)
                except:
                    logger.exception('impossible to revert')
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
            else:
                sync.revert(files)
            
        return self.get(request)
                    
class SyncRevisionView(kolektiMixin, TemplateView):
    template_name = "synchro/revision.html"
    def get(self, request, project, rev):
        context, kolekti = self.get_context_data({'project':project})
        sync = self.get_sync_manager(kolekti)
        revsumm, revinfo, difftext = sync.revision_info(rev)
        context, kolekti = self.get_context_data({
            "history": sync.history(),
            'revsumm':revsumm,
            'revinfo':revinfo,
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
            return HttpResponse(json.dumps(self._syncnumber),content_type="application/json")
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
        return serve(request, path, kolekti.syspath('/'))


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

    
class WidgetProjectHistoryView(kolektiMixin, TemplateView):
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
            "publications": [p for p in sorted(self.get_publications(), key = lambda a: a['time'], reverse = True) ]
        })
        return self.render_to_response(context)

class WidgetReleasePublicationsListView(kolektiMixin, View):

    def get(self, request, project):
        context, kolekti = self.get_context_data({
            'project':project,
            "publications": [p for p in sorted(self.get_releases_publications(), key = lambda a: a['time'], reverse = True) ]
        })
        return HttpResponse(json.dumps(context),content_type="application/json")

