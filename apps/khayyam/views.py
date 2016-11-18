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

    def get_context_data(self):
        context = {
            'run_form': RunForm(),
            'kronos_formset': KronosInlineFormset(),
            'data_list': Sequencing.objects.with_data(),
            'active_workflows': Workflow.active_objects.all(),
            }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        run_form = RunForm(request.POST)
        context['run_form'] = run_form
        if run_form.is_valid():
            # update the attributes of the run instance that
            # users don't specify in the input form.
            run = run_form.save(commit=False)
            run.run_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
            run.user = str(request.user)
            run.date = datetime.now().date().isoformat()
            run.time = datetime.now().time().isoformat()
            run.status = "R" # running
            run.accepted = False
            run.data = ','.join(request.POST.getlist('data_selected'))

            kronos_formset = KronosInlineFormset(request.POST, instance=run)
            context['kronos_formset'] = kronos_formset
            if kronos_formset.is_valid():
                run.save()
                kronos_formset.save()

                # run the workflow asynchronously
                run_workflow.delay(run.id)
                
                msg = "Successfully triggered the workflow run."
                messages.success(request, msg)
                return HttpResponseRedirect(run.get_absolute_url())

        msg = "Failed to initialize the workflow. Please fix the errors below."
        messages.error(request, msg)    
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class WorkflowFromRun(TemplateView):

    """
    Workflow from_run, i.e. new run from a previous run.
    This will create a new run with new run ID.
    """

    template_name = "khayyam/workflow_from_run.html"

    def get_context_data(self, pk):
        run = get_object_or_404(Run, pk=pk)
        workflow = Workflow.objects.get(pk=run.workflow)
        context = {
            'run_form': RunForm(instance=run),
            'kronos_formset': KronosInlineFormset(instance=run),
            'data_list': Sequencing.objects.with_data(),
            'data_selected': run.get_data(),
            'active_workflows': Workflow.active_objects.all(),
            'workflow': workflow,
            'pk': pk,
            }
        return context, run.kronos

    def get(self, request, pk, *args, **kwargs):
        context,_ = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        context, kronos = self.get_context_data(pk)
        run = get_object_or_404(Run, pk=pk)
        run_form = RunForm(request.POST, instance=run)
        context['run_form'] = run_form
        if run_form.is_valid():
            # update the attributes of the run instance that
            # users don't specify in the input form.
            run = run_form.save(commit=False)
            run.run_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
            run.user = str(request.user)
            run.date = datetime.now().date().isoformat()
            run.time = datetime.now().time().isoformat()
            run.status = "R" # running
            run.accepted = False
            run.data = ','.join(request.POST.getlist('data_selected'))
            
            # save the new run
            run.pk = None
            run.save()
            kronos.id = None
            kronos.run_id = run.id
            kronos.save()

            # run the workflow asynchronously
            run_workflow.delay(run.id)
            msg = "Successfully triggered the workflow run."
            messages.success(request, msg)
            return HttpResponseRedirect(run.get_absolute_url())

        msg = "Failed to initialize the workflow. Please fix the errors below."
        messages.error(request, msg)    
        return render(request, self.template_name, context)


class WorkflowReRun(WorkflowFromRun):

    """
    Workflow re_run, i.e. re-run a previous run 
    from where it left off with the same run ID.
    """

    template_name = "khayyam/workflow_re_run.html"

    def post(self, request, pk, *args, **kwargs):
        context, kronos = self.get_context_data(pk)
        run = get_object_or_404(Run, pk=pk)
        run_form = RunForm(request.POST, instance=run)
        context['run_form'] = run_form
        if run_form.is_valid():
            # update the attributes of the run instance that
            # users don't specify in the input form.
            run = run_form.save(commit=False)
            run.user = str(request.user)
            run.date = datetime.now().date().isoformat()
            run.time = datetime.now().time().isoformat()
            run.status = "R" # running
            run.accepted = False
            run.data = ','.join(request.POST.getlist('data_selected'))
            # run.rerun = '**RERUN OF <a href="{0}">{1}</a>**'.format(
            # run.get_absolute_url(), run.run_id)
           
            # save the new run
            run.pk = None
            run.save()
            kronos.id = None
            kronos.run_id = run.id
            kronos.save()

            # run the workflow asynchronously
            run_workflow.delay(run.id)
            
            msg = "Successfully triggered the workflow run."
            messages.success(request, msg)
            return HttpResponseRedirect(run.get_absolute_url())

        msg = "Failed to initialize the workflow. Please fix the errors below."
        messages.error(request, msg)    
        return render(request, self.template_name, context)


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
