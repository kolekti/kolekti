from django.conf.urls import patterns, include, url
from kserver.views import *
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as staticView

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^tocs/$', TocsListView.as_view(), name='toclist'),
    url(r'^tocs/edit/$', TocView.as_view(), name='tocedit'),
    url(r'^tocs/usecases/$', TocUsecasesView.as_view(), name='tocusecases'),
    url(r'^tocs/create/$', TocCreateView.as_view(),name="toc_create"),

    url(r'^import/$', ImportView.as_view(), name='import'),
    url(r'^releases/$', ReleaseListView.as_view(), name='releaselist'),
    url(r'^releases/detail/$', ReleaseDetailsView.as_view(), name='releasedetail'),
    url(r'^topics/$', TopicsListView.as_view(), name='topiclist'),

    url(r'^variables/$', VariablesListView.as_view(), name='variablelist'),
    url(r'^variables/upload$', VariablesUploadView.as_view(), name='variableupload'),
    url(r'^variables/details$', VariablesDetailsView.as_view(), name='variabledetails'),
    url(r'^variables/ods$', VariablesODSView.as_view(), name='variableods'),

    url(r'^images/$', ImagesListView.as_view(), name='imagelist'),
    url(r'^images/upload$', ImagesUploadView.as_view(), name='imageupload'),
    url(r'^images/details$', ImagesDetailsView.as_view(), name='imagedetails'),

    url(r'^sync/$', SyncView.as_view(), name='sync'),
    url(r'^sync/diff$', SyncDiffView.as_view(), name='syncdiff'),
    url(r'^sync/revision/(?P<rev>\d+)/$', SyncRevisionView.as_view(), name='syncrev'),

    url(r'^projects/$', ProjectsView.as_view(), name='projects'),    
    url(r'^projects/activate$', ProjectsActivateView.as_view(), name='projects_activate'),
    url(r'^projects/language$', ProjectsLanguageView.as_view(), name='projects_language'),    

    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^settings.js$', SettingsJsView.as_view(), name='settings_js'),
    url(r'^settings/job$', JobEditView.as_view(), name='jobedit'),
    url(r'^settings/jobs/create/', JobCreateView.as_view(), name='jobcreate'),
    url(r'^settings/criteria$', CriteriaEditView.as_view(), name='criteriaedit'),
    url(r'^criteria/$', CriteriaView.as_view(), name='criteria'),
    url(r'^criteria.css$', CriteriaCssView.as_view(), name='criteriacss'),
    url(r'^criteria.json$', CriteriaJsonView.as_view(), name='criteriacss'),

# url(r'^blog/', include('blog.urls')),

    url(r'^browse/exists$', BrowserExistsView.as_view(),name="kolekti_browser_exists"),
    url(r'^browse/mkdir$', BrowserMkdirView.as_view(),name="kolekti_browser_mkdir"),
    url(r'^browse/move$', BrowserMoveView.as_view(),name="kolekti_browser_move"),
    url(r'^browse/copy$', BrowserCopyView.as_view(),name="kolekti_browser_copy"),
    url(r'^browse/delete$', BrowserDeleteView.as_view(),name="kolekti_browser_delete"),
    url(r'^browse/ckbrowser$', BrowserCKView.as_view(),name="kolekti_ckbrowser"),
    url(r'^browse/ckupload$', BrowserCKUploadView.as_view(),name="kolekti_ckupload"),
    url(r'^browse', BrowserView.as_view(),name="kolekti_browser"),

    
    url(r'^publish/draft/', DraftView.as_view(),name="publish_draft"),
    url(r'^publish/release/', ReleaseView.as_view(),name="publish_release"),

    url(r'^topics/templates/', TopicTemplatesView.as_view(),name="topic_templates"),
    url(r'^topics/edit/', TopicEditorView.as_view(),name="topic_editor"),
    url(r'^topics/create/', TopicCreateView.as_view(),name="topic_create"),


    url(r'^search', SearchView.as_view(),name="kolekti_search"),

    url(r'^static/(?P<path>.*)$', staticView, {'document_root' : 'kolekti_server/kserver/static/'}),
    url(r'(?P<path>.*)$', projectStaticView.as_view(), name="project_static"),

#    url(r'^publications', staticView, name="kolekti_raw_publication"),
#    url(r'^drafts', staticView, name="kolekti_raw_draft"),

                       
#    (r'^admin/', include(admin.site.urls)),
)

