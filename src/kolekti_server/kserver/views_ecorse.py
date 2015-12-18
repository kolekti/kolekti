# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import os
import json
from lxml import etree as ET

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
from kolekti import publish_queries
from kolekti.searchindex import searcher
from kolekti.exceptions import ExcSyncNoSync
from kolekti.variables import OdsToXML, XMLToOds
from kolekti.import_sheets import Importer, Templater

from views import kolektiMixin

class EcoRSEMixin(kolektiMixin):
    def render_to_response(self, context):
        context.update({'DEBUG': settings.DEBUG})
        return super(EcoRSEMixin, self).render_to_response(context)

    def get_assembly_edit(self, path, release_path="", section=None):
        xassembly = self.parse(path.replace('{LANG}',self.user_settings.active_publang))
        if section is None:
            section = xassembly.xpath('string(/html:html/html:body/html:div[1]/@id)',namespaces={'html':'http://www.w3.org/1999/xhtml'})

        body = xassembly.xpath('/html:html/html:body/html:div[@class="section"][@id="%s"]'%section, namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('ecorse_assembly_edit')
        content = ''.join([str(xsl(t, path="'%s'"%release_path, section="'%s'"%section)) for t in body])
        return content

    def get_assembly_menu(self, path, release_path="", section=None):
        xassembly = self.parse(path.replace('{LANG}',self.user_settings.active_publang))
        if section is None:
            section = xassembly.xpath('string(/html:html/html:body/html:div[1]/@id)',namespaces={'html':'http://www.w3.org/1999/xhtml'})
        body = xassembly.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('ecorse_assembly_menu')
        content = ''.join([str(xsl(t, path="'%s'"%release_path, section="'%s'"%section)) for t in body])
        return content

    def get_report(self, release_path):
        report_name = release_path.rsplit('/',1)[1]
        report_path = "/".join([release_path,"sources","fr","assembly",report_name+"_asm.html"])
        return self.parse(report_path)

    def get_job(self, release_path):
        report_name = release_path.rsplit('/',1)[1]
        job_path = "/".join([release_path,"kolekti","publication-parameters",report_name+"_asm.xml"])
        return self.parse(job_path)

    def write_report(self, report, release_path):
        report_name = release_path.rsplit('/',1)[1]
        report_path = "/".join([release_path,"sources","fr","assembly",report_name+"_asm.html"])
        self.xwrite(report, report_path)
        
    def _checkout(self, release):
        pass


class EcoRSEReportCreateView(EcoRSEMixin, View):
    def post(self, request):
        try:
            title = request.POST.get('title','')
            commune1 = request.POST.get('commune1','')
            commune2 = request.POST.get('commune2','')
            commune3 = request.POST.get('commune3','')
            toc = request.POST.get('toc')
            tocpath = '/sources/fr/tocs/ecorse/'+toc
            xjob = self.parse('/kolekti/publication-parameters/report.xml')
            xjob.getroot().set('pubdir',title)
            lang=self.user_settings.active_srclang
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            criteria = xjob.xpath('/job/criteria')[0]
            ET.SubElement(criteria, 'criterion', attrib={"code":"placeURI1","value":commune1})
            ET.SubElement(criteria, 'criterion', attrib={"code":"placeURI2","value":commune2})
            ET.SubElement(criteria, 'criterion', attrib={"code":"placeURI3","value":commune3})
            r = publish.Releaser(projectpath, lang = lang)
            pp = r.make_release(tocpath, xjob)
        except:
            import traceback
            print traceback.format_exc()
            pp = []
        return HttpResponse(json.dumps(pp),content_type="application/json")
        

        
class EcoRSEReportUpdateView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        try:
            report = self.get_report(release_path)
            endpoint = self._project_settings.find('sparql').get('endpoint')
            endpoint = endpoint + report.xpath('string(/h:html/h:head/h:meta[@name="kolekti.sparql.endpoint"]/@content)',   namespaces={'h':'http://www.w3.org/1999/xhtml'})
            from kolekti.publish_queries import kolektiSparQL
            sp = kolektiSparQL(endpoint)
            sp.process_queries(report)
            self.write_report(report, release_path)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")
    
class EcoRSEReportAnalysisView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        topicid =  request.POST.get('topic','')
        data =  request.POST.get('data','')
    
        try:
            xdata = self.parse_html_string(data)
            report = self.get_report(release_path)
            try:
                ana = report.xpath("//html:div[@id = '%s']/html:div[@class='analyse']"%topicid,
                                    namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
                for child in ana:
                    print child
                    ana.remove(child)
                print ET.tostring(ana)
            except IndexError:
                topic = report.xpath("//html:div[@id = '%s']"%topicid,
                                        namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
                ana = ET.SubElement(topic,'{http://www.w3.org/1999/xhtml}div', attrib = {"class":"analyse"})
            for elt in xdata.xpath('/html/body/*'):
                ana.append(elt)
            self.write_report(report, release_path)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
        
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")

    
class EcoRSEReportStarView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        topicid =  request.POST.get('topic','')
        state =  request.POST.get('state','')
        print state
        try:
            report = self.get_report(release_path)
            topic = report.xpath("//html:div[@id = '%s']"%topicid,
                                 namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
            if(state == 'true'):
                topic.set('data-star','yes')
            else:
                del topic.attrib['data-star']
            self.write_report(report, release_path)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
            
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")
    
class EcoRSEReportHideView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        topicid =  request.POST.get('topic','')
        state =  request.POST.get('state','')
        print state
        try:
            report = self.get_report(release_path)
            topic = report.xpath("//html:div[@id = '%s']"%topicid,
                                 namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
            if(state == 'true'):
                topic.set('data-hidden','yes')
            else:
                del topic.attrib['data-hidden']
            self.write_report(report, release_path)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
            
        return HttpResponse(json.dumps({'status':'ok'}),content_type="application/json")
    
class EcoRSEReportChartView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        topicid =  request.POST.get('topic','')
        chart =  request.POST.get('charttype','Bar')
        try:
            report = self.get_report(release_path)
            topic = report.xpath("//html:div[@id = '%s']"%topicid,
                                    namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
            topic.set('data-chart-kind', chart )
            self.write_report(report, release_path)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
            
        return HttpResponse(json.dumps({'status':'ok','chart':chart}),
                            content_type="application/json")

    
    
class EcoRSEReportView(EcoRSEMixin, View):
    template_name = "ecorse/report.html"
    def get(self, request):
            
        release_path = request.GET.get('release','')
        section = request.GET.get('section')
        releases = self.get_directory('/releases')
        try:
            assembly_name = release_path.rsplit('/',1)[1]
            self._checkout(release_path)
            assembly_path = "/".join([release_path,"sources","fr","assembly",assembly_name+"_asm.html"])
            content = self.get_assembly_edit(assembly_path, release_path = release_path, section = section)
            menu = self.get_assembly_menu(assembly_path, release_path = release_path, section = section)
        except IndexError:
            import traceback
            print traceback.format_exc()
            content = "Selectionnez un rapport"
            menu = None
            assembly_name = ""

        return self.render_to_response({"content":content,
                                        "current":assembly_name,
                                        "release":release_path,
                                        "menu":menu,
                                        "releases":releases,
                                        "title":assembly_name})
    
        
class EcoRSEReportView(EcoRSEMixin, View):
    template_name = "ecorse/share.html"
    def get(self, request):
            
        release_path = request.GET.get('release','')
        section = request.GET.get('section')
        try:
            assembly_name = release_path.rsplit('/',1)[1]
            self._checkout(release_path)
            assembly_path = "/".join([release_path,"sources","fr","assembly",assembly_name+"_asm.html"])
            content = self.get_assembly_edit(assembly_path, release_path = release_path, section = section)
            menu = self.get_assembly_menu(assembly_path, release_path = release_path, section = section)
        except IndexError:
            import traceback
            print traceback.format_exc()
            content = "Selectionnez un rapport"
            menu = None
            assembly_name = ""

        return self.render_to_response({"content":content,
                                        "current":assembly_name,
                                        "release":release_path,
                                        "menu":menu,
                                        "title":assembly_name})
    
        

class EcoRSECommunesView(EcoRSEMixin, View):
    def get(self, request):
        referentiel = request.GET.get('referentiel','')
        xtoc = self.parse('/sources/fr/tocs/ecorse/'+referentiel)
        endpoint = self._project_settings.find('sparql').get('endpoint')
        endpoint = endpoint + xtoc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.sparql.endpoint"]/@content)',namespaces={'html':'http://www.w3.org/1999/xhtml'})
        from kolekti.publish_queries import kolektiSparQL
        sp = kolektiSparQL(endpoint)
        communes = sp.get_communes()
        return HttpResponse(json.dumps(communes),content_type="application/json")

class EcoRSEReferentielsView(EcoRSEMixin, View):
    def get(self, request):
        try:
            referentiels = self.get_directory('/sources/fr/tocs/ecorse')
            return HttpResponse(json.dumps([r.get('name') for r in referentiels]),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")


class EcoRSEReportPublishView(EcoRSEMixin, View):
    def post(self, request):
        try:
            release_path = request.POST.get('release','')
            assembly_name = release_path.rsplit('/',1)[1] + "_asm"
            script = request.POST.get('script','')
            xjob = self.get_job(release_path)
            jscripts = xjob.getroot().find('scripts')
            for jscript in jscripts:
                if jscript.get('name') != script:
                    jscripts.remove(jscript)
            print ET.tostring(jscripts)
            lang=self.user_settings.active_srclang
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            r = publish.ReleasePublisher(release_path, projectpath, langs = [lang])
            res = []
            for e in r.publish_assembly(assembly_name, xjob):
                if e['event']=='error':
                    print e['stacktrace']
                res.append(e)
            return HttpResponse(json.dumps(res),content_type="application/json")           
        except:
            print res
            import traceback
            print traceback.format_exc()
            return HttpResponse(json.dumps({'status':'fail',
                                            'msg':traceback.format_exc()}),content_type="application/json")
