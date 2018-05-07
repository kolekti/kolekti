from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def svnmsg(string):
    res =  string.replace('\n', '<br>')
    return mark_safe(res)




