import os
from lxml import etree as ET
from django import template
register = template.Library()

def serialize(elt):
    return ET.tostring(elt, encoding="utf-8")

register.filter(serialize)

def serialize_content(elt):
    out = (elt.text or "")
    for c in elt:
        out = out + ET.tostring(c, encoding="utf-8") + (c.tail or "")
    return out

register.filter(serialize_content)
