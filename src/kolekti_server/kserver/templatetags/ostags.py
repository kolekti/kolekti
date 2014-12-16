import os
from django import template
register = template.Library()

def basename(path):
    fname = path.split(os.path.sep)[-1]
    return os.path.splitext(fname)[0]

register.filter(basename)
