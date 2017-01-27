"""
Created on Jan 25, 2017

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
from .forms import (
	SampleForm,
	SampleClinicalInfoInlineFormset,
	LibraryForm
	)
from .models import Sample, Library

#============================
# Home page of the app
#----------------------------
@Render("bulk/home.html")
def home_view(request):
    """home page of the app."""
    context = {}
    return context


#============================
# Sample views
#----------------------------
@Render("bulk/sample_list.html")
def sample_list(request):
    """list of samples."""
    samples = Sample.objects.all().order_by('sample_id')
    context = {'samples': samples}
    return context

@Render("bulk/sample_detail.html")
def sample_detail(request, pk):
    """sample detail page."""
    sample = get_object_or_404(Sample, pk=pk)
    context = {
    'sample': sample
    }
    return context

@Render("bulk/sample_create.html")
@login_required()
def sample_create(request):
    """sample create page."""
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            additional_info_formset = SampleClinicalInfoInlineFormset(
                request.POST,
                instance=instance
                )
            if additional_info_formset.is_valid():
                additional_info_formset.save()

            msg = "Successfully created the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the sample. Please fix the errors below."
            messages.error(request, msg)
            formset = SampleClinicalInfoInlineFormset()
    
    else:
        form = SampleForm()
        formset = SampleClinicalInfoInlineFormset()
    
    context = {
        'form': form,
        'formset': formset
        }
    return context


@Render("bulk/sample_update.html")
@login_required()
def sample_update(request, pk):
    """sample update page."""
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == 'POST':
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            additional_info_formset = SampleClinicalInfoInlineFormset(
                request.POST,
                instance=instance
                )
            if additional_info_formset.is_valid():
                additional_info_formset.save()

            msg = "Successfully updated the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to update the sample. Please fix the errors below."
            messages.error(request, msg)
            formset = SampleClinicalInfoInlineFormset(instance=sample)

    else:
        form = SampleForm(instance=sample)
        formset = SampleClinicalInfoInlineFormset(instance=sample)

    context = {
        'form': form,
        'formset': formset,
        'pk': pk,
    }
    return context

@Render("bulk/sample_delete.html")
@login_required()
def sample_delete(request, pk):
    """sample delete page."""
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == 'POST':
        sample.delete()
        msg = "Successfully deleted the Sample."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('bulk:sample_list'))

    context = {
        'sample': sample,
        'pk': pk
    }
    return context


#============================
# Library views
#----------------------------
@Render("bulk/library_list.html")
def library_list(request):
    """list of libraries."""
    libraries = Library.objects.all().order_by('library_id')
    context = {'libraries': libraries}
    return context

@Render("bulk/library_detail.html")
def library_detail(request, pk):
    """library detail page."""
    library = get_object_or_404(Library, pk=pk)
    context = {
    'library': library,
    }
    return context

@Render("bulk/library_delete.html")
@login_required()
def library_delete(request, pk):
    """library delete page."""
    library = get_object_or_404(Library, pk=pk)

    if request.method == 'POST':
        library.delete()
        msg = "Successfully deleted the Library."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('bulk:library_list'))

    context = {
        'library': library,
        'pk': pk
    }
    return context
            
@method_decorator(login_required, name='dispatch')
class LibraryCreate(TemplateView):

    """
    Library create page.
    """

    template_name = "bulk/library_create.html"

    def get_context_data(self, from_sample=None):
        if from_sample:
            sample = get_object_or_404(Sample, pk=from_sample)
        else:
            sample = None
        context = {
        'lib_form': LibraryForm(),
        'sample': str(sample),
        'sample_id': from_sample,
        'related_libs': Library.objects.all()
        }
        return context

    def get(self, request, from_sample=None, *args, **kwargs):
        context = self.get_context_data(from_sample)
        return render(request, self.template_name, context)

    def post(self, request, from_sample=None, *args, **kwargs):
        context = self.get_context_data(from_sample)
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        # request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        lib_form = LibraryForm(request.POST)
        context['lib_form'] = lib_form
        if lib_form.is_valid():
            ## if 'commit=True' when saving lib_form, then it strangely
            ## raises the following error when trying to save the
            ## ManyToMany 'Projects' field:
            ## 'LibraryForm' object has no attribute 'save_m2m'.
            instance = lib_form.save(commit=False)
            all_valid, formsets = self._validate_formsets(request, instance)
            context.update(formsets)
            if all_valid:
                instance.save()
                # save the ManyToMany field.
                lib_form.save_m2m()
                # save the formsets.
                [formset.save() for formset in formsets.values()]
                msg = "Successfully created the Library."
                messages.success(request, msg)
                return HttpResponseRedirect(instance.get_absolute_url())

        msg = "Failed to create the library. Please fix the errors below."
        messages.error(request, msg)
        return render(request, self.template_name, context)

    def _validate_formsets(self, request, instance):
        all_valid = True
        formsets = {
        # 'libdetail_formset': LibrarySampleDetailInlineFormset(
        #     request.POST,
        #     instance=instance
        #     ),
        # 'libcons_formset': LibraryConstructionInfoInlineFormset(
        #     request.POST,
        #     instance=instance
        #     ),
        # 'libqs_formset': LibraryQuantificationAndStorageInlineFormset(
        #     request.POST,
        #     request.FILES or None,
        #     instance=instance
        #     )
        }
        for k, formset in formsets.items():
            if not formset.is_valid():
                all_valid = False
            formsets[k] = formset
        return all_valid, formsets


class LibraryUpdate(LibraryCreate):

    """
    Library update page.
    """

    template_name = "bulk/library_update.html"

    def get_context_data(self, pk):
        library = get_object_or_404(Library, pk=pk)
        # selected_projects = library.projects.names()
        # selected_related_libs = library.relates_to.only()
        context = {
        'pk': pk,
        'lib_form': LibraryForm(instance=library),
        # 'projects': [t.name for t in Tag.objects.all()],
        # 'selected_projects': selected_projects,
        # 'related_libs': Library.objects.all(),
        # 'selected_related_libs': selected_related_libs
        }
        return context

    def get(self, request, pk, *args, **kwargs):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        context = self.get_context_data(pk)
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        # request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        library = get_object_or_404(Library, pk=pk)
        lib_form = LibraryForm(request.POST, instance=library)
        context['lib_form'] = lib_form
        if lib_form.is_valid():
            # if 'commit=True' when saving lib_form, then it strangely
            # raises the following error when trying to save the
            # ManyToMany 'Projects' field:
            # 'LibraryForm' object has no attribute 'save_m2m'.
            instance = lib_form.save(commit=False)
            all_valid, formsets = self._validate_formsets(request, instance)
            context.update(formsets)
            if all_valid:
                instance.save()
                # save the ManyToMany field.
                lib_form.save_m2m()
                # save the formsets.
                [formset.save() for formset in formsets.values()]
                msg = "Successfully created the Library."
                messages.success(request, msg)
                return HttpResponseRedirect(instance.get_absolute_url())

        msg = "Failed to create the library. Please fix the errors below."
        messages.error(request, msg)
        return render(request, self.template_name, context)
