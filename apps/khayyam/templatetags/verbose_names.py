"""
Created on Nov 30, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django import template
register = template.Library()

@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """return verbose_name of the given field."""
    return instance._meta.get_field(field_name).verbose_name
