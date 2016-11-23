"""
Created on Nov 18, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import absolute_import

import os
import subprocess as sub


#============================
# Django imports
#----------------------------
from django.conf import settings


#============================
# App imports
#----------------------------
from .utils import FileHandler


#============================
# Celery imports
#----------------------------
from celery import shared_task, Task
from celery.registry import tasks


#============================
# Celery tasks
#----------------------------
@shared_task
def move_files(src, dst):
    # since the src and dst are on the same Filesystem 
    # we can simply rename the files.
    print "moving files from %s to %s" % (src, dst)
    FileHandler.rename(src, dst)

