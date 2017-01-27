"""
Created on Oct 25, 2017

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'bulk'
urlpatterns = [
url(r'^$', views.home_view, name='home'),
url(r'^sample/(?P<pk>\d+)$', views.sample_detail, name='sample_detail'),
url(r'^sample/list$', views.sample_list, name='sample_list'),
url(r'^sample/create/$', views.sample_create, name='sample_create'),
url(r'^sample/update/(?P<pk>\d+)$', views.sample_update, name='sample_update'),
url(r'^sample/delete/(?P<pk>\d+)$', views.sample_delete, name='sample_delete'),
url(r'^library/(?P<pk>\d+)$', views.library_detail, name='library_detail'),
url(r'^library/list$', views.library_list, name='library_list'),
url(r'^library/create/$', views.LibraryCreate.as_view(), name='library_create'),
url(r'^library/create/(?P<from_sample>\d+)$', views.LibraryCreate.as_view(), name='library_create_from_sample'),
url(r'^library/update/(?P<pk>\d+)$', views.LibraryUpdate.as_view(), name='library_update'),
url(r'^library/delete/(?P<pk>\d+)$', views.library_delete, name='library_delete'),
]

