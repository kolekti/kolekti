# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import os
from zipfile import ZipFile
from lxml import etree as ET

import logging
logger = logging.getLogger(__name__)

import common


class OdsToXML(common.kolektiBase):
    def convert(self, odsfile, varpath = None, orient="cols", sync=True):
        logger.debug("ods to xml convert")
        # genere le fichier de variables à partir du openoffice
        xslt1=self.get_xsl("ods2xml-%s-pass1"%orient)
        xslt2=self.get_xsl("ods2xml-pass2")
        # ods = varpath + ".ods"
        with ZipFile(odsfile, 'r') as zip:
            foffx=zip.read('content.xml')
        vx=xslt1(ET.ElementTree(ET.XML(foffx)))
        vy=xslt2(vx)
        if varpath is not None:
            self.xwrite(vy, varpath, sync = sync)
        return vy

class XMLToOds(common.kolektiBase):
    def convert(self, odsfile, varpath, orient="cols"):
        logger.debug("xml to ods convert")
        xslt=self.get_xsl("xml2ods-%s"%orient)
        varxml = self.parse(varpath)
        tpl = os.path.join(self._appdir,"templates","variables.ods")
        with ZipFile(tpl,'r') as zipin:
            with ZipFile(odsfile,'w') as zipout:
                for f in zipin.infolist():
                    if f.filename == "content.xml":
                        data=unicode(xslt(varxml)).encode('utf-8')
                    else:
                        data = zipin.read(f.filename)
                    zipout.writestr(f, data)
        

class UpdateFromReleases(common.kolektiBase):
    def run(self, srclang):
        for release in self.list_directory('/releases'):
            for lang in self.list_directory('/releases/%s/sources/'%release):
                yield lang
                if lang == srclang or lang=='share':
                    continue
                top = '/releases/%s/sources/%s/variables'%(release, lang)
                l = len(self.getOsPath(top))
                for root, dirs, files in os.walk(self.getOsPath(top)):
                    for varfile in files:
                        path = '%s/%s'%(root[l+1:],varfile)
                        tpath = '/sources/%s/variables/%s'%(lang,path)
                        spath = '%s/%s'%(top,path)
                        if not self.exists(tpath):
                            yield 'create %s'%tpath 
                            self.copy_resource(spath, tpath)
                        else:
                            svars = self.parse(spath)
                            tvars = self.parse(tpath)
                            for varval in svars.xpath('/variables/variable/value'):
                                varcode = varval.getparent().get('code')
                                content = ET.tostring(varval.find("content"), encoding="utf-8")
                                tpath = '/variables/variable[@code="%s"]/value'%varcode
                                if len(tvars.xpath(tpath)):
                                    
                                    for crit in varval.iter('crit'):
                                        critname = crit.get('name')
                                        critval  = crit.get('value')
                                        tpath = tpath + '[crit[@name="%s" and @value="%s"]]'%(critname, critval)
                                        
                                    if len(tvars.xpath(tpath)):
                                        found = False
                                        for tcontent in tvars.xpath(tpath)[0].findall('content'):
                                            if ET.tostring(tcontent, encoding="utf-8") == content:
                                                found = True
                                        if not found:
                                            tvars.xpath(tpath)[0].append(varval.find("content"))
                                            
                                    else:
                                        tvar = tvars.xpath('/variables/variable[@code="%s"]'%varcode)[0]
                                        tvar.append(varval)
                                else:
                                    tvars.getroot().append(varval.getparent())
                                    
class AuditVariables(common.kolektiBase):
    def audit_varfile(self, lang, varpath):
        path = '/sources/%s/variables/%s'%(lang,varpath)
        svar = self.parse(path)
        translations = {} 
        for l in self.project_languages():
            ltop = '/sources/%s/variables'%l
            lpath = '%s/%s'%(ltop, varpath)
            translation = {}
            if self.exists(lpath):
                tvar = self.parse(lpath)
                varsdesc = {}
                for var in svar.xpath('/variables/variable'):
                    varcode = var.get('code')

                    if len(tvar.xpath('/variables/variable[@code="%s"]'%varcode)):                        
                        values = {}
                        for condvalue in var.iter('value'):
                            condition = {}
                            for crit in condvalue.iter('crit'):
                                critname = unicode(crit.get('name'))
                                condition.update({critname:crit.get('value')})
                            values[l].append({'condition':condition, 'content':condvalue.find('content')})
                        varsdesc.update({varcode:values})
                translations.update({l: varsdesc})
        return translations
    
    def audit_all(self, lang):
        top = '/sources/%s/variables'%lang
        l = len(self.getOsPath(top))
        for root, dirs, files in os.walk(self.getOsPath(top)):
            for varfile in files:
                path = '%s/%s'%(root[l+1:],varfile)
                yield {path:self.audit_varfile(lang, path)}
