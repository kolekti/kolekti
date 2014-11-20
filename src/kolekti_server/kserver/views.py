from lxml import etree as ET
import json
import re
from django.http import Http404
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
#from models import kolektiMixin
from django.views.generic.base import TemplateResponseMixin
from django.conf import settings
# Create your models here.
from kolekti.common import kolektiBase, XSLExtensions
from kolekti.publish import PublisherExtensions
from kolekti.searchindex import searcher
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponse


fileicons= {
    "application/octet-stream":"glyphicon-file",
    "text/directory":"glyphicon-folder-close",
    }

class kolektiMixin(TemplateResponseMixin, kolektiBase):
    def __init__(self, *args, **kwargs):
        base = settings.KOLEKTI_BASE
        
        super(kolektiMixin, self).__init__(base,*args,**kwargs)

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
        xsl = self.get_xsl('django_toc_edit', extclass=PublisherExtensions, lang=settings.KOLEKTI_SRC_LANG)
        try:
            etoc = xsl(xtoc)
        except:
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return toctitle, tocjob, str(etoc)

    def get_topic_edit(self, path):
        xtopic = self.parse(path.replace('{LANG}',settings.KOLEKTI_SRC_LANG))
        topictitle = xtopic.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topicbody = xtopic.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        topiccontent = ''.join([ET.tostring(t) for t in topicbody])
        return topictitle, topiccontent

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
        xsl = self.get_xsl('django_job_edit', extclass=PublisherExtensions, lang=settings.KOLEKTI_SRC_LANG)
        try:
            ejob = xsl(xjob)
        except:
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return str(ejob)
    
class HomeView(TemplateView):
    template_name = "home.html"

    
class TocsListView(kolektiMixin, View):
    template_name = 'tocs/list.html'
    
    def get(self, request):
        context = self.get_context_data()
        context.update({'tocs':self.itertocs})
        return self.render_to_response(context)

class TocView(kolektiMixin, View):
    template_name = "tocs/detail.html"

    def get(self, request):
        context = self.get_context_data()
        tocpath = request.GET.get('toc')
        tocfile = tocpath.split('/')[-1]
        toctitle, tocjob, toccontent = self.get_toc_edit(tocpath)
        
        context.update({'tocfile':tocfile,'toctitle':toctitle,'toccontent':toccontent,'tocpath':tocpath, 'tocjob':tocjob})
#        context.update({'criteria':self.get_criteria()})
        context.update({'jobs':self.get_jobs()})
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

class ReleaseListView(TemplateView):
    template_name = "releases/list.html"

class ReleaseDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"
    def get(self, request):
        path = request.GET.get('path')
        lang = request.GET.get('lang', settings.KOLEKTI_SRC_LANG)
        context = self.get_context_data()
        context.update({
            'releasesinfo':self.release_details(path, lang),
            'success':True,
            'lang':lang,
        })
        print json.dumps(context, indent=2)
        return self.render_to_response(context)
        #        return HttpResponse(self.read(path+'/kolekti/manifest.json'),content_type="application/json")
    
class TopicsListView(TemplateView):
    template_name = "topics/list.html"

class ImagesListView(TemplateView):
    template_name = "list.html"

class SyncView(TemplateView):
    template_name = "home.html"

class ImportView(TemplateView):
    template_name = "home.html"


class SettingsView(kolektiMixin, TemplateView):
    template_name = "settings.html"

    def get(self, request):
        context = self.get_context_data()
        context.update({'jobs':self.get_jobs()})
        return self.render_to_response(context)


class JobEditView(kolektiMixin, TemplateView):
    template_name = "settings.html"

    def get(self, request):
        context = self.get_context_data()
        context.update({'jobs':self.get_jobs()})
        context.update({'job':self.get_job_edit(request.GET.get('job'))})
        return self.render_to_response(context)

class CriteriaView(kolektiMixin, View):
    def get(self, request):
        return HttpResponse(self.read('/kolekti/settings.xml'),content_type="text/xml")

class CriteriaCssView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml')
            xsl = self.get_xsl('django_criteria_css')
            print xsl(settings)
            return HttpResponse(str(xsl(settings)), "text/css")
        except:
            import traceback
            print traceback.format_exc()
            
class CriteriaEditView(kolektiMixin, TemplateView):
    template_name = "settings.html"

    def get(self, request):
        context = self.get_context_data()
        context.update({'jobs':self.get_jobs()})
        return self.render_to_response(context)
    
class BrowserExistsView(kolektiMixin, View):
    def get(self,request):
        path = request.GET.get('path','/')
        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        
class BrowserMkdirView(kolektiMixin, View):
    def post(self,request):
        path = request.POST.get('path','/')
        self.makedirs(path)
        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")

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
            f.update({'icon':fileicons.get(f.get('type'),"glyphicon-file")})
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
        print ET.tostring(xjob), profiles, scripts ,request.POST
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.get('name') in scripts:
                    jscript.getparent().remove(jscript)
            print ET.tostring(xjob)
            from kolekti import publish

            p = publish.DraftPublisher(settings.KOLEKTI_BASE, lang=settings.KOLEKTI_SRC_LANG)
        
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

        print request.POST

        profiles = request.POST.getlist('profiles[]',[])
        print profiles
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
            r = publish.Releaser(settings.KOLEKTI_BASE, lang=settings.KOLEKTI_SRC_LANG)
            pp = r.make_release(tocpath, [xjob])
            print "----"
            print pp
            print "----"
            release_dir = pp[0]['assembly_dir'].replace('/releases/','')
            p = publish.ReleasePublisher(settings.KOLEKTI_BASE, lang=settings.KOLEKTI_SRC_LANG)
            pubres = p.publish_assembly(release_dir, pp[0]['pubname'])
            print pubres
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
    template_name = "topics/edit.html"
    def get(self, request):
        topicpath = request.GET.get('topic')
        topictitle, topiccontent = self.get_topic_edit(topicpath)
        context = {"body":topiccontent, "title": topictitle}
        return self.render_to_response(context)

class TopicCreateView(kolektiMixin, View):
    def post(self, request):
        modelpath = request.POST.get('modelpath')
        topicpath = request.POST.get('topicpath')
        topic = self.parse(modelpath)
        self.xwrite(topic, topicpath)
        return HttpResponse(json.dumps(self.path_exists(topicpath)),content_type="application/json")


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
        s = searcher(settings.KOLEKTI_BASE)
        results = s.search(q)
        context.update({"results":results})
        context.update({"query":q})
        return self.render_to_response(context)
