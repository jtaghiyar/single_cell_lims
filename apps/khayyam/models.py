"""
Created on Oct 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals

#============================
# Django imports
#----------------------------
from django.core.urlresolvers import reverse
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

#============================
# App imports
#----------------------------
from core.helpers import *
from core.models import Sequencing

#============================
# Helpers
#----------------------------
class ActiveWorkflowManager(models.Manager):
    def get_queryset(self):
        return super(ActiveWorkflowManager, self).get_queryset().filter(
            active=True
            )

#============================
# Run models
#----------------------------
class Workflow(models.Model):

    """
    A model for storing workflow information.
    """

    class Meta:
        ordering = ('name', 'version')

    name = create_chrfield("Name", blank=False)
    version = create_chrfield("Version", blank=False)
    components_dir = create_pathfield("Components dir", blank=False)
    config_file = create_pathfield("Config file", blank=False)
    setup_file = create_pathfield("Setup file", blank=False)
    repository = create_pathfield("Repository", blank=False)
    python_venv = create_pathfield("Python Virtualenv")
    archive_path = create_pathfield("Archive path")
    active = models.BooleanField("Active")

    objects = models.Manager()
    active_objects = ActiveWorkflowManager()

    def __str__(self):
        return '_'.join([self.name, self.version])


class Run(models.Model, FieldValue):

    """
    A model for storing a workflow run information.
    """

    fields_to_exclude = ['ID', 'Data', 'Accepted', 'Accepted by']
    values_to_exclude = ['id', 'data', 'accepted', 'accepted_by']

    class Meta:
        ordering = ('run_id',)

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_sample'
    #     )

    ## choices
    status_choices = (
        ('D','Done'),
        ('F','Failed'),
        ('R','Running'),
        ('S','Stopped'),
        )

    ## required fields
    run_id = create_chrfield("Run ID", blank=False)
    workflow = create_intfield("Workflow", blank=False)
    user = create_chrfield("User", blank=False)
    date = models.DateField("Date", blank=False)
    time = models.TimeField("Time", blank=False)
    status = create_chrfield("Status", choices=status_choices, blank=False)
    comments = create_textfield("Comments")
    data = create_textfield("Data", blank=False, max_length=1000)
    accepted = models.BooleanField("Accepted")
    accepted_by = create_chrfield("Accepted by")

    def get_absolute_url(self):
        return reverse("picasso:run_detail", kwargs={"pk": self.pk})

    def get_workflow_display(self):
        return str(Workflow.objects.get(pk=self.workflow))

    def get_data(self):
        ids = self.data.strip().split(',')
        return Sequencing.objects.filter(id__in=ids)

    def __str__(self):
        return self.run_id


# class Data(models.Model, FieldValue):

#     """
#     A model for storing the data file used when running the workflow.
#     """

#     ## track history
#     # history = HistoricalRecords(
#     #     table_name='history_sublibrary_information'
#     #     )

#     ## database relationships
#     run = models.ForeignKey(
#         Run,
#         verbose_name="Run",
#         on_delete=models.CASCADE
#         )

#     ## other fields
#     name = create_chrfield('Name')
#     path = create_pathfield('Path')
#     comments = create_textfield('Comments')


class Kronos(models.Model, FieldValue):

    """
    A model for storing the input options/settings of Kronos.
    """

    fields_to_exclude = ['ID', 'Run', 'qsub options']
    values_to_exclude = ['id', 'run', 'qsub_options']

    ## database relationships
    run = models.OneToOneField(
        Run,
        verbose_name="Run",
        on_delete=models.CASCADE
        )

    ## required fields
    # components_dir = create_pathfield("Components dir", blank=False)
    version = create_chrfield("Version", blank=False)

    ## other fields
    num_jobs = create_intfield(
        "Number of jobs",
        default=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ],
        )
    num_pipelines = create_intfield(
        "Number of pipelines",
        default=1,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(1)
        ],
        )
    qsub_options = create_pathfield("qsub options")
    # kronos_workflow = create_chrfield("Kronos workflow")
    # python_installation = create_pathfield("Python installation")
    # drmaa_library_path = create_pathfield("Drmaa library path")
    # workflow_name = create_chrfield("Workflow name")
    # samples_file = create_chrfield("Samples file", max_length=200)
    # runid = create_chrfield("Run ID")
    # setup_file = create_pathfield("Setup file")
    # working_dir = create_pathfield("Working dir")
    # config_file = create_pathfield("Config file")
    # no_prefix = models.BooleanField("No prefix")
    # job_scheduler = create_chrfield(
    #     "Job scheduler",
    #     choices=[('S','SGE'), ('D','Drmaa')],
    #     default='S',
    #     )

    def __str__(self):
        return self.run.run_id



