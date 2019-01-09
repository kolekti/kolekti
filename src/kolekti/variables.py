# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import os
import copy
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
        

class UpdateFromRelease(common.kolektiBase):
    def run(self, srclang, release):
        #        for release in  ['A184_20180507']:
        if not self.exists('/releases/%s/release_info.json'%release):
            return
        for lang in self.list_directory('/releases/%s/sources/'%release):
            if lang == srclang or lang=='share':
                continue
            top = '/releases/%s/sources/%s/variables'%(release, lang)
            l = len(self.getOsPath(top))
            for root, dirs, files in os.walk(self.getOsPath(top)):
                for varfile in files:
                    if not os.path.splitext(varfile)[1] == ".xml":
                        continue
                    path = '%s/%s'%(root[l+1:],varfile)
                    tpath = '/sources/%s/variables/%s'%(lang,path)
                    spath = '%s/%s'%(top,path)
                    yield tpath
                    if not self.exists(tpath):
                        self.makedirs(self.dirname(tpath))
                        svars = self.parse(spath)
                        for content in svars.xpath('//content'):
                            content.set('release-origin',release)
                        self.xwrite(svars, tpath)
                    else:
                        file_changed = False
                        svars = self.parse(spath)
                        tvars = self.parse(tpath)
                        for varval in svars.xpath('/variables/variable/value'):
                            varcode = varval.getparent().get('code')
                            content = ET.tostring(varval.find("content"), encoding="utf-8")
                            txpath = '/variables/variable[@code="%s"]/value'%varcode
                            if len(tvars.xpath(txpath)):
                                for crit in varval.iter('crit'):
                                    critname = crit.get('name')
                                    critval  = crit.get('value')
                                    txpath = txpath + '[crit[@name="%s" and @value="%s"]]'%(critname, critval)
                                matched = tvars.xpath(txpath) 
                                if len(matched):
                                    found = False
                                    for tcontent_elt in matched[0].findall('content'):
                                        tcontent_elt=copy.deepcopy(tcontent_elt)
                                        try:
                                            tcontent_elt.attrib.pop('release-origin')
                                        except KeyError:
                                            pass
                                        tcontent = ET.tostring(tcontent_elt, encoding="utf-8") 
                                        if tcontent == content:
                                            found = True
                                    if not found:
                                        content = varval.find("content")
                                        content.set('release-origin',release)
                                        matched[0].append(varval.find("content"))
                                        file_changed = True
                                else:
                                    tvar = tvars.xpath('/variables/variable[@code="%s"]'%varcode)[0]
                                    tvar.append(varval)
                                    file_changed = True
                            else:
                                tvars.getroot().append(varval.getparent())
                                file_changed = True
                                    
                        if file_changed:
                            self.xwrite(tvars, tpath)


                            
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


    def audit_list_translation_langs (self, srclang):
        return [l for l in self.list_directory('/sources') if not l  in ['share',srclang]]

    def audit_source_translations(self, srclang):
        trlangs = self.audit_list_translation_langs(srclang)
        
        top = '/sources/%s/variables'%srclang
        l = len(self.getOsPath(top))
#        return []
        return [{'CoverTitles.xml':self.audit_varfile_source_translations('CoverTitles.xml', srclang, trlangs)}]
    
        # for root, dirs, files in os.walk(self.getOsPath(top)):
        #     for varfile in files:
        #         path = '%s/%s'%(root[l+1:],varfile)
        #         yield {path:self.audit_varfile_source_translations(path, srclang, trlangs)}

    def audit_varfile_source_translations(self, path, srclang, trlangs):
        xvars = {}
        xsrc = self.parse('/sources/%s/variables/%s'%(srclang, path))
        for trlang in trlangs:
            try:
                xv = self.parse('/sources/%s/variables/%s'%(trlang, path))
            except:
                xv = None
            xvars.update({trlang:xv})
        logger.debug(trlangs)
        double = []
        res = {}
        file_warning = False
        for variable in xsrc.xpath('//variable'):
            varinfo = {}
            varcode = variable.get('code')
            warning = False
            txpath = '/variables/variable[@code="%s"]/value'%varcode
            for varval in variable.findall('value'):
                valinfo = {}
                critspec = ""
                for crit in varval.iter('crit'):
                    critname = crit.get('name')
                    critval  = crit.get('value')
                    critspec = critspec + "%s=%s;"%(critname, critval) 
                    txpath = txpath + '[crit[@name="%s" and @value="%s"]]'%(critname, critval)
                
                for lang, tvars in xvars.iteritems():
                    logger.debug("%s  %s %s %s"%(path, varcode, critspec, lang))                    
                    if tvars is not None:
                        matched_elts = tvars.xpath(txpath)
                        if len(matched_elts) >1:
                            double.append('%s:%s'%(varcode, scriptspec))
                            warning = True
                            rescontent = {}
                            for matched in matched_elts:
                                contents = matched.findall('content')
                                if len(contents)>1:
                                    warning = True
                                rescontent.append(contents)
                            valinfo.update({lang:rescontents})
                                
                        elif len(matched_elts) == 0:
                            warning = True
                            valinfo.update({lang:None})
                            
                        else:
                            matched = matched_elts[0]
                            contents = matched.findall('content')
                            if len(contents)>1:
                                warning = True
                            valinfo.update({lang:[contents]})
                    else:
                        valinfo.update({lang:[]})
                        warning = True
                        
                varinfo.update({critspec:valinfo})
            res.update({varcode:(varinfo, warning)})
            file_warning = file_warning or warning
        return res, double, file_warning
