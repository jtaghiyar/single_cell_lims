"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os
#============================
# Django imports
#----------------------------
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse

#============================
# App imports
#----------------------------
from core.helpers import Render
from core import models as cm
from bulk import models as bm
from khayyam.models import Run

#============================
# Index page
#----------------------------
@Render("core/index.html")
def index_view(request):
    context = {
    'sc_sample_size': cm.Sample.objects.count(),
    'sc_library_size': cm.Library.objects.count(),
    'sc_sequencing_size': cm.Sequencing.objects.count(),
    'wg_sample_size': bm.Sample.objects.count(),
    'wg_library_size': bm.Library.objects.count(),
    }
    return context


#============================
# Search view
#----------------------------
def search_view(request):
    query_str = request.GET.get('query_str')
    instance = None

    ## search for singel cell samples
    qs = cm.Sample.objects.filter(sample_id=query_str)
    if qs:
        instance = qs[0]
        return HttpResponseRedirect(instance.get_absolute_url())

    ## search for singel libraries
    qs = cm.Library.objects.filter(pool_id=query_str)
    if qs:
        instance = qs[0]
        return HttpResponseRedirect(instance.get_absolute_url())

    ## search for runs
    qs = Run.objects.filter(run_id=query_str)
    if qs:
        instance = qs[0]
        return HttpResponseRedirect(instance.get_absolute_url())

    ## no match found message
    msg = "Sorry, no match found."
    messages.warning(request, msg)
    return HttpResponseRedirect(reverse('index'))
