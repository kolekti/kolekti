from django.conf.urls import patterns, include, url

from kserver.views import *
from kserver.saas_views import *
from kserver.views_ecorse import *

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as staticView

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',


    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/profile/$', UserProfileView.as_view(), name="user_profile"),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),


                       

    # ECOres specific wiews
    # url(r'^$', ElocusHomeView.as_view(), name='elocushome'),
    url(r'^elocus/$', ElocusReportView.as_view(), name='home'),
    
    url(r'^elocus/report/$', ElocusReportShareView.as_view(), name='elocusreport'),
    url(r'^elocus/report/create$', ElocusReportCreateView.as_view(), name='elocusreportcreate'),
    url(r'^elocus/report/publish$', ElocusReportPublishView.as_view(), name='elocusreportpublish'),
    url(r'^elocus/report/update$', ElocusReportUpdateView.as_view(), name='elocusreportupdate'),
    url(r'^elocus/topic/save$', ElocusTopicSaveView.as_view(), name='elocustopicsave'),
    url(r'^elocus/report/analysis$', ElocusReportAnalysisView.as_view(), name='elocusreportanalysis'),
    url(r'^elocus/report/star$', ElocusReportStarView.as_view(), name='elocusreportstar'),
    url(r'^elocus/report/hide$', ElocusReportHideView.as_view(), name='elocusreporthide'),
    url(r'^elocus/report/chart$', ElocusReportChartView.as_view(), name='elocusreportchart'),
    url(r'^elocus/refparameters$', ElocusRefParametersView.as_view(), name='elocusrefparameters'),

    url(r'^elocus/communes$', ElocusCommunesView.as_view(), name='elocuscommunes'),
    url(r'^elocus/referentiels$', ElocusReferentielsView.as_view(), name='elocusreferentiels'),
    
    url(r'^$', HomeView.as_view(), name='root'),
    url(r'^kolekti/$', KolektiView.as_view(), name='kolekti'),
    url(r'^widgets/project-history/$', WidgetProjectHistoryView.as_view(), name='WidgetProjectHistory'),
    url(r'^widgets/publications/$', WidgetPublicationsListView.as_view(), name='WidgetPublicationsList'),
    url(r'^widgets/releasepublications/$', WidgetReleasePublicationsListView.as_view(), name='WidgetReleasePublicationsList'),
    url(r'^project/history/$', ProjectHistoryView.as_view(), name='projecthistory'),
    
    url(r'^tocs/$', TocsListView.as_view(), name='toclist'),
    url(r'^tocs/edit/$', TocView.as_view(), name='tocedit'),
    url(r'^tocs/usecases/$', TocUsecasesView.as_view(), name='tocusecases'),
    url(r'^tocs/create/$', TocCreateView.as_view(),name="toc_create"),

    url(r'^projects/$', SaasProjectsView.as_view(), name='projects'),
    url(r'^projects/new/$', SaasProjectsView.as_view(), name='projects_new'),
    url(r'^projects/config$', ProjectsConfigView.as_view(), name='projects_config'),    
    url(r'^projects/activate$', ProjectsActivateView.as_view(), name='projects_activate'),
    url(r'^projects/language$', ProjectsLanguageView.as_view(), name='projects_language'),    

    url(r'^import/$', ImportView.as_view(), name='import'),
    url(r'^import/template/$', ImportTemplateView.as_view(), name='importtemplate'),

    url(r'^releases/$', ReleaseListView.as_view(), name='releaselist'),
    url(r'^releases/detail/$', ReleaseDetailsView.as_view(), name='releasedetail'),
    url(r'^releases/state/', ReleaseStateView.as_view(), name='releasestate'),
    url(r'^releases/focus/', ReleaseFocusView.as_view(), name='releasefocus'),
    url(r'^releases/copy/', ReleaseCopyView.as_view(), name='releasecopy'),
    url(r'^releases/publish', ReleasePublishView.as_view(),name="releasepublish"),
    url(r'^releases/validate', ReleaseValidateView.as_view(),name="releasevalidate"),
    url(r'^releases/assembly', ReleaseAssemblyView.as_view(),name="releaseassembly"),
    url(r'^releases/publications', ReleasePublicationsView.as_view(),name="releasepublications"),
    
    url(r'^variables/$', VariablesListView.as_view(), name='variablelist'),
    url(r'^variables/upload$', VariablesUploadView.as_view(), name='variableupload'),
    url(r'^variables/detail/$', VariablesDetailsView.as_view(), name='variabledetails'),
    url(r'^variables/ods$', VariablesODSView.as_view(), name='variableods'),

    url(r'^images/$', ImagesListView.as_view(), name='imagelist'),
    url(r'^images/upload$', ImagesUploadView.as_view(), name='imageupload'),
    url(r'^images/details$', ImagesDetailsView.as_view(), name='imagedetails'),

    url(r'^sync/$', SyncView.as_view(), name='sync'),
    url(r'^sync/diff$', SyncDiffView.as_view(), name='syncdiff'),
    url(r'^sync/status$', SyncStatusView.as_view(), name='syncstatus'),
    url(r'^sync/resstatus$', SyncResStatusView.as_view(), name='syncresstatus'),
    url(r'^sync/revision/(?P<rev>\d+)/$', SyncRevisionView.as_view(), name='syncrev'),
    url(r'^sync/add$', SyncAddView.as_view(), name='syncadd'),
    url(r'^sync/remove$', SyncRemoveView.as_view(), name='syncremove'),
    
#    url(r'^projects/$', ProjectsView.as_view(), name='projects'),    
#    url(r'^projects/activate$', ProjectsActivateView.as_view(), name='projects_activate'),
#    url(r'^projects/language$', ProjectsLanguageView.as_view(), name='projects_language'),
#    url(r'^projects/config$', ProjectsConfigView.as_view(), name='projects_config'),    

    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^settings.json$', SettingsJsonView.as_view(), name='settings_json'),
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
    url(r'^browse/upload$', BrowserUploadView.as_view(), name='kolekti_browser_upload'),
    url(r'^browse/releases/', BrowserReleasesView.as_view(),name="kolekti_browser_releases"),
    url(r'^browse', BrowserView.as_view(),name="kolekti_browser"),

    
    url(r'^publish/draft/', DraftView.as_view(),name="publish_draft"),
    url(r'^publish/release/', ReleaseView.as_view(),name="publish_release"),

    url(r'^topics/$', TopicsListView.as_view(), name='topiclist'),
    url(r'^topics/templates/', TopicTemplatesView.as_view(),name="topic_templates"),
    url(r'^topics/edit/', TopicEditorView.as_view(),name="topic_editor"),
    url(r'^topics/create/', TopicCreateView.as_view(),name="topic_create"),

    url(r'^topics/meta.json', TopicMetaJsonView.as_view(),name="topic_meta_json"),

    url(r'^publications/list.json', PublicationsListJsonView.as_view(),name="publications_list_json"),
    url(r'^publications/zip/$', PublicationsZipView.as_view(),name="publications_zip"),
    url(r'^releases/publications/list.json', ReleasesPublicationsListJsonView.as_view(),name="releases_publications_list_json"),


    url(r'^search', SearchView.as_view(),name="kolekti_search"),

    url(r'^static/(?P<path>.*)$', staticView, {'document_root' : 'kolekti_server/kserver/static/'}),
    url(r'^admin/', include(admin.site.urls)),

    url(r'(?P<path>.*)$', projectStaticView.as_view(), name="project_static"),

#    url(r'^publications', staticView, name="kolekti_raw_publication"),
#    url(r'^drafts', staticView, name="kolekti_raw_draft"),

                       

)


