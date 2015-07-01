# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import os
from zipfile import ZipFile
from lxml import etree as ET

import common


class OdsToXML(common.kolektiBase):
    def convert(self, odsfile, varpath = None, orient="cols"):
        # genere le fichier de variables à partir du openoffice
        xslt1=self.get_xsl("ods2xml-%s-pass1"%orient)
        xslt2=self.get_xsl("ods2xml-pass2")
        # ods = varpath + ".ods"
        with ZipFile(odsfile, 'r') as zip:
            foffx=zip.read('content.xml')
        vx=xslt1(ET.ElementTree(ET.XML(foffx)))
        vy=xslt2(vx)
        if varpath is not None:
            self.xwrite(vy, varpath)
        return vy

class XMLToOds(common.kolektiBase):
    def convert(self, odsfile, varpath, orient="cols"):
        xslt=self.get_xsl("xml2ods-%s"%orient)
        varxml = self.parse(varpath)
        tpl = os.path.join(self._appdir,"templates","variables.ods")
        with ZipFile(tpl,'r') as zipin:
            print odsfile
            with ZipFile(odsfile,'w') as zipout:
                for f in zipin.infolist():
                    if f.filename == "content.xml":
                        data=unicode(xslt(varxml)).encode('utf-8')
                    else:
                        data = zipin.read(f.filename)
                    zipout.writestr(f, data)
        
                

