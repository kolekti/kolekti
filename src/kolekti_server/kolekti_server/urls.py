from django.conf.urls import include, url

from kserver.views import *
from kserver_saas.views import *
from translators.views import *
# from translators.urls import *

from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import javascript_catalog

from django.views.static import serve as staticView

from django.contrib import admin

<<<<<<< HEAD
urls = [
    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/profile/$', UserProfileView.as_view(), name='user_profile'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),

    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),

        
#    url(r'^$', HomeView.as_view(), name='kolekti_home'),
    url(r'^$', HomeView.as_view(), name='kolekti_home'),

    url(r'^(?P<project>[^/\?]+)/', include([
        url(r'^$', ProjectHomeView.as_view(), name='kolekti_project_home'),
        
        
        url(r'^kolekti/', include([
            url(r'^settings/$', SettingsView.as_view(), name='kolekti_settings'),
            url(r'^settings.json$', SettingsJsonView.as_view(), name='kolekti_settings_json'),
            url(r'^settings.js$', SettingsJsView.as_view(), name='kolekti_settings_js'),
            url(r'^languages/$', ProjectLanguagesView.as_view(), name='kolekti_languages_edit'),
            url(r'^criteria/$', CriteriaEditView.as_view(), name='kolekti_criteria_edit'),
            url(r'^criteria.css$', CriteriaCssView.as_view(), name='kolekti_criteria_css'),
            url(r'^criteria.json$', CriteriaJsonView.as_view(), name='kolekti_criteria_json'),
            url(r'^publication-templates/$', PublicationTemplatesView.as_view(), name='kolekti_publication_templates'),
            url(r'^publication-parameters/', include([
                url(r'^/$', JobListView.as_view(), name='kolekti_jobs'),
                url(r'^create/', JobCreateView.as_view(), name='kolekti_job_create'),
                url(r'^(?P<job_path>.+)/edit/$', JobEditView.as_view(), name='kolekti_job_edit'),
            ])),
        ])),
=======
urlpatterns = [
#    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/profile/$', UserProfileView.as_view(), name="user_profile"),
#    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),
    url(r'^auth/', include('django.contrib.auth.urls')),

    url(r'^translator/', include('translators.urls')),
>>>>>>> 80fb374eaff5d3e99cb21f3ff85631908f1b4b9a

        
        url(r'^sources/(?P<lang>[^/\?]+)/', include([
            url(r'^tocs/', include([
                url(r'^$', TocsListView.as_view(), name='kolekti_tocs'),
                url(r'^(?P<toc_path>.+)/', include([
                    url(r'^edit$', TocEditView.as_view(), name='kolekti_toc_edit'),
                    url(r'^usecases$', TocUsecasesView.as_view(), name='kolekti_toc_usecases'),
                    url(r'^create$', TocCreateView.as_view(),name='kolekti_toc_create'),
                    url(r'^publish$', TocPublishView.as_view(),name='kolekti_toc_publish'),
                    url(r'^release$', TocReleaseView.as_view(),name='kolekti_publish_release'),
                    url(r'^$', TocsListView.as_view(), name='kolekti_tocs_browse'),        

                ])),
            ])),
                
            url(r'^topics/$', TopicsListView.as_view(), name='kolekti_topics'),
            url(r'^topics/templates/$', TopicTemplatesView.as_view(),name='kolekti_topic_templates'),
            url(r'^topics/(?P<topic_path>.+)/', include([
                url(r'^meta.json$', TopicMetaJsonView.as_view(),name='kolekti_topic_meta_json'),
                url(r'^edit$', TopicEditorView.as_view(),name='kolekti_topic_edit'),
                url(r'^create$', TopicCreateView.as_view(),name='kolekti_topic_create'),
                url(r'^$', TopicsListView.as_view(), name='kolekti_topics_browse'),        
            ])),
           
            url(r'^templates/$', TopicTemplateListView.as_view(),name='kolekti_templates'),
            
            url(r'^templates/(?P<template_path>.+)/', include([
                url(r'^edit/$', TemplateEditorView.as_view(),name='kolekti_topic_editor'),
                url(r'^create/$', TemplateCreateView.as_view(),name='kolekti_topic_create'),
            ])),
            
            url(r'^variables/', include([
                url(r'^$', VariablesListView.as_view(), name='kolekti_variables'),
                url(r'^(?P<variable_path>.+)/', include([
                    url(r'^create$', VariablesCreateView.as_view(), name='kolekti_variable_create'),
                    url(r'^upload$', VariablesUploadView.as_view(), name='kolekti_variable_upload'),
                    url(r'^detail$', VariablesDetailsView.as_view(), name='kolekti_variable_details'),
                    url(r'^editvar$', VariablesEditvarView.as_view(), name='kolekti_variable_editval'),
                    url(r'^editcol$', VariablesEditcolView.as_view(), name='kolekti_variable_editcol'),
                    url(r'^ods$', VariablesODSView.as_view(), name='kolekti_variable_ods'),
                    url(r'^$', VariablesListView.as_view(), name='kolekti_variables_browse'),
                ])),
            ])),
        
            url(r'^pictures/', include([
                url(r'^$', PicturesListView.as_view(), name='kolekti_pictures'),
                url(r'^upload$', PictureUploadView.as_view(), name='kolekti_picture_upload'),
                url(r'^(?P<picture_path>.+)/', include([
                    url(r'^details$', PictureDetailsView.as_view(), name='kolekti_picture_details'),
                    url(r'^$', PicturesListView.as_view(), name='kolekti_pictures_browse'),
                ])),
            ])),

            url(r'^import/$', ImportView.as_view(), name='kolekti_import'),
            url(r'^import/template/$', ImportTemplateView.as_view(), name='kolekti_import_template'),

        ])),    
            
            
        url(r'^publications.json$', PublicationsListJsonView.as_view(),name='kolekti_publications_list_json'),
        url(r'^publications/(?P<publication_path>.+)/zip/$', PublicationsZipView.as_view(),name='kolekti_publications_zip'),

        
        url(r'^releases/$', ReleaseListView.as_view(), name='kolekti_releases'),
        url(r'^releases/(?P<release>[^/\?]+)/', include([
            url(r'^states/$', ReleaseAllStatesView.as_view(), name='kolekti_release_states'),
            url(r'^(?P<lang>[^/\?]+)/', include([
                url(r'^detail/$', ReleaseDetailsView.as_view(), name='kolekti_release_detail'),
                url(r'^state/$', ReleaseStateView.as_view(), name='kolekti_release_state'),
                url(r'^focus/$', ReleaseFocusView.as_view(), name='kolekti_release_focus'),
                url(r'^copy/$', ReleaseCopyView.as_view(), name='kolekti_release_copy'),
                url(r'^delete/$', ReleaseDeleteView.as_view(), name='kolekti_release_delete'),
                url(r'^publish/$', ReleasePublishView.as_view(),name='kolekti_release_publish'),
                url(r'^validate/$', ReleaseValidateView.as_view(),name='kolekti_release_validate'),
                url(r'^assembly/$', ReleaseAssemblyView.as_view(),name='kolekti_release_assembly'),
                url(r'^publications/*', ReleasePublicationsView.as_view(),name='kolekti_release_publications'),
                url(r'^publications.json$', ReleasesPublicationsListJsonView.as_view(),name='kolekti_release_publications_list_json'),
            ])),
        ])),
        
        url(r'^api/', include([
            url(r'^sync/', include([        
                url(r'^$', SyncView.as_view(), name='kolekti_sync'),
                url(r'^diff$', SyncDiffView.as_view(), name='kolekti_sync_diff'),
                url(r'^status$', SyncStatusView.as_view(), name='kolekti_sync_status'),
                url(r'^remotestatus$', SyncRemoteStatusView.as_view(), name='kolekti_sync_remote_status'),
                url(r'^resstatus$', SyncResStatusView.as_view(), name='kolekti_sync_res_status'),
                url(r'^revision/(?P<rev>\d+)/$', SyncRevisionView.as_view(), name='kolekti_sync_revision'),
                url(r'^add$', SyncAddView.as_view(), name='kolekti_sync_add'),
                url(r'^remove$', SyncRemoveView.as_view(), name='kolekti_sync_remove'),
            ])),
            url(r'browse/', include([        
                url(r'^$', BrowserView.as_view(),name='kolekti_browser'),    
                url(r'^releases/$', BrowserReleasesView.as_view(),name='kolekti_browser_releases'),
                url(r'^exists/$', BrowserExistsView.as_view(),name='kolekti_browser_exists'),
                url(r'^mkdir/$', BrowserMkdirView.as_view(),name='kolekti_browser_mkdir'),
                url(r'^move/$', BrowserMoveView.as_view(),name='kolekti_browser_move'),
                url(r'^copy/$', BrowserCopyView.as_view(),name='kolekti_browser_copy'),
                url(r'^delete/$', BrowserDeleteView.as_view(),name='kolekti_browser_delete'),
                url(r'^ckbrowser/$', BrowserCKView.as_view(),name='kolekti_ckbrowser'),
                url(r'^ckupload/$', BrowserCKUploadView.as_view(),name='kolekti_ckupload'),
                url(r'^upload/$', BrowserUploadView.as_view(), name='kolekti_browser_upload'),
            ])),
            url(r'^widgets/', include([        
                url(r'^project-history/$', WidgetProjectHistoryView.as_view(), name='kolekti_widget_project_history'),
                url(r'^publications/$', WidgetPublicationsListView.as_view(), name='kolekti_widget_publication_list'),
                url(r'^releasepublications/$', WidgetReleasePublicationsListView.as_view(), name='kolekti_widget_release_publications_list')
            ])),
            url(r'^history/$', ProjectHistoryView.as_view(), name='kolekti_project_history'),
        ])),

        url(r'^search/$', SearchView.as_view(),name='kolekti_search'),
        ]))
    ]
    
    
<<<<<<< HEAD
if os.sys.platform[:3] == 'win':
    urls.extend([
        url(r'^projects/$', ProjectsView.as_view(), name='kolekti_projects'),    
        url(r'^projects/activate$', ProjectsActivateView.as_view(), name='kolekti_projects_activate'),
        url(r'^projects/language$', ProjectsLanguageView.as_view(), name='kolekti_projects_language'),
#        url(r'^projects/config$', ProjectsConfigView.as_view(), name='kolekti_projects_config'),
        url(r'^projects/new$', ProjectsView.as_view(), name='kolekti_projects_new'),
        ])
else:
    # Saas
    urls.extend([
        url(r'^projects/$', SaasProjectsView.as_view(), name='kolekti_projects'),    
        url(r'^projects/activate$', SaasProjectsActivateView.as_view(), name='kolekti_projects_activate'),
        url(r'^projects/language$', SaasProjectsLanguageView.as_view(), name='kolekti_projects_language'),
#        url(r'^projects/config$', ProjectsConfigView.as_view(), name='kolekti_projects_config'),
        url(r'^projects/new$', SaasProjectsView.as_view(), name='kolekti_projects_new'),    
        ])

urls.extend([

    url(r'^admin/', include(admin.site.urls)),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),
    url(r'^(?P<project>[^/\?]+)/(?P<path>.*)$', ProjectStaticView.as_view(), name='kolekti_project_static'),
    
    #url(r'^static/(?P<path>.*)$', staticView, {'document_root' : settings.STATIC_PATH}),
=======
    url(r'^variables/$', VariablesListView.as_view(), name='variablelist'),
    url(r'^variables/upload$', VariablesUploadView.as_view(), name='variableupload'),
    url(r'^variables/create/$', VariablesCreateView.as_view(), name='variablecreate'),
    url(r'^variables/detail/$', VariablesDetailsView.as_view(), name='variabledetails'),
    url(r'^variables/editvar/$', VariablesEditvarView.as_view(), name='variableeditval'),
    url(r'^variables/editcol/$', VariablesEditcolView.as_view(), name='variableeditcol'),
    url(r'^variables/ods$', VariablesODSView.as_view(), name='variableods'),

    url(r'^images/$', ImagesListView.as_view(), name='imagelist'),
    url(r'^images/upload$', ImagesUploadView.as_view(), name='imageupload'),
    url(r'^images/details$', ImagesDetailsView.as_view(), name='imagedetails'),

    url(r'^sync/$', SyncView.as_view(), name='sync'),
    url(r'^sync/diff$', SyncDiffView.as_view(), name='syncdiff'),
    url(r'^sync/status$', SyncStatusView.as_view(), name='syncstatus'),
    url(r'^sync/remotestatus$', SyncRemoteStatusView.as_view(), name='syncremotestatus'),
    url(r'^sync/resstatus$', SyncResStatusView.as_view(), name='syncresstatus'),
    url(r'^sync/revision/(?P<rev>\d+)/$', SyncRevisionView.as_view(), name='syncrev'),
    url(r'^sync/add$', SyncAddView.as_view(), name='syncadd'),
    url(r'^sync/remove$', SyncRemoveView.as_view(), name='syncremove'),
]

if os.sys.platform[:3] == "win":
    urlpatterns.extend([
        url(r'^projects/$', ProjectsView.as_view(), name='projects'),    
        url(r'^projects/activate$', ProjectsActivateView.as_view(), name='projects_activate'),
        url(r'^projects/language$', ProjectsLanguageView.as_view(), name='projects_language'),
        url(r'^projects/config$', ProjectsConfigView.as_view(), name='projects_config'),
        url(r'^projects/new$', ProjectsView.as_view(), name='projects_new'),
        ])
else:
    # Saas
    urlpatterns.extend([
        url(r'^projects/$', SaasProjectsView.as_view(), name='projects'),    
        url(r'^projects/activate$', SaasProjectsActivateView.as_view(), name='projects_activate'),
        url(r'^projects/language$', SaasProjectsLanguageView.as_view(), name='projects_language'),
        url(r'^projects/config$', ProjectsConfigView.as_view(), name='projects_config'),
        url(r'^projects/new$', SaasProjectsView.as_view(), name='projects_new'),    
        ])

urlpatterns.extend([
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^settings.json$', SettingsJsonView.as_view(), name='settings_json'),
    url(r'^settings.js$', SettingsJsView.as_view(), name='settings_js'),
    url(r'^settings/job$', JobEditView.as_view(), name='jobedit'),
    url(r'^settings/jobs/create/', JobCreateView.as_view(), name='jobcreate'),
    url(r'^settings/criteria$', CriteriaEditView.as_view(), name='criteriaedit'),
    url(r'^criteria/$', CriteriaView.as_view(), name='criteria'),
    url(r'^criteria.css$', CriteriaCssView.as_view(), name='criteriacss'),
    url(r'^criteria.json$', CriteriaJsonView.as_view(), name='criteriacss'),

    url(r'^publication-templates/$', PublicationTemplatesView.as_view(), name='publication_templates'),
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
    
    url(r'^templates/$', TopicTemplateListView.as_view(),name="templatelist"),
    
    url(r'^topics/meta.json', TopicMetaJsonView.as_view(),name="topic_meta_json"),

    url(r'^publications/list.json', PublicationsListJsonView.as_view(),name="publications_list_json"),
    url(r'^publications/zip/$', PublicationsZipView.as_view(),name="publications_zip"),
    url(r'^releases/publications/list.json', ReleasesPublicationsListJsonView.as_view(),name="releases_publications_list_json"),


    url(r'^search', SearchView.as_view(),name="kolekti_search"),

    url(r'^admin/', include(admin.site.urls)),
])
    
if settings.DEBUG:
    from django.contrib.staticfiles import views
    urlpatterns.extend([
        url(r'^staticdev/(?P<path>.*)$', views.serve),
    ])
    
urlpatterns.extend([
    url(r'^staticdev/(?P<path>.*)$', staticView, {'document_root' : settings.STATIC_PATH}),
    url(r'(?P<path>.*)$', projectStaticView.as_view(), name="project_static"),
>>>>>>> 80fb374eaff5d3e99cb21f3ff85631908f1b4b9a
])
    
#    url(r'^publications', staticView, name='kolekti_raw_publication'),
#    url(r'^drafts', staticView, name='kolekti_raw_draft'),


<<<<<<< HEAD
urlpatterns = patterns('', *urls) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

=======
>>>>>>> 80fb374eaff5d3e99cb21f3ff85631908f1b4b9a

admin.autodiscover()
