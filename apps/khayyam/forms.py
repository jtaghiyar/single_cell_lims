"""
Created on Oct 19, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os

#===========================
# Django imports
#---------------------------
from django import forms
# from django.forms.extras.widgets import SelectDateWidget

#===========================
# App imports
#---------------------------
from .models import (
    Run,
    Kronos
    )
# from .utils import parse_smartchipapp_file

#===========================
# Workflow forms
#---------------------------
class RunForm(forms.ModelForm):
    class Meta:
            model = Run
            fields = ["workflow", "sequencings", "comments"]
            # widgets = {
            # 'xenograft_biopsy_date': SelectDateWidget(
            #     years=range(2000, 2020),
            #     empty_label=('year', 'month', 'day')
            #     )
            # }
            labels = {
                'workflow': ('*Workflow:'),
                'sequencings': ('*Input sequencing:'),
            }
            # help_texts = {
            #     'workflow': ('Select a workflow to run.'),
            # }

        # def clean(self):
        #     ## if it's a new instance, the sample_id should not exist.
        #     if not self.instance.pk:
        #         cleaned_data = super(SampleForm, self).clean()
        #         sample_id = cleaned_data.get("sample_id")
        #         if len(Sample.objects.filter(sample_id=sample_id)):
        #             msg = "Sample ID already exists."
        #             self.add_error('sample_id', msg)


class KronosForm(forms.ModelForm):
    # class Meta:
    #     model = Kronos
    #     # fields = "__all__"
    #     exclude = ["run", "version", "qsub_options"]
    def has_changed(self):
        """ Should returns True if data differs from initial. 
        By always returning true even unchanged inlines will 
        get validated and saved."""
        return True

KronosInlineFormset =  forms.inlineformset_factory(
    Run,
    Kronos,
    form = KronosForm,
    # exclude = ['delete'],
    fields = ["num_jobs"],
    # widgets = {},
    can_delete = False,
    help_texts = {
        'num_jobs': "Choose in the range of 1-100.",
        'num_pipelines': "Choose in the range of 1-50.",
    },
    )


# class SamplesFileForm(forms.Form):
#     samples_file = forms.FileField(
#         label="Samples File",
#         required=False,
#         )

#     def clean_something(self):
#         pass

