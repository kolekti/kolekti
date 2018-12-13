# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(value, arg):
    return value[arg]

