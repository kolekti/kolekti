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
from django_js_reverse.views import urls_js

urls = [
    url(r'^accounts/profile/$', UserProfileView.as_view(), name='user_profile'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),
    url(r'^auth/', include('django.contrib.auth.urls')),
    
    url(r'^jsreverse/$', urls_js, name='js_reverse'),

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
            url(r'^publication-templates/', include([
                url(r'^$', PublicationTemplatesView.as_view(), name='kolekti_publication_templates'),
                url(r'^(?P<pt_path>.+)/$', PublicationTemplatesView.as_view(), name='kolekti_publication_templates'),
            ])),
#            .as_view(), name='kolekti_publication_templates'),
            url(r'^publication-parameters/', include([
                url(r'^$', JobListView.as_view(), name='kolekti_jobs'),
                url(r'^create/', JobCreateView.as_view(), name='kolekti_job_create'),
                url(r'^(?P<job_path>.+)/edit/$', JobEditView.as_view(), name='kolekti_job_edit'),
                url(r'^(?P<job_path>.+)/$', JobListView.as_view(), name='kolekti_jobs_path'),                
            ])),
        ])),

        
        url(r'^sources/(?P<lang>[^/\?]+)/', include([
            url(r'^tocs/', include([
                url(r'^$', TocsListView.as_view(), name='kolekti_tocs'),
                url(r'^(?P<toc_path>.+)/', include([
                    url(r'^edit$', TocEditView.as_view(), name='kolekti_toc_edit'),
                    url(r'^usecases$', TocUsecasesView.as_view(), name='kolekti_toc_usecases'),
                    url(r'^create$', TocCreateView.as_view(),name='kolekti_toc_create'),
                    url(r'^publish$', TocPublishView.as_view(),name='kolekti_toc_publish'),
                    url(r'^release$', TocReleaseView.as_view(),name='kolekti_toc_release'),
                    url(r'^$', TocsListView.as_view(), name='kolekti_tocs_browse'),        

                ])),
            ])),
                
            url(r'^topics/$', TopicsListView.as_view(), name='kolekti_topics'),
            url(r'^topics/templates/$', TopicTemplatesView.as_view(),name='kolekti_topic_templates'),
            url(r'^topics/templates/(?P<topic_template_path>.+)/', TopicTemplatesView.as_view(),name='kolekti_topic_templates_path'),
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
    
    
urls.extend([

    url(r'^admin/', include(admin.site.urls)),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog, name='javascript-catalog'),
    url(r'^staticdev/(?P<path>.*)$', staticView, {'document_root' : settings.STATIC_PATH}),
    url(r'^(?P<project>[^/\?]+)/(?P<path>.*)$', ProjectStaticView.as_view(), name='kolekti_project_static'),
])
    
#    url(r'^publications', staticView, name='kolekti_raw_publication'),
#    url(r'^drafts', staticView, name='kolekti_raw_draft'),


urlpatterns = urls + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.autodiscover()
