from django.conf.urls import patterns, include, url
from views import *

urls = [
    url(r'^$', TranslatorsHomeView.as_view(), name='translators_home'),
]
urlpatterns = patterns('', *urls)
