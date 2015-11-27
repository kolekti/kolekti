# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import logging
from lxml import etree as ET

from common import kolektiBase, XSLExtensions, LOCAL_ENCODING

DIAG_WARNING = 0
DIAG_ERROR = 1

class DiagnosticError(Exception):
    pass

class DiagnosticReport(object):
    def __init__(self):
        self.warnings = {}
        self.errors = {}

    def warning(self, ref, msg):
        pass

    def error(self, ref, msg):
        pass

    def xml(self):
        report = ET.XML("<report/>")
        for warning in self.warnings:
            warning_element = ET.SubElement(report,"warning")
            warning_element.set('ref', warning.ref)
            warning_element.text = warning.message
        return ET.tostring(report, encoding="utf-8")

class Diagnostic(kolektiBase):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}

    def __init__(self, *args, **kwargs):
        super(Diagnostic, self).__init__(*args, **kwargs)
        self.report = DiagnosticReport()

        # check configuration
        self._diag_config()
        

        
    def _diag_config(self):
        logging.debug("checking project config") 
        try:
            self.settings = self.parse('/kolekti/settings.xml')
        except:
            logging.error("/kolekti/settings", "Unable to parse settings file") 
            raise DiagnosticError

        schema = ET.XMLSchema(ET.parse(os.path.join(self._appdir, 'schemas', 'settings.xsd')))
        if not schema.validate(self.settings):
            logging.error('invalid settings structure')
            for e in schema.error_log:
                logging.error(e.message)
            raise DiagnosticError

                
    def diag_toc(self, toc):
        logging.debug("checking toc") 
        try:
            xtoc = self.parse(toc)
        except:
            logging.error('Unable to parse toc '+toc)
            raise DiagnosticError
        
        job = xtoc.xpath('/h:html/h:head/h:meta[@name="kolekti.job"])', namespaces=self.nsmap)
        if len(job !=1):
            logging.error('Unable to find a job reference in toc')
            raise DiagnosticError
        self.diag_job(job)

                

    def diag_job(self, job):
        logging.debug("checking job") 
        try:
            xjob = self.parse(job)
        except:
            logging.error('Unable to parse job '+job)
            raise DiagnosticError

        schema = ET.XMLSchema(ET.parse(os.path.join(self._appdir, 'schemas', 'job.xsd')))
        if not schema.validate(xjob):
            logging.error('invalid job structure')
            for e in schema.error_log:
                logging.error(e.message)
            raise DiagnosticError

        # check definition of criteria names and values are present in setting
        criteria = xjob.xpath('//criterion')
        for criterion in criteria:
            name = criterion.get('name')
            value = criterion.get('value',None)
            if not len(self.settings.xpath('/settings/criterion[@code="%s"]'%name)):
                logging.warn('Criterion %s undefined, will be ignored'%name)
            else:
                if not len(self.settings.xpath('/settings/criterion[@code="%s"]/value[.="%s"]'%(name,value))):
                    logging.warn('Criterion %s does not define value %s'%(name, value))
                    
        # check that scripts referenced in job exists in scripts definitions
        scripts = xjob.xpath('//script')
        scriptdefs = self.get_scripts_def()
        for script in scripts:
            name = script.get('name')
            if not len(scriptdefs.xpath('/scripts/pubscript/[@id="%s"]'%name)):
                logging.error('Script defintion %s not found')
        
            # check parameters existence

        # check parameter values
        
        # check usage af variable fields in pathes / labels


    def diag_topic(self, topic, profile=None):
        logging.debug("checking topic %s"%topic)
        # parse topic
        xtopic = self.parse(topic)
        
        # validate topic

        # check conditions expressions
        condelts = topic.xpath('//*[contains(@class,"=")]')
        for condelt in condelts:
            cond = condelt.get('class')
            condparser = ConditionsParser(cond)
            try:
                condparser.validate(self.settings)
            except ConditionParseError:
                logging.warning("condition could not be parsed: %s",(cond,))
            except ConditionError:
                logging.warning("condition invalid: %s",(cond,))

            # if needed apply filter
            if profile is not None:
                xcriteria = profile.find('criteria')
                if not condparser.evaluate(xcriteria):
                    condelt.getparent().unlink(condelt)
                     
                    
            # check variables usage
            for varelt in topic.xpath('//h:var',namespaces=self.nsmap):
                varexp = varelt.get('class')
                self.check_var_string(varexp, profile)
                
            # check images
            for imgelt in topic.xpath('//h:img',namespaces=self.nsmap):
                ref = imgelt.get('src')
                ref = self.substitute_criteria(ref, profile)
                imgfile = self.getOsPath(ref)
                if not os.path.exists(imgfile):
                    logging.error('missing illustration %s',ref)
                    
            # check links
            for linkelt in topic.xpath('//h:a',namespaces=self.nsmap):
                ref = linkelt.get('src')
                topicfile = self.getOsPath(ref)
                if not os.path.exists(topicfile):
                    logging.error('broken link to %s',ref)

    def check_var_string(self, string, profile):
        for varexp in re.findall('{[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+}', string):
            varexp = varexp[1:-1]
            if ":" in varexp:
                self.check_var_expr(varexp, profile)
            else:
                self.check_criteria(varexp)

    def check_criteria(self, string):
        if not len(self.settings.xpath('/settings/criterion[@code="%s"]'%name)):
            logging.warn('Criterion %s undefined'%name)
                
    def check_var_exp(self, string, profile):
        sheet, variable = string.split(':')
        variable_value(sheet, variable, profile)
            
    def diag_project(self):
        # process all tocs
        for toc in self.itertocs:
            self.diag_toc(toc)



