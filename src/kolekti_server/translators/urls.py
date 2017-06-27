from django.conf.urls import include, url
from views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = [

    url(r'^$', TranslatorsHomeView.as_view(), name='translators_home'),
    url(r'^upload/$', TranslatorsAssemblyUploadView.as_view(), name='translators_upload_assembly'),
    url(r'^(?P<project>[0-9_.\w-]+)/', include([
        url(r'^$', TranslatorsHomeView.as_view(), name='translators_project'),
        url('release/states/$', TranslatorsReleaseStatusesView.as_view(), name='translators_statuses'),
        url('release/admin/states/$', TranslatorsAdminReleaseStatusesView.as_view(), name='admin_translators_statuses'),
        url('langs/$', TranslatorsLangsView.as_view(), name='translators_home'),
        url('documents/$', TranslatorsDocumentsView.as_view(), name='translators_documents'),
        url('publish/$', TranslatorsPublishView.as_view(), name='translators_publish'),
        url(r'^admin/$', TranslatorsAdminView.as_view(), name='translators_admin'),
        url(r'^(?P<release>[0-9_. \w-]+)/', include([
            url(r'^$', TranslatorsHomeView.as_view(), name='translators_release'),
            url(r'^source/zip/$', TranslatorsSourceZipView.as_view(), name='translators_src_zip'),
            url(r'^source/assembly/$', TranslatorsSourceAssemblyView.as_view(), name='translators_src_assembly'),
            url(r'^admin/add$', TranslatorsAdminAddView.as_view(), name='translators_admin_add'),
            url(r'^admin/remove$', TranslatorsAdminRemoveView.as_view(), name='translators_admin_remove'),            
            url(r'^upload/$', TranslatorsUploadView.as_view(), name='translators_upload'),
            url(r'^(?P<lang>[_.\w-]+)/', include([
                url('commit/$', TranslatorsCommitLangView.as_view(), name='translators_commit_lang'),
                url('certif/$', TranslatorsCertificateUploadView.as_view(), name='translators_upload_certif'),
            ])),
            url(r'^(?P<path>.*)$', TranslatorsStaticView.as_view(), name='translators_static'),
            
        ])),
    ])),
]

