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
from copy import deepcopy
from lxml import etree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

class kolektiSparQL(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"} 
    def __init__(self, endpoint):
        self.sparql = SPARQLWrapper(endpoint)
        print endpoint

    def get_communes(self):
        query = """PREFIX generic_metadata: <http://ecorse.eu/schema/generic_metadata#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?communeURI ?communeLabel
        WHERE {
        ?communeURI a <http://rdf.insee.fr/def/geo#Commune> ;
         rdfs:label ?communeLabel .
        }
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return [{"id":e.get('communeURI').get('value').split('/')[-1], "name":e.get('communeLabel').get('value')} for e in results['results']['bindings']]
    
        
    def process_queries(self, assembly):
        for oldres in assembly.xpath("//h:div[@class='kolekti-sparql-result' or @class='kolekti-sparql-foreach-results']", namespaces=self.nsmap):
            oldres.getparent().remove(oldres)
            
        for dquery in assembly.xpath("//h:div[@class='kolekti-sparql']", namespaces=self.nsmap):
            query = dquery.xpath("string(h:p[@class='kolekti-sparql-query'])",  namespaces=self.nsmap)
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()
            topic = dquery.xpath('ancestor::h:div[@class="topic"]',namespaces=self.nsmap)[0]
            if topic.get("data-chart-kind") is None:
                topic.set("data-chart-kind","Bar")
            if not len(results['results']['bindings']):
                topic.set('data-hidden','yes')
                
            else:
                resdiv = ET.Element('{http://www.w3.org/1999/xhtml}div', attrib = {"class":"kolekti-sparql-result"})
                pjson = ET.SubElement(resdiv,'{http://www.w3.org/1999/xhtml}p', attrib = {"class":"kolekti-sparql-result-json"})
                pjson.text = json.dumps(results)
                phisto = ET.SubElement(resdiv,'{http://www.w3.org/1999/xhtml}p', attrib = {"class":"kolekti-sparql-result-chartjs"})
                phisto.text = self._to_json_chartjs(results)
                dquery.append(resdiv)
            
                
        for dquery in assembly.xpath("//h:div[@class='kolekti-sparql-foreach']", namespaces=self.nsmap):
            query = dquery.xpath("string(h:p[@class='kolekti-sparql-foreach-query'])",  namespaces=self.nsmap)
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()
            template = dquery.xpath("h:div[@class='kolekti-sparql-foreach-template']",  namespaces=self.nsmap)[0]
            dres = ET.SubElement(dquery,'{http://www.w3.org/1999/xhtml}div', attrib = {"class":"kolekti-sparql-foreach-results"})

            
            for result in results['results']['bindings']:
                elt = deepcopy(template)
                elt.set('class' ,"kolekti-sparql-foreach-result")
                resdict = dict([(z.encode('utf-8'),v['value'].encode('utf-8')) for z,v in result.iteritems()])
                self._instanciate(elt, resdict, True)
                dres.append(elt)
                
        return assembly

    def _instanciate(self, elt, values, root = False):
        for child in elt:
            self._instanciate(child, values)

        for attr in elt.keys():
            val = elt.get(attr)
            elt.set(attr, val.format(**values))

        if len(elt.text):
            t = elt.text
            t = t.encode('utf-8')
            t = t.format(**values)
            html = ET.HTML('<html><body><span class="tplvalue">'+t.decode('utf-8')+'</span></body></html>')
            span = html.find('body').find('span')
            if len(span) == 0:
                elt.text = t.decode('utf-8')
            else:
                elt.text=""
                elt.insert(0,span)
                
        if (not root) and not elt.tail is None :
            t = elt.tail
            t = t.encode('utf-8')
            t = t.format(**values)
            elt.tail = t.decode('utf-8')


            
    
    
    def _to_et_table(self, result):
        tab = ET.Element('table')
        reslist = result['results']['bindings']
        title = reslist[0]['indicateurLabel']['value']
        thead = ET.SubElement(table, '{http://www.w3.org/1999/xhtml}thead')
        tbody = ET.SubElement(table, '{http://www.w3.org/1999/xhtml}tbody')
        return
    
    def _to_json_chartjs(self, result):
        print '----'
        reslist = result['results']['bindings']
        years = set()
        series = {}
        sreslist = sorted(reslist, key=lambda s:s.get('year').get('value'))
        for item in sreslist:
            year = item[u'year']['value']
            years.add(year)
            place = item[u'placeLabel']['value']
            try:
                series[place].append(item[u'xapprox']['value'])
            except KeyError:
                series[place]=[item[u'xapprox']['value']]
#        if len(years)
#            resdict = dict([(z,v['value']) for z,v in item.iteritems()])
#            print
#            print resdict
        print "years", str(years)
        print "series", str(series)
        res = {
            "seriescount":len(series.keys()),
            "labels":sorted(list(years)),
            "datasets":[{
                "label":k,
                "data":v
                } for k,v in series.iteritems()]}
        return json.dumps(res)
        if len(reslist):
            labels = [record['year']['value'] for record in reslist]
            print labels
            try:
                res = {
                    "labels": [record['year']['value'] for record in reslist],
                    "datasets": [{
                        "label": reslist[0]['valueLabel']['value'],
                        "data": [record['xapprox']['value'] for record in reslist]
                        }]
                    }
                
                return json.dumps(res)
            except:
                import traceback
                print traceback.format_exc()
                raise
        else:
            return "no data"
