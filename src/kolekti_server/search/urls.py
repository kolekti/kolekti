from django.conf.urls import include, url
from .views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='search_home'),
]
