"""
Created on Oct 19, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'khayyam'
urlpatterns = [
url(r'^$', views.home_view, name='home'),
url(r'^run/new$', views.WorkflowRun.as_view(), name='workflow_run'),
url(r'^run/new/(?P<from_sequencing>\d+)$', views.WorkflowRun.as_view(), name='workflow_run_from_sequencing'),
url(r'^run/re/(?P<pk>\d+)$', views.workflow_re_run, name='workflow_re_run'),
url(r'^run/stop/(?P<pk>\d+)$', views.workflow_stop, name='workflow_stop'),
]

