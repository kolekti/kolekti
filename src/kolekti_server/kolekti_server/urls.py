from django.conf.urls import include, url

from django.views.i18n import javascript_catalog
from django.views.static import serve as staticView
from django.contrib import admin

from django_js_reverse.views import urls_js

from kserver.views import HomeView, AboutView, ChangelogView
from kserver_saas.views import *


urls = [
    url(r'^$', HomeView.as_view(), name='kolekti_home'),
    
    url(r'^accounts/profile/$', UserProfileView.as_view(), name='user_profile'),    
    url(r'^accounts/', include('allauth.urls')),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    
    url(r'^changelog/$', ChangelogView.as_view(), name='changelog'),
    url(r'^about/$', AboutView.as_view(), name='about'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),    
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog, name='javascript-catalog'),
    
    url(r'^staticdev/admin/(?P<path>.*)$', staticView, {'document_root' : '/usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin'}),    
    url(r'^staticdev/(?P<path>.*)$', staticView, {'document_root' : 'kserver/static'}),
    
    url(r'^translator/', include('translators.urls')),

    url(r'^(?P<project>[^/\?]+)/', include([
        url(r'^search/',include('search.urls')),
        url(r'^audit/',include('audit.urls')),
    ])),
    
    url(r'^(?P<project>[^/\?]+)/', include('kserver.urls')),
]
    
urlpatterns = urls

admin.autodiscover()

