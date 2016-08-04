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
logger = logging.getLogger(__name__)
import json
from copy import deepcopy

from lxml import etree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

    

class kolektiSparQL(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"} 
    def __init__(self, server):
        logger.debug("sparql server: %s"%server)
        self.server = server
        self.wrappers = {}
        
    def get_wrapper(self, endpoint):
        try:
            wrapper = self.wrappers[endpoint]
            logger.debug('cached endpoint')
        except KeyError:
            urlendpoint = self.server + endpoint
            logger.debug("url endpoint: %s"%urlendpoint)
            wrapper =  SPARQLWrapper(urlendpoint)
            self.wrappers.update({endpoint:wrapper})
        return wrapper

    def instanciate_parameters(self, vardef, endpoint):
        sparql = self.get_wrapper(endpoint)
        query_results={}
        for dquery in vardef.xpath("/uservariables/variable/values[query]"):
            idq = dquery.find('query').get('ref')
            results = None
            if idq is None: 
                query = dquery.xpath("string(query/sparql)")
            else:
                query = vardef.xpath("string(/uservariables/query[@id='%s']/sparql)"%idq)
                results = query_results.get(idq, None)
            if results is None:
                try:
                    logger.debug('uservar query : %s %s',endpoint, query)
                    sparql.setQuery(query)
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    results = results['results']['bindings']
                    if not idq is None:
                        query_results[idq] = results
                except:
                    import traceback
                    print traceback.format_exc()
                        
            for result in results:
                    ET.SubElement(dquery,'value', attrib = {'label':result.get('valueLabel').get('value'),
                                                            'data':result.get('valueData').get('value')})
                
    def process_queries(self, assembly):
        defaultendpoint = assembly.xpath('string(/h:html/h:head/h:meta[@name="kolekti.sparql.endpoint"]/@content)', namespaces=self.nsmap)
        for oldres in assembly.xpath("//*[@class='kolekti-sparql-result']", namespaces=self.nsmap):
            oldres.getparent().remove(oldres)
            
        for dquery in assembly.xpath("//*[@class='kolekti-sparql']", namespaces=self.nsmap):
            queryelt = dquery.xpath("*[@class='kolekti-sparql-query']",  namespaces=self.nsmap)[0]
            query = queryelt.xpath("string(.)")
            endpoint = queryelt.get('data-endpoint', defaultendpoint)
            logger.debug('sparql query')
            logger.debug('endpoint %s'%endpoint)
            logger.debug('query %s'%query)
            
            sparql = self.get_wrapper(endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            
            if not len(results['results']['bindings']):
                logger.debug("No result for query")
                try:
                    component = dquery.xpath('ancestor::h:div[starts-with(@class,"kolekti-component-")]',namespaces=self.nsmap)[0]
                    component.set('data-hidden','yes')
                    component.set('data-kolekti-sparql-empty','yes')
                except IndexError:
                    pass
                
            else:
                resdiv = ET.Element('{http://www.w3.org/1999/xhtml}div', attrib = {"class":"kolekti-sparql-result"})
                resjson = ET.SubElement(resdiv,'{http://www.w3.org/1999/xhtml}div', attrib = {"class":"kolekti-sparql-result-json"})
                resjson.text = json.dumps(results)

                try:
                    template = dquery.xpath(".//*[@class='kolekti-sparql-template']",  namespaces=self.nsmap)[0]
                    for result in results['results']['bindings']:
                        elt = deepcopy(template)
                        elt.set('class' ,"kolekti-sparql-result-template")
                        resdict = dict([(z.encode('utf-8'),v['value'].encode('utf-8')) for z,v in result.iteritems()])
                        self._instanciate(elt, resdict, True)
                        resdiv.append(elt)

                except IndexError:
                    print "no template for query"

                dquery.append(resdiv)
        return assembly

    def _instanciate(self, elt, values, root = False):
        for child in elt:
            self._instanciate(child, values)

        for attr in elt.keys():
            val = elt.get(attr)
            elt.set(attr, val.format(**values))

        if not elt.text is None and len(elt.text):
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
        sreslist = sorted(reslist, key=lambda s:s.get('year',{'value':'0'}).get('value'))
        for item in sreslist:
            year = item[u'year']['value']
            years.add(year)
            place = item[u'placeLabel']['value']
            try:
                series[place].append(item[u'xapprox']['value'])
            except KeyError:
                series[place]=[item[u'xapprox']['value']]
        res = {
            "unit":reslist[0].get('valueLabel',{'value':''}).get('value'),
            "seriescount":len(series.keys()),
            "labels":sorted(list(years)),
            "datasets":[{
                "label":k,
                "data":v
            } for k,v in series.iteritems()]}
        return json.dumps(res)
