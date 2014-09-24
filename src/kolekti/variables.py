# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

from zipfile import ZipFile
import common
from lxml import etree as ET

class OdsToXML(common.kolektiBase):
    def convert(self,varpath, orient="cols"):
        # genere le fichier de variables à partir du openoffice
        xslt1=self.get_xsl("ods2xml-%s-pass1"%orient)
        xslt2=self.get_xsl("ods2xml-pass2")
        ods = varpath + ".ods"
        with ZipFile(self.getOsPath(ods), 'r') as zip:
            foffx=zip.read('content.xml')
        vx=xslt1(ET.ElementTree(ET.XML(foffx)))
        vy=xslt2(vx)
        self.xwrite(vy, varpath+".xml")
        return vy

class XMLToOds(common.kolektiBase):
    def convert(self,varpath, orient="cols"):
        xslt=self.get_xsl("xml2ods-%s"%orient)
        varxml = self.parse(varpath + ".xml")
        odsfile = varpath + ".xml"
        tpl = self.appfilename("templates","variables.ods")
        with ZipFile(tpl,'r') as zipin:
            with ZipFile(odsfile,'w') as zipout:
                for f in zipin.infolist():
                    if f.filename == "content.xml":
                        data=unicode(xslt(varxml)).encode('utf-8')
                    else:
                        data = zipin.read(f.filename)
                    zipout.writestr(f, data)
    
                

