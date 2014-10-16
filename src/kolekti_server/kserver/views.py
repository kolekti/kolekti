from lxml import etree as ET
from django.http import Http404
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
#from models import kolektiMixin
from django.views.generic.base import TemplateResponseMixin
from django.conf import settings
# Create your models here.
from kolekti.common import kolektiBase, XSLExtensions
from kolekti.publish import PublisherExtensions
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import HttpResponse

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
        xsl = self.get_xsl('django_toc_edit', extclass=PublisherExtensions, lang='fr')
        try:
            etoc = xsl(xtoc)
        except:
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return toctitle, str(etoc)

    def get_tocs(self):
        return self.itertocs

    def get_jobs(self):
        return self.iterjobs

    def get_job_edit(self,path):
        xjob = self.parse(path)
        xsl = self.get_xsl('django_job_edit', extclass=PublisherExtensions, lang='fr')
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
        toctitle, toccontent = self.get_toc_edit(request.GET.get('toc'))
        context.update({'toctitle':toctitle,'toccontent':toccontent})
#        context.update({'criteria':self.get_criteria()})
        context.update({'jobs':self.get_jobs()})
        return self.render_to_response(context)
    
    def post(self, request):
        print request.body
        return HttpResponse('ok')

class TranslationsListView(ListView):
    template_name = "home.html"

class TopicsListView(TemplateView):
    template_name = "home.html"

class ImagesListView(TemplateView):
    template_name = "home.html"

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

class CriteriaEditView(kolektiMixin, TemplateView):
    template_name = "settings.html"

    def get(self, request):
        context = self.get_context_data()
        context.update({'jobs':self.get_jobs()})
        return self.render_to_response(context)
