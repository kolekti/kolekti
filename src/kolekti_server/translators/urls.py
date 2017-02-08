from django.conf.urls import patterns, include, url
from views import *
from django.contrib import admin
admin.autodiscover()

urls = [
    url(r'^$', TranslatorsHomeView.as_view(), name='translators_home'),
]
urlpatterns = patterns('', *urls)
