"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os

#===========================
# Django imports
#---------------------------
from django.forms import (
    ModelForm,
    Form,
    CharField,
    FileField,
    EmailField,
    DateField,
    BooleanField,
    ChoiceField,
    ValidationError,
    inlineformset_factory,
    BaseInlineFormSet
    )
from django.forms.extras.widgets import SelectDateWidget

#===========================
# App imports
#---------------------------
from .models import (
    Sample,
    SampleClinicalInformation,
    Library,
    )

#===========================
# Helpers
#---------------------------
class SaveDefault(ModelForm):

    """
    Save the default values all the time.
    """

    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will
        get validated and saved."""
        return True

#===========================
# Sample forms
#---------------------------
class SampleForm(ModelForm):
    class Meta:
        model = Sample
        fields = "__all__"
        # widgets = {}
        labels = {
            'sample_id': ('*Sample ID'),
        }
        help_texts = {
            'sample_id': ('Sequencing ID (usually SA ID).'),
            'collaborator_sample_id': ('Original/clinical patient ID.'),
            }

    def clean(self):
        ## if it's a new instance, the sample_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(SampleForm, self).clean()
            sample_id = cleaned_data.get("sample_id")
            if len(Sample.objects.filter(sample_id=sample_id)):
                msg = "Sample ID already exists."
                self.add_error('sample_id', msg)

SampleClinicalInfoInlineFormset =  inlineformset_factory(
    Sample,
    SampleClinicalInformation,
    form = SaveDefault,
    # exclude = ['sample'],
    fields = "__all__",
    widgets = {
        'diagnosis_date': SelectDateWidget(
            years=range(2000, 2020),
            empty_label=('year', 'month', 'day')
            ),
        'last_followup_date': SelectDateWidget(
            years=range(2000, 2020),
            empty_label=('year', 'month', 'day')
            )
    }
    # can_delete = True,
    # help_texts = {
    #     'patient_biopsy_date': ('yyyy-mm-dd.')
    # },
    )


#===========================
# Library forms
#---------------------------
class LibraryForm(ModelForm):
    class Meta:
        model = Library
        fields = "__all__"
        # exclude = []
        labels = {
            'sample': ('*Sample'),
            'library_id': ('*Library ID'),
            'consent_id': ('*Consent ID'),
            }
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID).'),
            'library_id': ('GSC library ID or pool ID.'),
            'consent_id': ('Consent ID from Atim or other clinical records.'),
            }

    def clean(self):
        ## if it's a new instance, the library_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(LibraryForm, self).clean()
            library_id = cleaned_data.get("library_id")
            if len(Library.objects.filter(library_id=library_id)):
                msg = "Library ID already exists."
                self.add_error('library_id', msg)
