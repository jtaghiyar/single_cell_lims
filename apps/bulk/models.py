"""
Created on Jan 25, 2017

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals

#============================
# Django imports
#----------------------------
from django.core.urlresolvers import reverse
from django.db import models


#============================
# App imports
#----------------------------
from core.helpers import *


#============================
# 3rd-party app imports
#----------------------------
from simple_history.models import HistoricalRecords


#============================
# helpers
#----------------------------


#============================
# Sample models
#----------------------------
class Sample(models.Model, FieldValue):

    """
    Base class of different bulk (whole genome) sample types.
    """

    class Meta:
        ordering = ('sample_id',)

    ## track history
    history = HistoricalRecords(
        table_name='bulk_history_sample'
        )

    ## required fields
    sample_id = create_chrfield("Sample ID", blank=False)
    collaborator_sample_id = create_chrfield("Collaborator sample ID")
    project_name = create_chrfield("Project name")
    tumour_subtype = create_chrfield("Tumour subtype")
    genotype = create_chrfield("Genotype")
    tissue_cell_line = create_chrfield("Tissue/ Cell line")
    description = create_textfield("Description")

    def has_sample_clinical_information(self):
        return hasattr(self,
            'sampleclinicalinformation'
            )

    def get_absolute_url(self):
        return reverse("bulk:sample_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.sample_id


class SampleClinicalInformation(models.Model, FieldValue):

    """
    Clinical information for a bulk sample.
    """

    fields_to_exclude = ['ID', 'Sample']
    values_to_exclude = ['id', 'sample']

    ## database relationships
    sample = models.OneToOneField(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    ## choices
    status_choices = (
        ('D','Dead'),
        ('R','Relapse'),
        ('A','Alive with disease'),
        ('O','Dead of other causes'),
        ('N','No status'),
        )

    treatment_choices = (
        ('T','Chemotherapy'),
        ('C','Cisplatin'),
        )
    
    ## fields
    progression_free_survival = create_chrfield(
        "Progression free survival"
        )
    diagnosis_date = models.DateField(
        "Diagnosis date",
        null=True,
        blank=True,
        )
    last_followup_date = models.DateField(
        "Last follow-up date",
        null=True,
        blank=True,
        )
    status = create_chrfield(
        "Status",
        choices=status_choices,
        )
    treatment = create_chrfield(
        "Treatment",
        choices=treatment_choices,
        )


class Library(models.Model, FieldValue):

    """
    Library corresponding to a bulk sample.
    """

    class Meta:
        ordering = ('library_id',)


    ## track history
    history = HistoricalRecords(
        table_name='bulk_history_library'
        )

    ## database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    ## choices
    library_type_choices = (
        ('G','Genome'),
        ('E','Exome'),
        ('T','Transciptome amplicon'),
        ('C','ChIP'),
        ('O','Other'),
        )

    ## required fields
    library_id = create_chrfield("Library ID", blank=False)
    consent_id = create_chrfield("Consent ID", blank=False)

    ## other fields
    library_type = create_chrfield(
        "Library type",
        choices=library_type_choices
        )
    relates_to = models.ManyToManyField(
        "self",
        verbose_name="Relates to",
        # null=True,
        blank=True,
        )

    def get_absolute_url(self):
        return reverse("bulk:library_detail", kwargs={"pk": self.pk})

    def get_library_id(self):
        return '_'.join([self.sample.sample_id, self.library_id])

    def __str__(self):
        return 'LIB_' + self.get_library_id()
