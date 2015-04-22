import re
import os
from copy import copy
import json

from lxml import etree as ET

from models import Settings

from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.static import serve 
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator


# kolekti imports
from kolekti.common import kolektiBase
from kolekti.publish import PublisherExtensions
from kolekti.searchindex import searcher
from kolekti.exceptions import ExcSyncNoSync

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

    def get_context_data(self, **kwargs):
        context = {}
        context['kolekti'] = self._config
        return context

    def get_toc_edit(self, path):
        xtoc = self.parse(path)
        toctitle = xtoc.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        tocjob = xtoc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_toc_edit', extclass=PublisherExtensions, lang=self.user_settings.active_srclang)
        try:
            etoc = xsl(xtoc)
        except:
            import traceback
            print traceback.format_exc()
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return toctitle, tocjob, str(etoc)

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

    def get_tocs(self):
        return self.itertocs

    def get_jobs(self):
        res = []
        for job in self.iterjobs:
            xj = self.parse(job['path'])
            job.update({'profiles':[p.text for p in xj.xpath('/job/profiles/profile/label')],
                        'scripts':[s.get("name") for s in xj.xpath('/job/scripts/script[@enabled="1"]')],
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
            ejob = xsl(xjob, path="'%s'"%path)
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
        languages=[l.text for l in projectsettings.xpath('/settings/languages/lang')]
        defaultlang = projectsettings.xpath('string(/settings/@sourcelang)')
        if not self.user_settings.active_srclang in languages:
             self.user_settings.active_srclang = defaultlang
        self.user_settings.save()

    def language_activate(self,language):
        # get userdir
        self.user_settings.active_srclang = language
        self.user_settings.save()
        
        
class HomeView(kolektiMixin, View):
    template_name = "home.html"
    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)


class ProjectsView(kolektiMixin, View):
    template_name = "projects.html"
    def get(self, request):
        projects = []
        for projectname in os.listdir(settings.KOLEKTI_BASE):
            project={'name':projectname}
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
            
        context = {"projects" : projects,
                   "active_project" :self.user_settings.active_project.encode('utf-8'),
                   "active_srclang":self.user_settings.active_srclang,
                   }
            
        return self.render_to_response(context)

    def post(self, request):
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE)
        if project_url=="":
            # create local project
            sync.export_project(project_folder)
        else:
            sync.checkout_project(project_folder, project_url)

        return self.get(request)


class ProjectsActivateView(ProjectsView):
    def get(self, request):
        project = request.GET.get('project')
        self.project_activate(project)
        return super(ProjectsActivateView, self).get(request)
    


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
        toctitle, tocjob, toccontent = self.get_toc_edit(tocpath)
        
        context.update({'tocfile':tocfile,'tocdisplay':tocdisplay,'toctitle':toctitle,'toccontent':toccontent,'tocpath':tocpath, 'tocjob':tocjob})
#        context.update({'criteria':self.get_criteria()})
        context.update({'jobs':self.get_jobs()})
        #print context
        return self.render_to_response(context)
    
    def post(self, request):
        try:
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

class ReleaseDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"
    def get(self, request):
        path = request.GET.get('release')
        lang = request.GET.get('lang', self.user_settings.active_srclang)
        context = self.get_context_data()
        context.update({
            'releasesinfo':self.release_details(path, lang),
            'success':True,
            'lang':lang,
        })
        #print json.dumps(context, indent=2)
        return self.render_to_response(context)
        #        return HttpResponse(self.read(path+'/kolekti/manifest.json'),content_type="application/json")
    
class TopicsListView(kolektiMixin, TemplateView):
    template_name = "topics/list.html"

class ImagesListView(kolektiMixin, TemplateView):
    template_name = "list.html"

class ImportView(kolektiMixin, TemplateView):
    template_name = "home.html"


class SettingsJsView(kolektiMixin, TemplateView):
    def get(self, request):
        settings_js="""
        var kolekti = {
        "lang":"%s"
        }
        """%(self.user_settings.active_srclang,)
        return HttpResponse(settings_js,content_type="text/javascript")
    
class SettingsView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"

    def get(self, request):
        context = self.get_context_data()
        context.update({'jobs':self.get_jobs()})
        return self.render_to_response(context)

class JobCreateView(kolektiMixin, View):
    def post(self, request):        
        try:
            path = request.POST.get('path')
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
        context.update({'jobs':self.get_jobs()})
        context.update({'job':self.get_job_edit(request.GET.get('path'))})
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
                         
    def get(self,request):
        context={}
        path = request.GET.get('path','/')
        mode = request.GET.get('mode','select')
        files = filter(self.__browserfilter,self.get_directory(path))
        
        for f in files:
            # print f.get('type')
            f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
        pathsteps = []
        startpath = ""
        for step in path.split("/")[1:]:
            startpath= startpath + "/" + step
            pathsteps.append({'label':step, 'path': startpath})
        context.update({'files':files})
        context.update({'pathsteps':pathsteps})
        context.update({'mode':mode})
        return self.render_to_response(context)
        
class PublicationView(kolektiMixin, View):
    template_name = "publication.html"
    def __init__(self, *args, **kwargs):
        super(PublicationView, self).__init__(*args, **kwargs)
        import StringIO
        self.loggerstream = StringIO.StringIO()
        import logging
        self.loghandler = logging.StreamHandler(stream = self.loggerstream)
        self.loghandler.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        self.loghandler.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(self.loghandler)
    
class DraftView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = self.parse(jobpath)
        # print ET.tostring(xjob), profiles, scripts ,request.POST
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.get('name') in scripts:
                    jscript.getparent().remove(jscript)
            # print ET.tostring(xjob)
            from kolekti import publish
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            p = publish.DraftPublisher(projectpath, lang=self.user_settings.active_srclang)
        
            pubres = p.publish_draft(tocpath, [xjob])
            context.update({'pubres':pubres})
            context.update({'success':True})
        except:
            import traceback
            print traceback.format_exc()
            self.loghandler.flush()
            context.update({'success':False})
            context.update({'logger':self.loggerstream.getvalue()})        

        return self.render_to_response(context)
        
class ReleaseView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')

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

            from kolekti import publish
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            r = publish.Releaser(projectpath, lang=self.user_settings.active_srclang)
            pp = r.make_release(tocpath, [xjob])
            #print "----"
            #print pp
            #print "----"
            release_dir = pp[0]['assembly_dir'].replace('/releases/','')
            p = publish.ReleasePublisher(projectpath, lang=self.user_settings.active_srclang)
            pubres = p.publish_assembly(release_dir, pp[0]['pubname'])
            #print pubres
            context.update({'pubres':pubres})
            context.update({'success':True})
        except:
            import traceback
            print traceback.format_exc()
            self.loghandler.flush()
            context.update({'success':False})
            context.update({'logger':self.loggerstream.getvalue()})        

        return self.render_to_response(context)

class TopicEditorView(kolektiMixin, View):
    template_name = "topics/edit-ckeditor.html"
    def get(self, request):
        topicpath = request.GET.get('topic')
        topictitle, topicmeta, topiccontent = self.get_topic_edit(topicpath)
        context = {"body":topiccontent, "title": topictitle, "meta":topicmeta}
        return self.render_to_response(context)

    def post(self,request):
        try:
            path=request.GET['topic']
            xbody = self.parse_html_string(request.body)
            
            xtopic = self.parse(path.replace('{LANG}',self.user_settings.active_srclang))
            body = xtopic.xpath('/h:html/h:body',namespaces={'h':'http://www.w3.org/1999/xhtml'})[0]
            for e in xtopic.xpath('/h:html/h:body/*',namespaces={'h':'http://www.w3.org/1999/xhtml'}):
                body.remove(e)
            for e in xbody.xpath('/html/body/*'):
                body.append(e)
            self.xwrite(xtopic, path)
            return HttpResponse(json.dumps({'status':'ok'}))
        except:
            import  traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'error'}))
    
class TopicCreateView(kolektiMixin, View):
    template_name = "home.html"
    def post(self, request):
        try:
            modelpath = '/sources/'+ self.user_settings.active_srclang + "/templates/" + request.POST.get('model')
            topicpath = request.POST.get('topicpath')
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
            changes = sync.statuses()
            newmerge = []
            newconflict = []
            for change in changes['merge']:
                mergeinfo = sync.merge_dryrun(change['path'])
                if len(mergeinfo['conflict']):
                    newconflict.append(change)
                else:
                    newmerge.append(change)
            changes.update({
                    "merge":newmerge,
                    "conflict":newconflict
                    })
            context.update({
                    "history": sync.history(),
                    "changes": changes,
                    "ok":len(changes['error'])==0
                    })
        except ExcSyncNoSync:
            
            context = {'status':'nosync'}
        return self.render_to_response(context)

class SyncStartView(kolektiMixin, View):
    template_name = "synchro/sync.html"
    def post(self, request):
        message = request.POST.get("syncromsg")
        from kolekti.synchro import SynchroManager
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
        sync = SynchroManager(projectpath)
        
        context = {
            'update':sync.update_all(),
            'commit':sync.commit_all(message)
            }
        
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
        context = {
            'diff':difflib.ndiff(headdata.splitlines(), workdata.splitlines()),
            'headdata':headdata,
            'workdata':workdata,
#            'htmldiff':htmldiff,
            }
        
        return self.render_to_response(context)




class projectStaticView(kolektiMixin, View):
    def get(self, request, path):
        projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)        
        return serve(request, path, projectpath)
