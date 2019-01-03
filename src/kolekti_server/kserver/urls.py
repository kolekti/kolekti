from django.conf.urls import include, url
from views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
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
            
            url(r'^topics/(?P<topic_path>.+)/', include([
                url(r'^meta.json$', TopicMetaJsonView.as_view(),name='kolekti_topic_meta_json'),
                url(r'^edit$', TopicEditorView.as_view(),name='kolekti_topic_edit'),
                url(r'^tocview$', TopicTocView.as_view(),name='kolekti_topic_tocview'),
                url(r'^create$', TopicCreateView.as_view(),name='kolekti_topic_create'),
                url(r'^$', TopicsListView.as_view(), name='kolekti_topics_browse'),        
            ])),
           
            url(r'^templates/$', TopicTemplateListView.as_view(),name='kolekti_templates'),
            url(r'^templates/json/$', TopicTemplatesView.as_view(),name='kolekti_templates_json'),
            
            url(r'^templates/(?P<template_path>.+)/', include([
                url(r'^edit$', TopicTemplateEditorView.as_view(),name='kolekti_topic_template_edit'),
                url(r'^create$', TopicTemplateCreateView.as_view(),name='kolekti_topic_template_create'),
            ])),
            
            url(r'^variables/', include([
                url(r'^$', VariablesListView.as_view(), name='kolekti_variables'),
                url(r'^(?P<variable_path>.+)/', include([                    
                    url(r'^create$', VariablesCreateView.as_view(), name='kolekti_variable_create'),
                    url(r'^upload$', VariablesUploadView.as_view(), name='kolekti_variable_upload'),
                    url(r'^editvar$', VariablesEditvarView.as_view(), name='kolekti_variable_editval'),
                    url(r'^editcol$', VariablesEditcolView.as_view(), name='kolekti_variable_editcol'),
                    url(r'^ods$', VariablesODSView.as_view(), name='kolekti_variable_ods'),
                    url(r'^$', VariablesDetailsView.as_view(), name='kolekti_variable'),
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

        ])), # sources
        
        url(r'^releases/$', ReleaseListView.as_view(), name='kolekti_releases'),
        url(r'^releases/archive$', ReleaseArchiveView.as_view(),name="kolekti_release_archive_form"),
        url(r'^releases/(?P<release>[^/\?]+)/', include([
            url(r'^publish/$', ReleasePublishView.as_view(),name='kolekti_release_publish'),
            url(r'^archive', ReleaseArchiveView.as_view(),name="kolekti_release_archive"),
            url(r'^states/$', ReleaseStatesView.as_view(), name='kolekti_release_states'),
            url(r'^delete/$', ReleaseDeleteView.as_view(), name='kolekti_release_delete'),
            url(r'^update/$', ReleaseUpdateView.as_view(), name='kolekti_release_update'),
            url(r'^rename/$', ReleaseRenameView.as_view(), name='kolekti_release_rename'),
            url(r'^sources/(?P<lang>[^/\?]+)/', include([
                url(r'^$', ReleaseLangDetailsView.as_view(), name='kolekti_release_lang_detail'),
                url(r'^state/$', ReleaseLangStateView.as_view(), name='kolekti_release_lang_state'),
                url(r'^focus/$', ReleaseLangFocusView.as_view(), name='kolekti_release_lang_focus'),
                url(r'^copy/$', ReleaseLangCopyView.as_view(), name='kolekti_release_lang_copy'),
                url(r'^delete/$', ReleaseLangDeleteView.as_view(), name='kolekti_release_lang_delete'),
                url(r'^publish/$', ReleaseLangPublishView.as_view(),name='kolekti_release_lang_publish'),
                url(r'^validate/$', ReleaseLangValidateView.as_view(),name='kolekti_release_lang_validate'),
                url(r'^assembly/$', ReleaseLangAssemblyView.as_view(),name='kolekti_release_lang_assembly'),
                url(r'^variables/', include([
                    url(r'^(?P<variable_path>.+)/', include([                    
                        url(r'^edit$', VariablesDetailsView.as_view(), name='kolekti_release_lang_variable'),
                        url(r'^create$', VariablesCreateView.as_view(), name='kolekti_release_lang_variable_create'),
                        url(r'^upload$', VariablesUploadView.as_view(), name='kolekti_release_lang_variable_upload'),
                        url(r'^editvar$', VariablesEditvarView.as_view(), name='kolekti_release_lang_variable_editval'),
                        url(r'^editcol$', VariablesEditcolView.as_view(), name='kolekti_release_lang_variable_editcol'),
                        url(r'^ods$', VariablesODSView.as_view(), name='kolekti_release_lang_variable_ods'),
                        url(r'^$', VariablesListView.as_view(), name='kolekti_release_lang_variables_browse'),
                    ]))
                ])),

                url(r'^publications/*', ReleaseLangPublicationsView.as_view(),name='kolekti_release_lang_publications'),
                url(r'^publications.json$', ReleaseLangPublicationsListJsonView.as_view(),name='kolekti_release_lang_publications_list_json'),
                url(r'^edit/(?P<topic_id>[^/\?]+)/$', ReleaseLangEditTopicView.as_view(), name='kolekti_release_lang_edit_topic'),
            ])),
        ])), # /releases
        
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
                url(r'^tree$', SyncStatusTreeView.as_view(), name='kolekti_sync_tree'),
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
                url(r'^releasepublications/$', WidgetReleasePublicationsListView.as_view(), name='kolekti_widget_release_publications_list'),
                url(r'^search/$', WidgetSearchView.as_view(), name='kolekti_widget_search'),
                url(r'^publish_archive/$', WidgetPublishArchiveView.as_view(), name='kolekti_widget_publish_archive'),
            ])),
            url(r'^diff/', include([        
                url(r'^release-topic-source/$', CompareReleaseTopicSource.as_view(), name='kolekti_compare_topic_source'),
            ])),
            url(r'^history/$', ProjectHistoryView.as_view(), name='kolekti_project_history'),
            url(r'^publications.json$', PublicationsListJsonView.as_view(),name='kolekti_publications_list_json'),
            url(r'^publications/(?P<publication_path>.+)/zip/$', PublicationsZipView.as_view(),name='kolekti_publications_zip'),
            
        ])), #/api
        
        url(r'^(?P<path>.*)$', ProjectStaticView.as_view(), name='kolekti_project_static'),
    
    ]
