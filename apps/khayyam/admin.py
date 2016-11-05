"""
Created on Oct 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin

from .models import Run, Workflow, Kronos

## third-party apps
# from simple_history.admin import SimpleHistoryAdmin

## Run information
class KronosInline(admin.StackedInline):
    model = Kronos

# class WorkflowInline(admin.StackedInline):
#     model = Workflow

class RunAdmin(admin.ModelAdmin):
    inlines = [KronosInline]
    list_display = [
    'run_id',
    'workflow',
    'user',
    'date',
    'time',
    'status'
    ]
    list_filter = ['workflow', 'user', 'date']
    search_fields = ['run_id']

class KronosAdmin(admin.ModelAdmin):
    list_display = ['run', 'num_jobs', 'num_pipelines', 'version']
    # list_filter = ['num_jobs', 'num_pipelines']
    search_fields = ['run']


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'version']
    list_filter = ['name']
    search_fields = ['name']

# class LibraryAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
#     fieldsets = [
#       (
#         '',
#         {'fields': [
#           "sample",
#           "pool_id",
#           "jira_ticket",
#           "description",
#           "num_sublibraries",
#           "projects"
#         ]
#         }
#       ),
#     ]
#     inlines = [
#       SublibraryInformationInline,
#       LibrarySampleDetailInline,
#       LibraryConstructionInformationInline,
#       LibraryQuantificationAndStorageInline
#       ]
#     list_display = ['sample', 'pool_id', 'jira_ticket']
#     list_filter = ['jira_ticket']
#     search_fields = ['pool_id']


admin.site.register(Run, RunAdmin)

## extra admin only information
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Kronos, KronosAdmin)


