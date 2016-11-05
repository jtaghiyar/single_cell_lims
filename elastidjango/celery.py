"""
Created on Oct 27, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import absolute_import
import os

#============================
# Celery imports
#----------------------------
from celery import Celery


#============================
# Django imports
#----------------------------
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elastidjango.settings')
from django.conf import settings # noqa

#============================
# main
#----------------------------
app = Celery('elastidajngo')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

# A common practice for reusable apps is to define all tasks in a separate
# tasks.py module, and this is how Celery autodiscovers these modules
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))