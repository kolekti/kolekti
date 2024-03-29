from django.conf.urls import include, url
from views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = [

    url(r'^$', TranslatorsHomeView.as_view(), name='translators_home'),
    url(r'^upload/$', TranslatorsAssemblyUploadView.as_view(), name='translators_upload_assembly'),
    url(r'^update/check/$', TranslatorsCheckUpdateView.as_view(), name='translators_check_updates'),
    url(r'^svnhook/(?P<rev>[^/]+)/(?P<path>.*)$', TranslatorsHook.as_view(), name='translators_hook'),
    
    url(r'^(?P<project>[0-9_.\w-]+)/', include([
        url(r'^$', TranslatorsProjectView.as_view(), name='translators_project'),
        
        url(r'^langs/$', TranslatorsLangsView.as_view(), name='translators_langs'),        
        
        url(r'^admin/$', TranslatorsAdminView.as_view(), name='translators_admin'),
        url(r'^(?P<release>[^/]+)/', include([
            url(r'^$', TranslatorsReleaseView.as_view(), name='translators_release'),
            url(r'^admin/$', TranslatorsAdminReleaseView.as_view(), name='translators_admin_release'),
            url(r'^states/$', TranslatorsReleaseStatusesView.as_view(), name='translators_statuses'),
            url(r'^admin/states/$', TranslatorsAdminReleaseStatusesView.as_view(), name='admin_translators_statuses'),
            url(r'^upload/$', TranslatorsUploadView.as_view(), name='translators_upload'),
            url(r'^update/$', TranslatorsUpdateView.as_view(), name='translators_update'),


            url(r'^source/zip/$', TranslatorsSourceZipView.as_view(), name='translators_src_zip'),
            url(r'^source/assembly/$', TranslatorsSourceAssemblyView.as_view(), name='translators_src_assembly'),
            
            url(r'^admin/add$', TranslatorsAdminAddView.as_view(), name='translators_admin_add'),
            url(r'^admin/remove$', TranslatorsAdminRemoveView.as_view(), name='translators_admin_remove'),            
            url(r'^(?P<lang>[_.\w-]+)/', include([
                url(r'^source/zip/$', TranslatorsSourceZipView.as_view(), name='translators_src_zip'),
                url(r'^source/assembly/$', TranslatorsSourceAssemblyView.as_view(), name='translators_src_assembly'),
                url(r'^documents/$', TranslatorsDocumentsView.as_view(), name='translators_documents'),
                url(r'^publish/$', TranslatorsPublishView.as_view(), name='translators_publish'),
                url(r'^commit/$', TranslatorsCommitLangView.as_view(), name='translators_commit_lang'),
                url(r'^certify/$', TranslatorsCertifyDocumentView.as_view(), name='translators_certif'),
                url(r'^certificate/upload/$', TranslatorsCertificateUploadView.as_view(), name='translators_upload_certif'),
            ])),
            url(r'^(?P<path>.*)$', TranslatorsStaticView.as_view(), name='translators_static'),
            
        ])),
    ])),
]

