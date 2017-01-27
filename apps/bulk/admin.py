"""
Created on Jan 25, 2017

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample, SampleClinicalInformation, Library

## third-party apps
from simple_history.admin import SimpleHistoryAdmin


## Sample information
class SampleClinicalInformationInline(admin.StackedInline):
    model = SampleClinicalInformation

class SampleAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    inlines = [SampleClinicalInformationInline]
    list_display = ['sample_id', 'collaborator_sample_id', 'project_name']
    list_filter = ['tumour_subtype', 'genotype']
    search_fields = ['sample_id']


## Library information
class LibraryAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ['sample', 'library_id', 'library_type', 'consent_id']
    list_filter = ['sample', 'library_type']
    search_fields = ['library_id', 'consent_id']


admin.site.register(Sample, SampleAdmin)
admin.site.register(Library, LibraryAdmin)

## extra admin only information
admin.site.register(SampleClinicalInformation)

