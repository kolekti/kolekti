from django.conf.urls import patterns, include, url
from views import *
from django.contrib import admin
admin.autodiscover()

urls = [

    url(r'^$', TranslatorsHomeView.as_view(), name='translators_home'),
    url(r'^(?P<project>[0-9_.\w-]+)/', include([
        url(r'^$', TranslatorsHomeView.as_view(), name='translators_project'),
        url('release/states/$', TranslatorsReleaseStatusesView.as_view(), name='translators_statuses'),
        url('langs/$', TranslatorsLangsView.as_view(), name='translators_home'),
        url('documents/$', TranslatorsDocumentsView.as_view(), name='translators_documents'),
        url('publish/$', TranslatorsPublishView.as_view(), name='translators_publish'),
        url('source/zip/$', TranslatorsSourceZipView.as_view(), name='translators_src_zip'),
        url('source/assembly/$', TranslatorsSourceAssemblyView.as_view(), name='translators_src_assembly'),
        url(r'^admin/$', TranslatorsAdminView.as_view(), name='translators_admin'),
        url(r'^(?P<release>[0-9_. \w-]+)/', include([
            url(r'^$', TranslatorsHomeView.as_view(), name='translators_release'),
            url(r'^admin/add$', TranslatorsAdminAddView.as_view(), name='translators_admin_add'),
            url(r'^admin/remove$', TranslatorsAdminRemoveView.as_view(), name='translators_admin_remove'),            
            url('upload/$', TranslatorsUploadView.as_view(), name='translators_upload'),
            url(r'^(?P<lang>[_.\w-]+)/', include([
                url('commit/$', TranslatorsCommitLangView.as_view(), name='translators_commit_lang'),
            ])),
        ])),
    ])),
]
urlpatterns = patterns('', *urls)
