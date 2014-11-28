from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def diffline(string):
    res =  "<span class='diff diff-none'></span>"
    if len(string):
        if string[0] == '+':
            res =  "<span class='diff diff-plus'>" + string[2:] + "</span>"            
        if string[0] == '-':
            res =  "<span class='diff diff-minus'>" + string[2:] + "</span>"            
        if string [0] == ' ':
            res =  "<span class='diff'>" + string[2:] + "</span>"
        if string [0] == '?':
            res =  "<span class='hidden diff diff-positions' data-diff-positions='"+string[2:]+"'></span>"

    return mark_safe(res)




