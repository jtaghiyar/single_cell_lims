"""
Created on Oct 19, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'picasso'
urlpatterns = [
url(r'^$', views.home_view, name='home'),
url(r'^run/list$', views.run_list, name='run_list'),
url(r'^run/(?P<pk>\d+)$', views.run_detail, name='run_detail'),
]

