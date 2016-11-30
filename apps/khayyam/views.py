"""
Created on Oct 19, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from datetime import datetime

#============================
# Django imports
#----------------------------
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

#============================
# App imports
#----------------------------
from core.decorators import Render
from core.models import Sequencing
from .forms import RunForm, KronosInlineFormset 
from .models import Workflow, Run, Kronos
from .tasks import run_workflow, stop_workflow

#============================
# Home page of the app
#----------------------------
@Render("khayyam/home.html")
def home_view(request):
    """home page of the app."""
    context = {}
    return context

@method_decorator(login_required, name='dispatch')
class WorkflowRun(TemplateView):

    """
    Workflow fresh run.
    """

    template_name = "khayyam/workflow_run.html"

    def get_context_data(self, from_sequencing=None):
        if from_sequencing:
            sequencing = get_object_or_404(Sequencing, pk=from_sequencing)
        else:
            sequencing = None
        context = {
            'run_form': RunForm(),
            'kronos_formset': KronosInlineFormset(),
            'data_list': Sequencing.objects.with_data(),
            'active_workflows': Workflow.active_objects.all(),
            'sequencing': sequencing,
            'sequencing_id': from_sequencing,
            }
        return context

    def get(self, request, from_sequencing=None, *args, **kwargs):
        context = self.get_context_data(from_sequencing)
        return render(request, self.template_name, context)

    def post(self, request, from_sequencing=None, *args, **kwargs):
        context = self.get_context_data(from_sequencing)
        request.POST['sequencings'] = ','.join(request.POST.getlist('sequencings'))
        run_form = RunForm(request.POST)
        context['run_form'] = run_form
        if run_form.is_valid():
            run = run_form.save(commit=False)
            run.user = request.user.username
            run.status = "R" # running

            kronos_formset = KronosInlineFormset(request.POST, instance=run)
            context['kronos_formset'] = kronos_formset
            if kronos_formset.is_valid():
                run.save()
                run_form.save_m2m()
                kronos_formset.save()

                # run the workflow asynchronously
                run_workflow.delay(run.id)
                
                msg = "Successfully triggered the workflow run."
                messages.success(request, msg)
                return HttpResponseRedirect(run.get_absolute_url())

        msg = "Failed to initialize the workflow. Please fix the errors below."
        messages.error(request, msg)    
        return render(request, self.template_name, context)

@login_required()
def workflow_re_run(request, pk):
    """ Re_run previous run with the same run ID."""
    if request.method == 'POST':
        run = get_object_or_404(Run, pk=pk)
        run.rerun_at = datetime.now().date().isoformat()
        run.rerun_by = request.user.username
        run.status = "R" # running
        run.save()

        # run the workflow asynchronously
        run_workflow.delay(run.id)

        msg = "Successfully triggered the workflow re-run."
        messages.success(request, msg)
        return HttpResponseRedirect(run.get_absolute_url())
    else:
        context = {}
    return context

@Render("khayyam/workflow_stop.html")
@login_required()
def workflow_stop(request, pk):
    """sample delete page."""
    run = get_object_or_404(Run, pk=pk)
    if request.method == 'POST':
        stop_workflow.delay(pk)
        msg = "Successfully triggered the workflow stop."
        messages.success(request, msg)
        return HttpResponseRedirect(run.get_absolute_url())

    context = {
    'pk':  pk,
    'run_id': run.run_id
    }
    return context
