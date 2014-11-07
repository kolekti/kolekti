from django.conf.urls import patterns, include, url
from kserver.views import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^tocs/$', TocsListView.as_view(), name='toclist'),
    url(r'^tocs/edit/$', TocView.as_view(), name='tocedit'),
    url(r'^tocs/usecases/$', TocUsecasesView.as_view(), name='tocusecases'),
    url(r'^import/$', ImportView.as_view(), name='import'),
    url(r'^tranlations/$', TranslationsListView.as_view(), name='translationlist'),
    url(r'^topics/$', TopicsListView.as_view(), name='topiclist'),
    url(r'^images/$', ImagesListView.as_view(), name='imagelist'),
    url(r'^sync/$', SyncView.as_view(), name='sync'),
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^settings/job$', JobEditView.as_view(), name='jobedit'),
    url(r'^settings/criteria$', CriteriaEditView.as_view(), name='criteriaedit'),
    url(r'^criteria/$', CriteriaView.as_view(), name='criteria'),

# url(r'^blog/', include('blog.urls')),

    url(r'^browse/', BrowserView.as_view(),name="kolekti_browser"),

    url(r'^publish/draft/', DraftView.as_view(),name="publish_draft"),
    url(r'^publish/release/', ReleaseView.as_view(),name="publish_release"),

    url(r'^topics/edit/', TopicEditorView.as_view(),name="topic_editor"),

#    (r'^admin/', include(admin.site.urls)),
)
