# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter(is_safe=True)
def statustext(string):
    res =  "Non initialisé"
    if string is not None and len(string):
        if string == 'edition':
            res =  "Nouveau"
        elif string == 'translation':
            res =  "En traduction"
        elif string == 'validation':
            res =  "En relecture"
        elif string == 'publication':
            res =  "Officialisé"

    return res




