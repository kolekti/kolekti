# -*- coding: utf-8 -*-

#     eLocus : Report generation
#     Copyright (C) 2016 Stéphane Bonhomme (stephane@exselt.com)

import tempfile
import subprocess
import sys
import logging
import os
from lxml import etree as ET

logger = logging.getLogger('kolekti.'+__name__)
    
LOCAL_ENCODING=sys.getfilesystemencoding()

try:
    from django.conf import settings
    appdir = settings.BASE_DIR
except:
    appdir = os.getcwd()

def to_svg(html):
    cmd = ['nodejs',os.path.normpath(os.path.join(appdir, 'd3js2img/d3svg.js'))]
    print cmd
    exccmd = subprocess.Popen(
        cmd,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        )

    stdoutdata, stderrdata = exccmd.communicate(html)
    logger.debug(stdoutdata)
    logger.debug(stderrdata)
    return stdoutdata

def to_png(html, css = None):
    
    svg = to_svg(html)
    
    if css:
        with open(css, 'r') as cssfile:
            csscontent = cssfile.read()
        svgelt = ET.XML(svg)
        styleelt = ET.Element('style', {'type':'text/css'})
        styleelt.text = ET.CDATA( csscontent )
        svgelt.insert(0,styleelt)
        svg = ET.tostring(svgelt)

    _,tmpf = tempfile.mkstemp(suffix='.svg')

    with open(tmpf, 'w') as f:
        f.write(svg)

    
    cmd = ['convert','-verbose','svg:'+tmpf,'png:']
    print ' '.join(cmd)
    exccmd = subprocess.Popen(cmd,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                )
    stdoutdata, stderrdata = exccmd.communicate(svg)
    # print stdoutdata
    print stderrdata
    
    return stdoutdata

def test():


    html = """<div xmlns="http://www.w3.org/1999/xhtml" class="ecorse-chart" data-chartdata="{&quot;head&quot;: {&quot;vars&quot;: [&quot;indicateurURI&quot;, &quot;indicateurLabel&quot;, &quot;placeURI&quot;, &quot;placeLabel&quot;, &quot;valueURI&quot;, &quot;valueLabel&quot;, &quot;year&quot;, &quot;xapprox&quot;]}, &quot;results&quot;: {&quot;bindings&quot;: [{&quot;placeURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://id.insee.fr/geo/commune/38229&quot;}, &quot;xapprox&quot;: {&quot;datatype&quot;: &quot;http://www.w3.org/2001/XMLSchema#decimal&quot;, &quot;type&quot;: &quot;typed-literal&quot;, &quot;value&quot;: &quot;1.0&quot;}, &quot;valueURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://ecorse.eu/schema/generic_metadata#valeur_nombre_d_etablissements&quot;}, &quot;indicateurLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;Hypermarch\u00e9&quot;}, &quot;placeLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;Meylan&quot;}, &quot;year&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;2014&quot;}, &quot;valueLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;valeur&quot;}, &quot;indicateurURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://ecorse.eu/open_data/insee.fr/BPE/***/schema#B101&quot;}}, {&quot;placeURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://id.insee.fr/geo/commune/38421&quot;}, &quot;xapprox&quot;: {&quot;datatype&quot;: &quot;http://www.w3.org/2001/XMLSchema#decimal&quot;, &quot;type&quot;: &quot;typed-literal&quot;, &quot;value&quot;: &quot;1.0&quot;}, &quot;valueURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://ecorse.eu/schema/generic_metadata#valeur_nombre_d_etablissements&quot;}, &quot;indicateurLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;Hypermarch\u00e9&quot;}, &quot;placeLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;Saint-Martin-d'H\u00e8res&quot;}, &quot;year&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;2014&quot;}, &quot;valueLabel&quot;: {&quot;type&quot;: &quot;literal&quot;, &quot;value&quot;: &quot;valeur&quot;}, &quot;indicateurURI&quot;: {&quot;type&quot;: &quot;uri&quot;, &quot;value&quot;: &quot;http://ecorse.eu/open_data/insee.fr/BPE/***/schema#B101&quot;}}]}}" data-chartkind="bar"/>"""
    with open('/tmp/in.html','w') as s:
        s.write(html)
    with open('/tmp/out.png','w') as o:
        o.write(to_png(html,"/home/waloo/Bureau/eLocus/eLocus/src/kolekti_server/kserver/static/components/css/chart.css"))
    

#    print to_svg(html)    

if __name__ == "__main__":
    test()

