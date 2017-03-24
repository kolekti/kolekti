from django.conf.urls import patterns, include, url

from kserver.views import *
from kserver_saas.views import *

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as staticView

from django.contrib import admin
admin.autodiscover()

urls = [
    url(r'^accounts/register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/profile/$', UserProfileView.as_view(), name='user_profile'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^auth/', include('django.contrib.auth.urls')),



        
#    url(r'^$', HomeView.as_view(), name='kolekti_home'),
    url(r'^$', HomeView.as_view(), name='kolekti_home'),

    url(r'^(?P<project>[^/\?]+)/', include([
        url(r'^$', ProjectHomeView.as_view(), name='kolekti_project_home'),

        url(r'^widgets/project-history/$', WidgetProjectHistoryView.as_view(), name='kolekti_widget_project_history'),
        url(r'^widgets/publications/$', WidgetPublicationsListView.as_view(), name='kolekti_widget_publication_list'),
        url(r'^widgets/releasepublications/$', WidgetReleasePublicationsListView.as_view(), name='kolekti_widget_release_publications_list'),
        url(r'^history/$', ProjectHistoryView.as_view(), name='kolekti_project_history'),

        
        
        url(r'^kolekti/', include([
            url(r'^settings/$', SettingsView.as_view(), name='kolekti_settings'),
            url(r'^settings.json$', SettingsJsonView.as_view(), name='kolekti_settings_json'),
            url(r'^settings.js$', SettingsJsView.as_view(), name='kolekti_settings_js'),
            url(r'^languages/$', LanguagesView.as_view(), name='kolekti_languages_edit'),
            url(r'^criteria/$', CriteriaEditView.as_view(), name='kolekti_criteria_edit'),
            url(r'^criteria.css$', CriteriaCssView.as_view(), name='kolekti_criteria_css'),
            url(r'^criteria.json$', CriteriaJsonView.as_view(), name='kolekti_criteria_json'),
            url(r'^publication-templates/$', PublicationTemplatesView.as_view(), name='kolekti_publication_templates'),
            url(r'^publication-parameters/', include([
                url(r'^/$', JobListView.as_view(), name='kolekti_job_list'),
                url(r'^create/', JobCreateView.as_view(), name='kolekti_job_create'),
                url(r'^(?P<job_path>.+)/edit/$', JobEditView.as_view(), name='kolekti_job_edit'),
            ])),
        ])),

        
        url(r'^sources/(?P<lang>[^/\?]+)/', include([
            url(r'^tocs/', include([
                url(r'^$', TocsListView.as_view(), name='kolekti_tocs'),
                url(r'^(?P<toc_path>.+)/', include([
                    url(r'^edit/$', TocEditView.as_view(), name='kolekti_toc_edit'),
                    url(r'^usecases/$', TocUsecasesView.as_view(), name='kolekti_toc_usecases'),
                    url(r'^create/$', TocCreateView.as_view(),name='kolekti_toc_create'),
                    url(r'^publish/$', DraftView.as_view(),name='kolekti_toc_publish'),
                ])),
            ])),
                
            url(r'^topics/$', TopicsListView.as_view(), name='kolekti_topics'),
            url(r'^topics/templates/$', TopicTemplatesView.as_view(),name='kolekti_topic_templates'),
            url(r'^topics/(?P<topic_path>.+)/', include([
                url(r'^meta.json$', TopicMetaJsonView.as_view(),name='kolekti_topic_meta_json'),
                url(r'^edit/$', TopicEditorView.as_view(),name='kolekti_topic_editor'),
                url(r'^create/$', TopicCreateView.as_view(),name='kolekti_topic_create'),
            ])),
           
            url(r'^templates/$', TopicTemplateListView.as_view(),name='kolekti_templates'),
            
            url(r'^templates/(?P<template_path>.+)/', include([
                url(r'^edit/$', TemplateEditorView.as_view(),name='kolekti_topic_editor'),
                url(r'^create/$', TemplateCreateView.as_view(),name='kolekti_topic_create'),
            ])),
            url(r'^variables/', include([
                url(r'^$', VariablesListView.as_view(), name='kolekti_variables'),
                url(r'^create/$', VariablesCreateView.as_view(), name='kolekti_variable_create'),
                url(r'^(?P<variable_path>.+)/upload/$', VariablesUploadView.as_view(), name='kolekti_variable_upload'),
                url(r'^(?P<variable_path>.+)/detail/$', VariablesDetailsView.as_view(), name='kolekti_variable_details'),
                url(r'^(?P<variable_path>.+)/editvar/$', VariablesEditvarView.as_view(), name='kolekti_variable_editval'),
                url(r'^(?P<variable_path>.+)/editcol/$', VariablesEditcolView.as_view(), name='kolekti_variable_editcol'),
                url(r'^(?P<variable_path>.+)/ods$', VariablesODSView.as_view(), name='kolekti_variable_ods'),
            ])),
        
            url(r'^images/', include([
                url(r'^$', PicturesListView.as_view(), name='kolekti_pictures'),
                url(r'^upload$', PictureUploadView.as_view(), name='kolekti_picture_upload'),
                url(r'^(?P<picture_path>.+)/detail$', PictureDetailsView.as_view(), name='kolekti_picture_details'),
            ])),    
        ])),    
            
            
        url(r'^publications.json$', PublicationsListJsonView.as_view(),name='kolekti_publications_list_json'),
        url(r'^publications/(?P<publication_path>.+)/zip/$', PublicationsZipView.as_view(),name='kolekti_publications_zip'),

        url(r'^import/$', ImportView.as_view(), name='kolekti_import'),
        url(r'^import/template/$', ImportTemplateView.as_view(), name='kolekti_import_template'),
        
        url(r'^releases/$', ReleaseListView.as_view(), name='kolekti_releases'),
        url(r'^releases/(?P<release>[^/\?]+)/', include([
            url(r'^detail/$', ReleaseDetailsView.as_view(), name='kolekti_release_detail'),
            url(r'^state/$', ReleaseStateView.as_view(), name='kolekti_release_state'),
            url(r'^states/$', ReleaseAllStatesView.as_view(), name='kolekti_release_states'),
            url(r'^focus/$', ReleaseFocusView.as_view(), name='kolekti_release_focus'),
            url(r'^copy/$', ReleaseCopyView.as_view(), name='kolekti_release_copy'),
            url(r'^delete/$', ReleaseDeleteView.as_view(), name='kolekti_release_delete'),
            url(r'^publish/$', ReleasePublishView.as_view(),name='kolekti_release_publish'),
            url(r'^validate/$', ReleaseValidateView.as_view(),name='kolekti_release_validate'),
            url(r'^assembly/$', ReleaseAssemblyView.as_view(),name='kolekti_release_assembly'),
            url(r'^publications/*', ReleasePublicationsView.as_view(),name='kolekti_release_publications'),
            url(r'^publications.json$', ReleasesPublicationsListJsonView.as_view(),name='kolekti_release_publications_list_json'),
        ])),
        
        url(r'^api/', include([
            url(r'^sync/', include([        
                url(r'^$', SyncView.as_view(), name='kolekti_sync'),
                url(r'^diff$', SyncDiffView.as_view(), name='kolekti_syncdiff'),
                url(r'^status$', SyncStatusView.as_view(), name='kolekti_syncstatus'),
                url(r'^remotestatus$', SyncRemoteStatusView.as_view(), name='kolekti_syncremotestatus'),
                url(r'^resstatus$', SyncResStatusView.as_view(), name='kolekti_syncresstatus'),
                url(r'^revision/(?P<rev>\d+)/$', SyncRevisionView.as_view(), name='kolekti_syncrev'),
                url(r'^add$', SyncAddView.as_view(), name='kolekti_syncadd'),
                url(r'^remove$', SyncRemoveView.as_view(), name='kolekti_syncremove'),
            ])),
            url(r'^browse/', include([        
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
        ])),

    # url(r'^blog/', include('blog.urls')),


        
        

        url(r'^publish/release/$', ReleaseView.as_view(),name='kolekti_publish_release'),
        

        url(r'^search/$', SearchView.as_view(),name='kolekti_search'),
        url(r'(?P<path>.*)$', projectStaticView.as_view(), name='kolekti_project_static'),
        ]))
    ]
    
    
if os.sys.platform[:3] == 'win':
    urls.extend([
        url(r'^projects/$', ProjectsView.as_view(), name='kolekti_projects'),    
        url(r'^projects/activate$', ProjectsActivateView.as_view(), name='kolekti_projects_activate'),
        url(r'^projects/language$', ProjectsLanguageView.as_view(), name='kolekti_projects_language'),
        url(r'^projects/config$', ProjectsConfigView.as_view(), name='kolekti_projects_config'),
        url(r'^projects/new$', ProjectsView.as_view(), name='kolekti_projects_new'),
        ])
else:
    # Saas
    urls.extend([
        url(r'^projects/$', SaasProjectsView.as_view(), name='kolekti_projects'),    
        url(r'^projects/activate$', SaasProjectsActivateView.as_view(), name='kolekti_projects_activate'),
        url(r'^projects/language$', SaasProjectsLanguageView.as_view(), name='kolekti_projects_language'),
        url(r'^projects/config$', ProjectsConfigView.as_view(), name='kolekti_projects_config'),
        url(r'^projects/new$', SaasProjectsView.as_view(), name='kolekti_projects_new'),    
        ])

urls.extend([

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^static/(?P<path>.*)$', staticView, {'document_root' : settings.STATIC_PATH}),
])
    
#    url(r'^publications', staticView, name='kolekti_raw_publication'),
#    url(r'^drafts', staticView, name='kolekti_raw_draft'),


urlpatterns = patterns('', *urls)


