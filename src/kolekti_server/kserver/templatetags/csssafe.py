import os
from django import template
register = template.Library()

def csssafe(inputs):
    return inputs.replace(' ','-')

register.filter(csssafe)
