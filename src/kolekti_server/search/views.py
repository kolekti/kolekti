# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.shortcuts import render
from django.views.generic import View, TemplateView, ListView


# Create your views here.
class HomeView(TemplateView):
    template_name="search/index.html"
    pass
