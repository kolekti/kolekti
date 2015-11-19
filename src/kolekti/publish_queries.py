# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

from datetime import datetime
import time
import urllib
import re
import os
import copy
import logging
import json
from lxml import etree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

class kolektiSparQL(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"} 
    def __init__(self, endpoint):
        self.sparql = SPARQLWrapper(endpoint)

    def process_queries(self, assembly):
        for dquery in assembly.xpath("//h:div[@class='kolekti:sparql']", namespaces=self.nsmap):
            query = dquery.xpath("string(h:p[@class='kolekti:sparql:query'])",  namespaces=self.nsmap)
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()
            resdiv = ET.Element('{http://www.w3.org/1999/xhtml}div', attrib = {"class":"kolekti:sparql:result"})
            pjson = ET.SubElement(resdiv,'{http://www.w3.org/1999/xhtml}p', attrib = {"class":"kolekti:sparql:result:json"})
            pjson.text = json.dumps(results)
            phisto = ET.SubElement(resdiv,'{http://www.w3.org/1999/xhtml}p', attrib = {"class":"kolekti:sparql:result:histogram"})
            pjson.text = self._to_json_chartjs_histogram(results)
            dquery.append(resdiv)
        return assembly

    def _to_et_table(self, result):
        tab = ET.Element('table')
        reslist = result['results']['bindings']
        title = reslist[0]['labelClass3']['value']
        thead = ET.SubElement(table, '{http://www.w3.org/1999/xhtml}thead')
        tbody = ET.SubElement(table, '{http://www.w3.org/1999/xhtml}tbody')
        return
    
    def _to_json_chartjs_histogram(self, result):
        reslist = result['results']['bindings']
        if len(reslist):
            try:
                res = {
                    "labels": [record['annee3']['value'] for record in reslist],
                    "datasets": [{
                        "label": reslist[0]['labelClass3']['value'],
                        "fillColor": "rgba(220,220,220,0.5)",
                        "strokeColor": "rgba(220,220,220,0.8)",
                        "highlightFill": "rgba(220,220,220,0.75)",
                        "highlightStroke": "rgba(220,220,220,1)",
                        "data": [record['xarrondi']['value'] for record in reslist]
                        }]
                    }
                
                return json.dumps(res)
            except:
                import traceback
                print traceback.format_exc()
                raise
        else:
            return "no data"
