"""
Created on Oct 19, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""


import os

#============================
# Django imports
#----------------------------
from django.conf import settings
from django.shortcuts import get_object_or_404
# from django.contrib.auth.decorators import login_required #, permission_required

#============================
# App imports
#----------------------------
from .tasks import move_files
from core.decorators import Render
from khayyam.models import Run

#============================
# Home page of the app
#----------------------------
@Render("picasso/home.html")
def home_view(request):
    """home page of the app."""
    context = {
    }
    # request.session.pop('run')

    return context

@Render("picasso/run_detail.html")
def run_detail(request, pk):
    """Run detail page."""
    run = get_object_or_404(Run, pk=pk)
    temp_path = run.get_path_temp()
    perm_path = run.get_path_perm()
    is_running = False
    is_authorized = False
    if run.status == "R":
        is_running = True
    if run.user == request.user.username:
        is_authorized = True
    if run.accepted:
        output_path = perm_path
    # if results are already accepted, resending the POST request
    # by refreshing the page shouldn't trigger the saving and copying again.
    #  So, we need to check if not run.accepted.
    elif request.method == 'POST':
        run.accept_by(request.user.username)
        move_files.delay(temp_path, perm_path)
        output_path = perm_path
    else:
        output_path = temp_path
    context = {
    'pk': pk,
    'run': run,
    'is_running': is_running,
    'is_authorized': is_authorized,
    'output_path': output_path,
    }
    return context

@Render("picasso/run_list.html")
def run_list(request):
    """home page of the app."""
    context = {
    'runs': Run.objects.all()
    }
    return context
