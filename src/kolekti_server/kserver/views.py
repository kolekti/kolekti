# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import re
import os
from copy import copy
import shutil
import json
import random
from datetime import datetime
import time
from lxml import etree as ET
from PIL import Image
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
   
from models import Settings, ReleaseFocus
from forms import UploadFileForm

from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.conf import settings
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.static import serve 
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.template.loader import get_template
from django.template import Context

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

class kolektiMixin(TemplateResponseMixin, kolektiBase):
    def __init__(self, *args, **kwargs):
        self.user_settings = Settings.objects.get()
        projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
        super(kolektiMixin, self).__init__(projectpath,*args,**kwargs)

    def config(self):
        return self._config

    def projects(self):
        projects = []
        for projectname in os.listdir(settings.KOLEKTI_BASE):
            project={'name':projectname, 'id':projectname.replace(' ','_')}
            try:
                projectsettings = ET.parse(os.path.join(settings.KOLEKTI_BASE, projectname, 'kolekti', 'settings.xml'))
                if projectsettings.xpath('string(/settings/@version)') != '0.7':
                    continue
                project.update({'languages':[l.text for l in projectsettings.xpath('/settings/languages/lang')],
                                'defaultlang':projectsettings.xpath('string(/settings/@sourcelang)')})
            except:
                continue

            try:
                from kolekti.synchro import SynchroManager
                synchro = SynchroManager(os.path.join(settings.KOLEKTI_BASE,projectname))
                projecturl = synchro.geturl()
                project.update({"status":"svn","url":projecturl})
            except ExcSyncNoSync:
                project.update({"status":"local"})
            projects.append(project)
        return projects

    def project_langs(self, project):
        try:
            projectsettings  = ET.parse(os.path.join(settings.KOLEKTI_BASE, project, 'kolekti', 'settings.xml'))     
            return ([l.text for l in projectsettings.xpath('/settings/languages/lang')],
                        projectsettings.xpath('string(/settings/@sourcelang)'))
        except IOError:
            return ['fr'],'fr'
    
    def get_context_data(self, data={}, **kwargs):
        prj = self.user_settings.active_project
        try:
            ET.parse(os.path.join(settings.KOLEKTI_BASE, prj, 'kolekti', 'settings.xml'))
        except IOError:
            prj = None
                     
        languages, default_lang = self.project_langs(self.user_settings.active_project)
        context = {}
        context['kolekti'] = self._config
        context['projects'] = self.projects()
        context['srclangs'] = languages
        context["active_project"] = prj
        context["active_srclang"] = self.user_settings.active_srclang
        context['syncinfo'] = self._syncstate
        context.update(data) 
        return context

    def get_toc_edit(self, path):
        xtoc = self.parse(path)
        tocmeta = {}
        toctitle = xtoc.xpath('string(/html:html/html:head/html:meta[@name="DC.title"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})

        if len(toctitle) == 0:
            toctitle = xtoc.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        for meta in xtoc.xpath('/html:html/html:head/html:meta', namespaces={'html':'http://www.w3.org/1999/xhtml'}):
            if meta.get('name',False):
                tocmeta.update({meta.get('name').replace('.','_'):meta.get('content')})
        tocjob = xtoc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_toc_edit', extclass=PublisherExtensions, lang=self.user_settings.active_srclang)
        try:
            etoc = xsl(xtoc)
        except:
            import traceback
            print traceback.format_exc()
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return toctitle, tocmeta, str(etoc)

    def localname(self,e):
        return re.sub('\{[^\}]+\}','',e.tag)
    
    def get_topic_edit(self, path):
        xtopic = self.parse(path.replace('{LANG}',self.user_settings.active_srclang))
        topictitle = xtopic.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topicmeta = xtopic.xpath('/html:html/html:head/html:meta[@name]', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topicmetalist = [{'tag':self.localname(m),'name':m.get('name',None),'content':m.get('content',None)} for m in topicmeta]
        topicmeta = xtopic.xpath('/html:html/html:head/html:title', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topicmetalist += [{'tag':self.localname(m),'title':m.text} for m in topicmeta]
        topicmeta = xtopic.xpath('/html:html/html:head/html:link', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topicmetalist += [{'tag':self.localname(m),'rel':m.get('rel',None),'type':m.get('type',None),'href':m.get('href',None)} for m in topicmeta]
        topicbody = xtopic.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_topic_edit')
        #print [str(xsl(t)) for t in topicbody]
        topiccontent = ''.join([str(xsl(t)) for t in topicbody])
        return topictitle, topicmetalist, topiccontent

    def get_assembly_edit(self, path, release_path=""):
        xassembly = self.parse(path.replace('{LANG}',self.user_settings.active_publang))
        body = xassembly.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_assembly_edit')
        
        content = ''.join([str(xsl(t, path="'%s'"%release_path)) for t in body])
        return content
    
    def get_tocs(self):
        return self.itertocs

    def get_jobs(self):
        res = []
        for job in self.iterjobs:
            xj = self.parse(job['path'])
            job.update({'profiles':[(p.find('label').text,p.get('enabled')) for p in xj.xpath('/job/profiles/profile')],
                        'scripts':[(s.get("name"),s.get('enabled')) for s in xj.xpath('/job/scripts/script')],
                        })
            res.append(job)
        return res

    def get_job_edit(self,path):
        xjob = self.parse(path)
        xjob.getroot().append(copy(self._project_settings))
        xjob.getroot().find('settings').append(copy(self.get_scripts_defs()))
        #with open('/tmp/xml','w') as f:
        #    f.write(ET.tostring(xjob, pretty_print=True))
        xsl = self.get_xsl('django_job_edit', extclass=PublisherExtensions, lang=self.user_settings.active_srclang)
        try:
            ejob = xsl(xjob, path="'%s'"%path, jobname="'%s'"%self.basename(path))
        except:
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return str(ejob)

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

    def project_activate(self,project):
        # get userdir
        self.user_settings.active_project = project
        projectsettings = ET.parse(os.path.join(settings.KOLEKTI_BASE, project, 'kolekti', 'settings.xml'))     
        languages, defaultlang = self.project_langs(project)
        if not self.user_settings.active_srclang in languages:
             self.user_settings.active_srclang = defaultlang
        self.user_settings.save()

    def language_activate(self,language):
        # get userdir
        self.user_settings.active_srclang = language
        self.user_settings.save()


    def format_iterator(self, sourceiter):
        template = get_template('publication-iterator.html')
        nbchunck = 0
        for chunck in sourceiter:
            nbchunck += 1
            chunck.update({'id':nbchunck})
            yield template.render(Context(chunck))
        

    def set_extension(self, path, default):
        if os.path.splitext(path)[1] == "":
            path = path + default
        return path
    
class HomeView(kolektiMixin, View):
    template_name = "home.html"
    def get(self, request):
        context = self.get_context_data()
        if context.get('active_project') is None:
            return HttpResponseRedirect('/projects/') 
        return self.render_to_response(context)


class ProjectsView(kolektiMixin, View):
    template_name = "projects.html"
    def get(self, request, require_svn_auth=False, project_folder="", project_url=""):
        
        context = self.get_context_data({
                    "active_project" :self.user_settings.active_project.encode('utf-8'),
                    "active_srclang":self.user_settings.active_srclang,
                    "require_svn_auth":require_svn_auth,
                    "projectfolder":project_folder,
                    "projecturl":project_url,
                    })
            
        return self.render_to_response(context)

    def post(self, request):
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username,password)
        if project_url=="":
        # create local project
            sync.export_project(project_folder)
            return self.get(request, require_svn_auth=False, project_folder=project_folder)
        else:
            try:
                sync.checkout_project(project_folder, project_url)
                return self.get(request)
            except ExcSyncNoSync:
                return self.get(request, require_svn_auth=True, project_folder=project_folder, project_url=project_url)
            

class ProjectsActivateView(ProjectsView):
    def get(self, request):
        project = request.GET.get('project')
        redirect = ''
        #        redirect = request.META.get('HTTP_REFERER', '')
        self.project_activate(project)
        if redirect == '':
            return super(ProjectsActivateView, self).get(request)
        else:
            
            return HttpResponseRedirect(redirect)


class ProjectsLanguageView(ProjectsView):
    def get(self, request):
        project = request.GET.get('lang')
        self.language_activate(project)
        return super(ProjectsLanguageView, self).get(request)

        
class TocsListView(kolektiMixin, View):
    template_name = 'tocs/list.html'
    

class TocView(kolektiMixin, View):
    template_name = "tocs/detail.html"

    def get(self, request):
        context = self.get_context_data()
        tocpath = request.GET.get('toc')
        tocfile = tocpath.split('/')[-1]
        tocdisplay = os.path.splitext(tocfile)[0]
        toctitle, tocmeta, toccontent = self.get_toc_edit(tocpath)
        context.update({'tocfile':tocfile,
                        'tocdisplay':tocdisplay,
                        'toctitle':toctitle,
                        'toccontent':toccontent,
                        'tocpath':tocpath,
                        'tocmeta':tocmeta})
#        context.update({'criteria':self.get_criteria()})
        context.update({'jobs':self.get_jobs()})
        #print context
        return self.render_to_response(context)
    
    def post(self, request):
        try:
#            print request.body
            xtoc=self.parse_string(request.body)
            tocpath = xtoc.get('data-kolekti-path')
            xtoc_save = self.get_xsl('django_toc_save')
            xtoc = xtoc_save(xtoc)
            self.write(str(xtoc), tocpath)
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


class TocCreateView(kolektiMixin, View):
    template_name = "home.html"
    def post(self, request):
        try:
            tocpath = request.POST.get('tocpath')
            tocpath = self.set_extension(tocpath, ".html")
            toc = self.parse_html_string("""<?xml version="1.0"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>toc</title></head>
  <body></body>
</html>""")
            self.xwrite(toc, tocpath)
        except:
            import  traceback
            print traceback.format_exc()
        return HttpResponse(json.dumps(self.path_exists(tocpath)),content_type="application/json")


class ReleaseListView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"

class ReleaseStateView(kolektiMixin, TemplateView):
    def get(self, request):
        path, assembly_name = request.GET.get('release').rsplit('/',1)
        lang = request.GET.get('lang', self.user_settings.active_srclang)
        state = self.syncMgr.propget("release_state","/".join([path,"sources",lang,"assembly",assembly_name+'.html']))
        return HttpResponse(state)

    def post(self,request):
        path, assembly_name = request.POST.get('release').rsplit('/',1)
        state = request.POST.get('state')
        lang = request.POST.get('lang')
        self.syncMgr.propset("release_state",state,"/".join([path,"sources",lang,"assembly",assembly_name+'.html']))
        return HttpResponse(state)
        
class ReleaseCopyView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"
    def post(self,request):
        try:
            release = request.POST.get('release')
            path, assembly_name = release.rsplit('/',1) 
            srclang = request.POST.get('release_copy_from_lang')
            dstlang = request.POST.get('release_lang')

            #            return StreamingHttpResponse(
            for copiedfiles in self.copy_release(path, assembly_name, srclang, dstlang):
                pass
        except:
            import traceback
            print traceback.format_exc()
    #    return HttpResponse("ok")
        return HttpResponseRedirect('/releases/detail/?release=%s&lang=%s'%(path,dstlang))
    
class ReleaseAssemblyView(kolektiMixin, TemplateView):
    def get(self, request):
        release_path, assembly_name = request.GET.get('release').rsplit('/',1)
        lang = request.GET.get('lang', self.user_settings.active_srclang)
        assembly_path = os.path.join(release_path,"sources",lang,"assembly",assembly_name+".html")
        content = self.get_assembly_edit(assembly_path, release_path=release_path),
        return HttpResponse(content)
    
        
class ReleaseDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"
    def get(self, request):
        release_path = request.GET.get('release')
        lang = request.GET.get('lang', self.user_settings.active_srclang)
        assembly_name = [f['name'] for f in self.get_directory('%s/sources/%s/assembly'%(release_path, lang)) if f['name'][-5:] == '.html'][0][:-5]
        
        assembly_path = os.path.join(release_path,"sources",lang,"assembly",assembly_name+".html")
        #print self.get_assembly_edit(assembly_path)
        context = self.get_context_data({
            'releasesinfo':self.release_details(release_path, lang),
            'success':True,
            'release_path':release_path,
            'assembly_name':assembly_name,
            'lang':lang,
#            'content':self.get_assembly_edit(assembly_path, release_path=release_path),
        })
        states = []
        focus = []
        for lang in context.get('srclangs',[]):
            tr_assembly_path = release_path+"/sources/"+lang+"/assembly/"+assembly_name+'.html'
            if self.path_exists(tr_assembly_path):
                states.append(self.syncMgr.propget('release_state',tr_assembly_path))
            else:
                states.append("unknown")
            try:
                focus.append(ReleaseFocus.objects.get(release = release_path, assembly = assembly_name, lang = lang))
            except:
                import traceback
                print traceback.format_exc()
                focus.append(False)
                
        context.update({'langstates':zip(context.get('srclangs',[]),states,focus)})
        #print json.dumps(context, indent=2)
        return self.render_to_response(context)
        #        return HttpResponse(self.read(path+'/kolekti/manifest.json'),content_type="application/json")
    
    def post(self, request):
        release, assembly = request.GET.get('release',"").rsplit('/',1)
         
        lang=request.GET.get('lang',self.user_settings.active_srclang)
        assembly_path = '/'.join([release,'sources',lang,'assembly',assembly+'.html'])
        xassembly = self.parse(assembly_path)
        xbody = self.parse_html_string(request.body)
        body = xassembly.xpath('/h:html/h:body',namespaces={'h':'http://www.w3.org/1999/xhtml'})[0]
        for e in xassembly.xpath('/h:html/h:body/*',namespaces={'h':'http://www.w3.org/1999/xhtml'}):
            body.remove(e)
        for e in xbody.xpath('/html/body/*'):
            body.append(e)
        xsl = self.get_xsl('django_assembly_save')
        xassembly = xsl(xassembly, prefixrelease='"%s"'%release)
        self.xwrite(xassembly, assembly_path)
        return HttpResponse(json.dumps({'status':'ok'}))

class ReleasePublishView(kolektiMixin, TemplateView):
    def post (self, request):
        release, assembly = request.POST.get('release',"/").rsplit('/',1)
        langs = request.POST.getlist('langs[]',[])
        context={}

#        jobpath = release + '/kolekti/publication-parameters/' + assembly + '.xml'
#        print jobpath
#        xjob = self.parse(jobpath)
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        try:
            p = publish.ReleasePublisher(projectpath, langs=langs)
            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(release, assembly)), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

class TopicsListView(kolektiMixin, TemplateView):
    template_name = "topics/list.html"

class ImagesListView(kolektiMixin, TemplateView):
    template_name = "illustrations/list.html"

class ImagesUploadView(kolektiMixin, TemplateView):
    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            path = request.POST['path']
            self.write_chunks(uploaded_file.chunks,path +'/'+ uploaded_file.name, mode = "wb") 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class ImagesDetailsView(kolektiMixin, TemplateView):
    template_name = "illustrations/details.html"
    def get(self, request):
        path = request.GET.get('path')
        name = path.rsplit('/',1)[1]
        ospath = self.getOsPath(path)
        im = Image.open(ospath)
        context = self.get_context_data({
            'fileweight':"%.2f"%(float(os.path.getsize(ospath)) / 1024),
            'name':name,
            'path':path,
            'format':im.format,
            'mode':im.mode,
            'size':im.size,
            'info':im.info,
            })
        return self.render_to_response(context)


class VariablesListView(kolektiMixin, TemplateView):
    template_name = "variables/list.html"

class VariablesDetailsView(kolektiMixin, TemplateView):
    template_name = "variables/details.html"
    def get(self, request):
        path = request.GET.get('path')
        name=path.rsplit('/',1)[1]
        ospath = self.getOsPath(path)

        context = self.get_context_data({
            'name':name,
            'path':path,
            })
        return self.render_to_response(context)

    def post(self, request):
        try:
            xvar = self.parse_string(request.body)
            varpath = request.GET.get('path')
            self.xwrite(xvar, varpath)
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


    
class VariablesUploadView(kolektiMixin, TemplateView):
    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            uploaded_file = request.FILES[u'upload_file']
            path = request.POST['path']
            projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
            converter = OdsToXML(projectpath)
            varpath = path + "/" + uploaded_file.name.replace('.ods', '.xml')
            converter.convert(uploaded_file, varpath)
            # self.write_chunks(uploaded_file.chunks,path +'/'+ uploaded_file.name) 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class VariablesODSView(kolektiMixin, View):
    def get(self, request):
        path = request.GET.get('path')
        filename = path.rsplit('/',1)[1].replace('.xml','.ods')
        odsfile = StringIO()
        projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
        converter = XMLToOds(projectpath)
        converter.convert(odsfile, path)
        response = HttpResponse(odsfile.getvalue(),
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response


    
class ImportView(kolektiMixin, TemplateView):
    template_name = "import.html"
    def get(self, request):
        lang = self.user_settings.active_srclang
        tpls = self.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        
        context = self.get_context_data({'templates':tnames})
        return self.render_to_response(context)

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
            uploaded_file = request.FILES[u'upload_file']
            filename = str(uploaded_file)

            importer = Importer(projectpath, lang=self.user_settings.active_srclang)
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
        context = self.get_context_data({'events':events})
        return self.render_to_response(context)
            
class ImportTemplateView(kolektiMixin, TemplateView):
    def get(self, request):
        template = request.GET.get('template')
        filename = "import_template.ods"
        odsfile = StringIO()
        projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
        tplter = Templater(projectpath)
        tplter.generate("/sources/"+self.user_settings.active_srclang+"/templates/"+template, odsfile)
        response = HttpResponse(odsfile.getvalue(),                            
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response

    
class SettingsJsView(kolektiMixin, TemplateView):
    def get(self, request):
        settings_js="""
        var kolekti = {
        "lang":"%s"
        }
        """%(self.user_settings.active_srclang,)
        return HttpResponse(settings_js,content_type="text/javascript")
    
class SettingsJsonView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"
    def get(self, request):
        context = self.get_context_data()
        context.pop('syncinfo')
        return HttpResponse(json.dumps(context),content_type="application/json")
        

class SettingsView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

class JobCreateView(kolektiMixin, View):
    def post(self, request):        
        try:
            path = request.POST.get('path')
            path = self.set_extension(path, ".xml")
            ospath = self.getOsPath(path)
            jobid, ext = os.path.splitext(os.path.basename(path))
            if not len(ext):
                ext = ".xml"
            job = self.parse_string('<job id="%s"><dir value="%s"/><criteria/><profiles/><scripts/></job>'%(jobid, jobid))
            self.xwrite(job, os.path.join(os.path.dirname(path),jobid + ext))
            return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
        

class JobEditView(kolektiMixin, TemplateView):
    template_name = "settings/job.html"

    def get(self, request):
        context = self.get_context_data()
#        context.update({'jobs':self.get_jobs()})
        context.update({'job':self.get_job_edit(request.GET.get('path'))})
        context.update({'path':request.GET.get('path')})
        return self.render_to_response(context)

    def post(self, request):
        try:
            xjob = self.parse_string(request.body)
            jobpath = request.GET.get('path')
            self.xwrite(xjob, jobpath)
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


class CriteriaView(kolektiMixin, View):
    def get(self, request):
        return HttpResponse(self.read('/kolekti/settings.xml'),content_type="text/xml")

class CriteriaCssView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml')
            xsl = self.get_xsl('django_criteria_css')
            #print xsl(settings)
            return HttpResponse(str(xsl(settings)), "text/css")
        except:
            import traceback
            print traceback.format_exc()
            
class CriteriaJsonView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request):
        try:
            criterias = self._get_criteria_def_dict()
            return HttpResponse(json.dumps(criterias),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
    
                
class CriteriaEditView(kolektiMixin, TemplateView):
    template_name = "settings/criteria.html"

    def get(self, request):
        context = self.get_context_data()
        settings = self.parse('/kolekti/settings.xml')
        criteria = []
        for xcriterion in settings.xpath('/settings/criteria/criterion'):
            criteria.append(
                {'code':xcriterion.get('code'),
                'type':xcriterion.get('type'),
                'values':[str(v.text) for v in xcriterion.findall("value")]
                })
        context.update({'criteria':criteria})
        return self.render_to_response(context)
    def post(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml')
            xcriteria = self.parse_string(request.body)
            xsettingscriteria=settings.xpath('/settings/criteria')[0]
            for xcriterion in xsettingscriteria:
                xsettingscriteria.remove(xcriterion)
                
            for xcriterion in xcriteria.xpath('/criteria/criterion'):
                xsettingscriteria.append(xcriterion)
            self.xwrite(settings, '/kolekti/settings.xml')
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
   
class BrowserExistsView(kolektiMixin, View):
    def get(self,request):
        path = request.GET.get('path','/')
        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        
class BrowserMkdirView(kolektiMixin, View):
    def post(self,request):
        path = request.POST.get('path','/')
        self.makedirs(path)
        return HttpResponse("",content_type="text/plain")
#        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")

class BrowserMoveView(kolektiMixin, View):
    def post(self,request):
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        self.move_resource(src, dest)
        return HttpResponse("",content_type="text/plain")
        #return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")

class BrowserCopyView(kolektiMixin, View):
    def post(self,request):
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        self.copy_resource(src, dest)
        return HttpResponse("",content_type="text/plain")
        #return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")


class BrowserDeleteView(kolektiMixin, View):
    def post(self,request):
        path = request.POST.get('path','/')
        try:
            self.delete_resource(path)
        except:
            import traceback
            print traceback.format_exc()

        return HttpResponse("",content_type="text/plain")

class BrowserView(kolektiMixin, View):
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
            
    def get(self,request):
        try:
            context = self.get_context_data()
            path = request.GET.get('path','/')
            mode = request.GET.get('mode','select')

            files = filter(self.__browserfilter, self.get_directory(path))
        
            for f in files:
                f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
                        
            pathsteps = []
            startpath = ""
            for step in path.split("/")[1:]:
                startpath = startpath + "/" + step
                pathsteps.append({'label':step, 'path': startpath})

            context.update({'files':files})
            context.update({'pathsteps':pathsteps})
            context.update({'mode':mode})
            context.update({'path':path})
            context.update({'id':'browser_%i'%random.randint(1, 10000)})
            return self.render_to_response(context)
        except:
            import traceback
            print traceback.format_exc()

class BrowserReleasesView(BrowserView):
    def get_directory(self, path):

        try:
            res = []
            for assembly, date in self.get_release_assemblies(path):
                res.append({'name':assembly,
                            'type':"text/xml",
                            'date':date})

            return res
        except:
            import traceback
            print traceback.format_exc()
            return super(BrowserReleasesView, self).get_directory(path)
                      
            
class BrowserCKView(kolektiMixin, View):
    template_name = "browser/browser.html"
    def __browserfilter(self, entry):
        for exc in settings.RE_BROWSER_IGNORE:
            if re.search(exc, entry.get('name','')):
                return False
        return True
                         
    def get(self,request):
        context={}
        path = request.GET.get('path','/')
        mode = request.GET.get('mode','select')
        client_filter_name = request.GET.get('filter',None)
        client_filter = None
        if client_filter_name is not None:
            client_filter = getattr(self, client_filter_name)
            
        files = filter(self.__browserfilter, self.get_directory(path,client_filter))

        for f in files:
            f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
        pathsteps = []
        startpath = ""
        for step in path.split("/")[1:]:
            startpath = startpath + "/" + step
            pathsteps.append({'label':step, 'path': startpath})
        context.update({'files':files})
        context.update({'pathsteps':pathsteps})
        context.update({'mode':mode})
        context.update({'path':path})
        context.update({'editor':request.GET.get('CKEditor','_')})
        context.update({'funcnum':request.GET.get('CKEditorFuncNum','_')})
        
        context.update({'id':'browser_%i'%random.randint(1, 10000)})
        return self.render_to_response(context)

class BrowserCKUploadView(kolektiMixin, View):
    template_name = "browser/main.html"



    
class PublicationView(kolektiMixin, View):
    template_name = "publication.html"
    def __init__(self, *args, **kwargs):
        super(PublicationView, self).__init__(*args, **kwargs)
        self.loggerstream = StringIO()
        import logging
        self.loghandler = logging.StreamHandler(stream = self.loggerstream)
        self.loghandler.setLevel(logging.WARNING)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(levelname)-8s ; %(message)s\n')
        # tell the handler to use this format
        self.loghandler.setFormatter(formatter)
        # add the handler to the root logger
        rl = logging.getLogger('')
        rl.addHandler(self.loghandler)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PublicationView, cls).as_view(**initkwargs)
        return condition(etag_func=None)(view)

class DraftView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')
        pubdir  = request.POST.get('pubdir')
        pubtitle= request.POST.get('pubtitle')
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = self.parse(jobpath)
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
                else:
                    jprofile.set('enabled',"1")
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.get('name') in scripts:
                    jscript.getparent().remove(jscript)
                else:
                    jscript.set('enabled',"1")

            xjob.getroot().set('pubdir',pubdir)
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)

            p = publish.DraftPublisher(projectpath, lang=self.user_settings.active_srclang)
            return StreamingHttpResponse(self.format_iterator(p.publish_draft(tocpath, xjob, pubtitle)), content_type="text/html")

        except:
            import traceback
            self.loghandler.flush()
            print self.loggerstream
            context.update({'success':False})
            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)
        
class ReleaseView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')
        pubdir  = request.POST.get('pubdir')
#        pubtitle= request.POST.get('pubtitle')

        # print request.POST

        profiles = request.POST.getlist('profiles[]',[])
        # print profiles
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = self.parse(jobpath)
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.get('name') in scripts:
                    jscript.getparent().remove(jscript)

            xjob.getroot().set('pubdir',pubdir)
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            return StreamingHttpResponse(self.format_iterator(self.release_iter(projectpath, tocpath, xjob)))
#            r = publish.Releaser(projectpath, lang=self.user_settings.active_srclang)
#            pp = r.make_release(tocpath, xjob)
            

#            release_dir = pp[0]['assembly_dir']
            
#            p = publish.ReleasePublisher(projectpath, langs=[self.user_settings.active_srclang])
#            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(release_dir, pp[0]['pubname'])), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            self.loghandler.flush()
            context.update({'success':False})
            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})
            
            return self.render_to_response(context)

    def release_iter(self, projectpath, tocpath, xjob):
        r = publish.Releaser(projectpath, lang=self.user_settings.active_srclang)
        pp = r.make_release(tocpath, xjob)
        release_dir = pp[0]['assembly_dir']
        yield {
            'event':'release',
            'ref':release_dir,
            'time':pp[0]['datetime'],
        }

            
        p = publish.ReleasePublisher(projectpath, langs=[self.user_settings.active_srclang])
        for e in p.publish_assembly(release_dir, pp[0]['pubname']):
            yield e
            
            
class TopicEditorView(kolektiMixin, View):
    template_name = "topics/edit-ckeditor.html"
    def get(self, request):
        topicpath = request.GET.get('topic')
        topictitle, topicmeta, topiccontent = self.get_topic_edit(topicpath)
        context = self.get_context_data({"body":topiccontent,
                                         "title": self.basename(topicpath),
                                         "meta":topicmeta
                                         })
        return self.render_to_response(context)

    def post(self,request):
        try:
            path=request.GET['topic']
            try:
                s = request.META['HTTP_METADATA']
                meta = dict([m.split(':') for m in s.split(';')])
            except KeyError:
                meta = {}
            xbody = self.parse_html_string(request.body)
            
            xtopic = self.parse(path.replace('{LANG}',self.user_settings.active_srclang))
            body = xtopic.xpath('/h:html/h:body',namespaces={'h':'http://www.w3.org/1999/xhtml'})[0]
            for e in xtopic.xpath('/h:html/h:body/*',namespaces={'h':'http://www.w3.org/1999/xhtml'}):
                body.remove(e)
            for e in xbody.xpath('/html/body/*'):
                body.append(e)
            for metaname, metavalue in meta.iteritems():
                if len(xtopic.xpath('/h:html/h:head/h:meta[@name="%s"][@content]'%metaname,namespaces={'h':'http://www.w3.org/1999/xhtml'})):
                    xtopic.xpath('/h:html/h:head/h:meta[@name="%s"]'%metaname,namespaces={'h':'http://www.w3.org/1999/xhtml'})[0].set('content', metavalue)
                else:
                    ET.SubElement(xtopic.xpath('/h:html/h:head',namespaces={'h':'http://www.w3.org/1999/xhtml'})[0], "{http://www.w3.org/1999/xhtml}meta", {"name":metaname,"content":metacontent})
                    
                    
            self.xwrite(xtopic, path)
            return HttpResponse(json.dumps({'status':'ok'}))
        except:
            import  traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'error'}))

class TopicMetaJsonView(kolektiMixin, View):
    def get(self, request):
        path=request.GET['topic']
        xtopic = self.parse(path.replace('{LANG}',self.user_settings.active_srclang))
        metaelts = xtopic.xpath('/h:html/h:head/h:meta[@name][@content]',namespaces={'h':'http://www.w3.org/1999/xhtml'})
        meta = [{'name':m.get('name'),'content':m.get('content')} for m in metaelts]
        return HttpResponse(json.dumps(meta))
    
class TopicCreateView(kolektiMixin, View):
    template_name = "home.html"
    def post(self, request):
        try:
            modelpath = '/sources/'+ self.user_settings.active_srclang + "/templates/" + request.POST.get('model')
            topicpath = request.POST.get('topicpath')
            topicpath = self.set_extension(topicpath, ".html")
            topic = self.parse(modelpath)
            self.xwrite(topic, topicpath)
        except:
            import  traceback
            print traceback.format_exc()
        return HttpResponse(json.dumps(self.path_exists(topicpath)),content_type="application/json")

class TopicTemplatesView(kolektiMixin, View):
    def get(self, request):
        lang = request.GET.get('lang')
        tpls = self.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        return HttpResponse(json.dumps(tnames),content_type="application/json")

class TocUsecasesView(kolektiMixin, View):
    def get(self, request):
        pathes = request.GET.getlist('pathes[]',[])
        context={}
        for toc in self.itertocs:
            xtoc=self.parse(toc)
            for path in pathes:
                if len(xtoc.xpath('//html:a[@href="%s"]'%path,namespaces={'html':'http://www.w3.org/1999/xhtml'})):
                    try:
                        context[path].append(toc)
                    except:
                        context[path]=[toc]
        return HttpResponse(json.dumps(context),content_type="application/json")


class SearchView(kolektiMixin, View):
    template_name = "search/results.html"
    def get(self, request):
        context = self.get_context_data()
        q = request.GET.get('query')
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        s = searcher(projectpath)
        results = s.search(q)
        context.update({"results":results})
        context.update({"query":q})
        return self.render_to_response(context)



class SyncView(kolektiMixin, View):
    template_name = "synchro/main.html"
    def get(self, request):
        context = self.get_context_data()
        try:
            from kolekti.synchro import SynchroManager
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            sync = SynchroManager(projectpath)
            context.update({
                    "history": sync.history(),
                    "changes": sync.statuses(),
                    })
        except ExcSyncNoSync:
            import traceback
            print traceback.format_exc()
            context.update({'status':'nosync'})
        return self.render_to_response(context)

    def post(self, request):
        from kolekti.synchro import SynchroManager
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        sync = SynchroManager(projectpath)
        action = request.POST.get('action')
        commitmsg = request.POST.get('commitmsg',u"").encode('utf-8')
        if len(commitmsg) == 0:
            commitmsg = "unspecified"
        if action == "conflict":
            resolve = request.POST.get('resolve')
            files = [f.encode('utf-8') for f in request.POST.getlist('fileselect',[])]
            if resolve == "local":
                sync.update(files)
                for file in files:
                    if os.path.exists(file+'.mine'):
                        shutil.copy(file+'.mine', file)
                        sync.resolved(file)
                sync.commit(files, commitmsg)
            if resolve == "remote":
                sync.revert(files)

        elif action == "merge":
            files = request.POST.getlist('fileselect',[])
            sync.update(files)
                
        elif action == "update":
            sync.update_all()
            
        elif action == "commit":
            files = [f.encode('utf-8') for f in request.POST.getlist('fileselect',[])]
            sync.commit(files,commitmsg)
            
            
        return self.get(request)
                    
class SyncRevisionView(kolektiMixin, View):
    template_name = "synchro/revision.html"
    def get(self, request, rev):
        from kolekti.synchro import SynchroManager
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        sync = SynchroManager(projectpath)
        revsumm, revinfo, difftext = sync.revision_info(rev)
        context = self.get_context_data({
            "history": sync.history(),
            'revsumm':revsumm,
            'revinfo':revinfo,
            'difftext':difftext,
            })
        
        return self.render_to_response(context)




class SyncDiffView(kolektiMixin, View):
    template_name = "synchro/diff.html"
    def get(self, request):
        entry = request.GET.get("file")
        from kolekti.synchro import SynchroManager
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        sync = SynchroManager(projectpath)
        diff,  headdata, workdata = sync.diff(entry) 
        import difflib
        #htmldiff = hd.make_table(headdata.splitlines(), workdata.splitlines())
        context = self.get_context_data({
            'diff':difflib.ndiff(headdata.splitlines(), workdata.splitlines()),
            'headdata':headdata,
            'workdata':workdata,
#            'htmldiff':htmldiff,
            })
        
        return self.render_to_response(context)




class projectStaticView(kolektiMixin, View):
    def get(self, request, path):
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)        
        return serve(request, path, projectpath)
