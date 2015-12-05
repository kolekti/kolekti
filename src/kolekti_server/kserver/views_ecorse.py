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

    def write_report(self, report, release_path):
        report_name = release_path.rsplit('/',1)[1]
        report_path = "/".join([release_path,"sources","fr","assembly",report_name+"_asm.html"])
        self.xwrite(report, report_path)
        
    def _checkout(self, release):
        pass


class EcoRSEReportPublishView(EcoRSEMixin, View):
    def post(self, request):
        try:
            title = request.POST.get('title','')
            commune1 = request.POST.get('commune1','')
            commune2 = request.POST.get('commune2','')
            commune3 = request.POST.get('commune3','')
            tocpath = '/sources/fr/tocs/trame_sparql.html'
            xjob = self.parse('/kolekti/publication-parameters/report.xml')
            xjob.getroot().set('pubdir',title)
            lang=self.user_settings.active_srclang
            projectpath = os.path.join(settings.KOLEKTI_BASE,self.user_settings.active_project)
            criteria = xjob.xpath('/job/criteria')[0]
            ET.SubElement(criteria, 'criterion', attrib={"code":"codeINSEE1","value":commune1})
            ET.SubElement(criteria, 'criterion', attrib={"code":"codeINSEE2","value":commune2})
            ET.SubElement(criteria, 'criterion', attrib={"code":"codeINSEE3","value":commune3})
            r = publish.Releaser(projectpath, lang = lang)
            print ET.tostring(xjob)
            pp = r.make_release(tocpath, xjob)
        except:
            import traceback
            print traceback.format_exc()
            pp = []
        return HttpResponse(json.dumps(pp),content_type="application/json")
        

        
class EcoRSEReportUpdateView(EcoRSEMixin, View):
    def post(self, request):
        release_path = request.POST.get('release','')
        print release_path
        try:
            report = self.get_report(release_path)
            endpoint = self._project_settings.find('sparql').get('endpoint')
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
            topic_chart = report.xpath("//html:div[@id = '%s']//html:p[@class='kolekti-sparql-result-chartjs']"%topicid,
                                    namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
            topic_chart.set('data-chartjs-kind', chart )
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
            content = None
            menu = self.get_assembly_menu(release_path = release_path)
            assembly_name = None
        return self.render_to_response({"content":content,
                                        "current":assembly_name,
                                        "release":release_path,
                                        "menu":menu,
                                        "releases":releases,
                                        "title":assembly_name})
    
        

class EcoRSECommunesView(EcoRSEMixin, View):
    def get(self, request):
        endpoint = self._project_settings.find('sparql').get('endpoint')
        from kolekti.publish_queries import kolektiSparQL
        sp = kolektiSparQL(endpoint)
        communes = sp.get_communes()
        
        return HttpResponse(json.dumps(communes),content_type="application/json")
