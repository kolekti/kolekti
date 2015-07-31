# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import os
from zipfile import ZipFile
from lxml import etree as ET
import time

import common

def repl(s):
    if s is None:
        return ""
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return s

class Importer(common.kolektiBase):

    __nsxlsx = {"n":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    __nsods  = {"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0" ,
                "table" : "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                "text"  : "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
                }

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('lang'):
            self._lang = kwargs.get('lang')
            kwargs.pop('lang')
        super(Importer, self).__init__(*args, **kwargs)
    
    def substitute(self, template, **params):
        p = self.getOsPath(template)
        with open(p) as f:
            for line in f.readlines():
                yield(line.format(**params))  
    
    def importOds(self, odsfile):
        with ZipFile(odsfile, 'r') as zip:
            foffx=zip.read('content.xml')
            xcontent=ET.XML(foffx)
            conflines = self._ods_getlines(xcontent.xpath('/office:document-content/office:body/office:spreadsheet/table:table[1]',namespaces=self.__nsods)[0])
            template = conflines[0][1]
            path     = conflines[1][1]
            lines = self._ods_getlines(xcontent.xpath('/office:document-content/office:body/office:spreadsheet/table:table[2]',namespaces=self.__nsods)[0])
            return self._generate_topics(lines, template, path)
        
    def _ods_getlines(self, xtable):
        lines = []
        for line in xtable.xpath('table:table-row',namespaces=self.__nsods):
            l = []
            for col in line.xpath('table:table-cell',namespaces=self.__nsods):
                l.append(col.xpath('string(.)'))
            lines.append(l)

        return lines
                
    def importXlsx (self, xlsxfile):
        
        dz = zipfile.ZipFile(doc,'r')

        # read shared strings file
        szf = dz.open('xl/sharedStrings.xml', 'rU')
        sx = ET.XML(szf.read())
        strings=[]
        for s in sx:        
            strings.append(unicode(s.xpath("normalize-space(.//n:t)",namespaces=self.__nsxlsx)))

        # read genration parameters
        dzf = dz.open('xl/worksheets/sheet1.xml', 'rU')
        dx = ET.XML(dzf.read())
        conflines = self._xslx_getlines(dx, strings)
        template = conflines[0][1]
        path     = conflines[1][1]

        
        dzf = dz.open('xl/worksheets/sheet2.xml', 'rU')
        dx = ET.XML(dzf.read())
        lines = self._xslx_getlines(dx, strings)

        return self._generate_topics(lines, template, path)

    def _xslx_getlines(self, xsheet, strings):
        coln = [chr(v + 65) for v in range(26)] + ['A' + chr(v + 65) for v in range(26)]
        lines = []
        for line in dx.xpath('/n:worksheet/n:sheetData/n:row',namespaces=self.__nsxlsx):
            l = []
            for col in xrange(len(coln)):
                cnum = coln[col] + line.get('r')
                v = line.xpath('n:c[@r="%s"]/n:v'%cnum, namespaces=self.__nsxlsx)
                if len(v):
                    l.append(strings[int(v[0].text)])
                else:
                    l.append(None)

            for v in range(32):
                l.append(None)

            lines.append(l)
        return lines
        
    def _generate_topics(self, lines, template, path):

        outpath = '/sources/'+ self._lang + '/topics/' + path + "/"
        tplpath = '/sources/'+ self._lang + '/templates/' + template
        
        self.makedirs(outpath)
        nl = 0
        for l in lines[1:]:
            nl +=1 
            try:
                sheet_params = {}
                nc = 0
                for col in l:
                    if lines[0][nc] is None:
                        break
                    sheet_params[lines[0][nc]] = repl(col)
                    nc += 1
                topicfile = l[0]
                print sheet_params
                if topicfile is not None and len(topicfile):
                    buf = ""
                    for l in self.substitute(tplpath, **sheet_params):
                        buf += l
                    self.write(buf, outpath + topicfile)
                    yield { 'event':'result',
                            'file':outpath + topicfile,
                            'time':time.time(),
                            }
                                       
            except:
                import traceback
                print traceback.format_exc()
                yield {
                        'event':'error',
                        'msg':"Erreur lors de l'import",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }

