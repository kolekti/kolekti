# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os

import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.views.generic import View, TemplateView, ListView

# kolekti imports
from kserver.views import kolektiMixin
from kolekti.common import kolektiBase
from kolekti.variables import AuditVariables


class HomeView(kolektiMixin,TemplateView):
    template_name="audit/index.html"
    
class AuditVariablesView(kolektiMixin,TemplateView):
    template_name="audit/result.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        audit = AuditVariables(kolekti.getOsPath('/')).audit_all('en')
        context.update({'audit':audit})
        return self.render_to_response(context)
    
class AuditVariablesSourceTranslationsView(kolektiMixin,TemplateView):
    template_name="audit/result_source_translations.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        audit = AuditVariables(kolekti.getOsPath('/'))
        
        context.update({
            'audit':audit.audit_source_translations('en'),
            'trlangs':audit.audit_list_translation_langs('en')
            })
        return self.render_to_response(context)
    

    
