# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import os
import re
from zipfile import ZipFile
from lxml import etree as ET
import time
import traceback
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import common

def repl(s):
    if s is None:
        return ""
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return s


class Templater(common.kolektiBase):
    __nsods  = {"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0" ,
                "table" : "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                "text"  : "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
                }
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('lang'):
            self._lang = kwargs.get('lang')
            kwargs.pop('lang')
        super(Templater, self).__init__(*args, **kwargs)

    def generate(self, topictpl, odsfile):
        vars = set()
        p = self.getOsPath(topictpl)
        with open(p) as f:
            for line in f.readlines():
                for match in re.findall('\{\s*\w+\s*\}',line):
                    t = match[1:-1].strip()
                    if t != 'topicname':
                        vars.add(match[1:-1].strip())
                     
        tpl = os.path.join(self._appdir,"templates","import.ods")
        with ZipFile(tpl,'r') as zipin:
            with ZipFile(odsfile,'w') as zipout:
                for f in zipin.infolist():
                    data = zipin.read(f.filename)
                    if f.filename == "content.xml":                        
                        data=self.gen_cols(data, vars, self.basename(topictpl))
                    zipout.writestr(f, data)

    def gen_cols(self, data, vars, topictpl):
        x = ET.XML(data)
        n = 0
        print x.xpath('//table:table[1]//table:table-row[1]//table:table-cell',namespaces=self.__nsods)
        t = x.xpath('//table:table[1]//table:table-row[1]//table:table-cell[2]/text:p',namespaces=self.__nsods)[0]
        t.text = topictpl
        
        print "variables", vars
        for var in vars:
            print var
            n = n+1
            t = x.xpath('//table:table[@table:name="Ecrans"]',namespaces=self.__nsods)[0]
            tc = ET.Element("{%s}table-column"%self.__nsods["table"])
            tc.set("{%s}style-name"%self.__nsods["table"],"co3")
            tc.set("{%s}default-cell-style-name"%self.__nsods["table"],"Default")
            t.insert(n, tc)
            
            tc = ET.Element("{%s}table-cell"%self.__nsods["table"])
            tc.set("{%s}style-name"%self.__nsods["table"],"ce1")
            p = ET.SubElement(tc,'{%s}p'%self.__nsods["text"])
            p.text = var
            tc.set("{%s}value-type"%self.__nsods["office"],"string")
            t.find('{%s}table-row'%self.__nsods["table"]).append(tc)
        print ET.tostring(t,pretty_print=True)
        return ET.tostring(x)
            
    
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
        try:
            with ZipFile(odsfile, 'r') as zip:
                foffx=zip.read('content.xml')
                xcontent=ET.XML(foffx)
        except:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : fichier ods invalide",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
        
        if len(xcontent.xpath('/office:document-content/office:body/office:spreadsheet/table:table', namespaces=self.__nsods)) < 2:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : onglets non trouvés",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
        
        conflines = self._ods_getlines(xcontent.xpath('/office:document-content/office:body/office:spreadsheet/table:table[1]', namespaces=self.__nsods)[0])
            
        try:
            template = conflines[0][1]
            path     = conflines[1][1]
            tocpath  = conflines[2][1]
            job      = conflines[3][1]
        except IndexError:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : paramètres non spécifiés",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
        
        lines = self._ods_getlines(xcontent.xpath('/office:document-content/office:body/office:spreadsheet/table:table[2]',namespaces=self.__nsods)[0])
        if len(lines) == 0:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : aucun topic défini",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
        
        for e in  self._generate_topics(lines, template, path):
            yield e
    
        for e in  self._generate_toc(lines, tocpath, path, job):
            yield e
    
    def _ods_getlines(self, xtable):
        lines = []
        for line in xtable.xpath('table:table-row',namespaces=self.__nsods):
            l = []
            for col in line.xpath('table:table-cell',namespaces=self.__nsods):
                l.append(col.xpath('string(.)'))
            lines.append(l)

        return lines
                
    def importXlsx (self, xlsxfile):
        
        try:
            dz = ZipFile(xlsxfile,'r')

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
        except:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : fichier xlsx invalide",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
            
        try:
            template = conflines[0][1]
            path     = conflines[1][1]
            tocpath  = conflines[2][1]
            job      = conflines[3][1]
        except IndexError:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : parametres non spécifiés",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return
        try:
            dzf = dz.open('xl/worksheets/sheet2.xml', 'rU')
            dx = ET.XML(dzf.read())
            lines = self._xslx_getlines(dx, strings)
            if len(lines) == 0:
                yield {
                    'event':'error',
                    'msg':"Erreur lors de l'import : aucun topic défini",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                    }
                return
        except:
            yield {
                'event':'error',
                'msg':"Erreur lors de l'import : fichier xlsx invalide (topics)",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }
            return


        for e in self._generate_topics(lines, template, path):
            yield e
    
        for e in  self._generate_toc(lines, tocpath, path, job):
            yield e
    
    def _xslx_getlines(self, xsheet, strings):
        coln = [chr(v + 65) for v in range(26)] + ['A' + chr(v + 65) for v in range(26)]
        lines = []
        for line in xsheet.xpath('/n:worksheet/n:sheetData/n:row',namespaces=self.__nsxlsx):
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


    def _generate_toc(self, lines, path, topicspath, job):
        outpath = '/sources/'+ self._lang + '/tocs/' + path
        topicspath = '/sources/'+ self._lang + '/topics/' + topicspath
        self.makedirs(self.dirname(outpath), sync=True)
        
        buf = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>imported toc</title>
    <meta name="DC.title" content="imported toc"/>
    <meta name="kolekti.job" content="%s"/>
    <meta name="kolekti.jobpath" content="/kolekti/publication-parameters/%s.xml"/>
    <meta name="kolekti.pubdir" content=""/>
  </head>
  <body><a rel="kolekti:toc"/>
"""%(job, job)
        nl = 0
        for l in lines[1:]:
            nl +=1
            topicfile = l[0]
            if topicfile is not None and len(topicfile):
                buf += """<a href="%s/%s" rel="kolekti:topic"/>"""%(topicspath, topicfile)
        buf += "</body></html>"
        
        self.write(buf, outpath)
        yield { 'event':'result',
                'file':outpath,
                'url':'/tocs/edit/?toc='+outpath,
                'time':time.time(),
                }

    def _generate_topics(self, lines, template, path):

        outpath = '/sources/'+ self._lang + '/topics/' + path + "/"
        tplpath = '/sources/'+ self._lang + '/templates/' + template
        
        self.makedirs(outpath, sync=True)
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
                if topicfile is not None and len(topicfile):
                    buf = ""
                    for l in self.substitute(tplpath, **sheet_params):
                        buf += l
                    self.write(buf, outpath + topicfile)
                    yield { 'event':'result',
                            'file':outpath + topicfile,
                            'url':outpath + topicfile,
                            'time':time.time(),
                }
# TODO : if line is not empty
#                else:
#                    yield {
#                        'event':'error',
#                        'msg':"Erreur lors de l'import : fichier module non spécifié",
#                        'stacktrace':traceback.format_exc(),
#                        'time':time.time(),
#                        }

            except:
                print traceback.format_exc()
                yield {
                        'event':'error',
                        'msg':"Erreur lors de l'import :impossible de créer les modules",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }

