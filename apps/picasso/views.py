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
    def _get_output_path(run, output_root):
        path = os.path.join(
            output_root,
            run.get_workflow_display(),
            run.user,
            run.run_id,
            run.run_id
            )
        return path

    run = get_object_or_404(Run, pk=pk)
    output_root = settings.WORKING_DIR_ROOT
    is_running = False
    is_authorized = False
    if request.method == 'POST':
        run.accepted = True
        run.accepted_by = request.user.username
        run.save()
    if run.accepted:
        output_root = settings.RESULTS_ARCHIVE
    if run.status == "R":
        is_running = True
    if run.user == request.user.username:
        is_authorized = True
    context = {
    'pk': pk,
    'run': run,
    'is_running': is_running,
    'is_authorized': is_authorized,
    'output_path': _get_output_path(run, output_root),
    }
    return context

@Render("picasso/run_list.html")
def run_list(request):
    """home page of the app."""
    context = {
    'runs': Run.objects.all()
    }
    return context
