"""
Created on Oct 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals
from datetime import datetime
import os

#============================
# Django imports
#----------------------------
from django.conf import settings
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

    fields_to_exclude = [
    'ID',
    'Data',
    'Accepted',
    'Accepted by',
    'Re-run on',
    'Re-run by'
    ]
    values_to_exclude = [
    'id',
    'data',
    'accepted',
    'accepted_by',
    'rerun_at',
    'rerun_by'
    ]

    class Meta:
        ordering = ('run_id',)

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_sample'
    #     )

    ## database relationships
    sequencings = models.ManyToManyField(Sequencing)

    ## choices
    status_choices = (
        ('A', 'Accepted'),
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
    accepted = models.BooleanField("Accepted", default=False)
    accepted_by = create_chrfield("Accepted by")
    rerun_by = create_chrfield("Re-run by")
    rerun_at = models.DateField("Re-run on", blank=True, null=True)

    def save(self, sequencings=None, run_id=False, *args, **kwargs):
        """update the run_id, date and time and save the m2m as well."""
        if not self.pk:
            self.date = datetime.now().date().isoformat()
            self.time = datetime.now().time().isoformat()
        if not self.run_id:
            self.run_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        if sequencings:
            [self.sequencings.add(seq) for seq in sequencings]
        super(Run, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("picasso:run_detail", kwargs={"pk": self.pk})

    def get_workflow_display(self):
        return str(Workflow.objects.get(pk=self.workflow))

    def days_to_expire(self):
        """"calc number of days left before the run's temp results expire."""
        days = 30
        if self.rerun_at:
            start_date = self.rerun_at
        else:
            start_date = self.date

        if not self.status == "R":
            today = datetime.now().date()
            d = (today - start_date).days
            days = 0 if d >= days else days - d
        return days

    def get_path_temp(self):
        """"get the temporary run's results path in the working dir."""
        path = os.path.join(
            settings.WORKING_DIR_ROOT,
            self.get_workflow_display(),
            self.user,
            self.run_id,
            )
        return path

    def get_path_perm(self):
        """"get the permanent run's results path in the results archive."""
        path = os.path.join(
            settings.RESULTS_ARCHIVE,
            self.get_workflow_display(),
            self.user,
            self.run_id,
            )
        return path

    def accept_by(self, username):
        if not self.accepted:
            self.accepted = True
            self.accepted_by = username
            self.status = 'A'
            self.save()

    def __str__(self):
        return self.run_id


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
            MaxValueValidator(2000),
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



