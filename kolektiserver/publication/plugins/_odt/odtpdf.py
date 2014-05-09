# -*- coding: utf-8 -*-
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import uno
import pycurl

from os.path import dirname, exists
from unohelper import systemPathToFileUrl, absolutize
from com.sun.star.beans import PropertyValue
from com.sun.star.beans import NamedValue
from lxml import etree as ET

from kolekti.logger import dbgexc,debug

DEFAULT_PDF_PROPS = {"UseLosslessCompression": False,
                     "Quality": 90,
                     "ReduceImageResolution": False,
                     "MaxImageResolution": 300,
                     "SelectPdfVersion": 0,
                     "UseTaggedPDF": False,
                     "ExportFormFields": True,
                     "FormsType": 0,
                     "ExportBookmarks": True,
                     "ExportNotes": False,
                     "ExportNotesPages": False,
                     "IsSkipEmptyPages": False,
                     "IsAddStream": False,
                     "InitialView": 0,
                     "InitialPage": 1,
                     "Magnification": 0,
                     "Zoom": 100,
                     "PageLayout": 0,
                     "FirstPageOnLeft": False,
                     "ResizeWindowToInitialPage": False,
                     "CenterWindow": False,
                     "OpenInFullScreenMode": False,
                     "DisplayPDFDocumentTitle": True,
                     "HideViewerMenubar": False,
                     "HideViewerToolbar": False,
                     "HideViewerWindowControls": False,
                     "UseTransitionEffects": True,
                     "OpenBookmarkLevels": -1,
                     "ExportBookmarksToPDFDestination": False,
                     "ConvertOOoTargetToPDFTarget": False,
                     "ExportLinksRelativeFsys": False,
                     "PDFViewSelection": 0,
                     "Changes": 4,
                     "EnableCopyingOfContent": True,
                     "EnableTextAccessForAccessibilityTools": True}

class KolektiODTPDF:
    def __init__(self, publisher, conf):
        self.publisher=publisher
        self.oooserver=(conf.get('oooserver_host'), conf.get('oooserver_port'))
        if self.oooserver == ('',''):
            localContext = uno.getComponentContext()
            resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )
            ctx = resolver.resolve( "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext" )
            smgr = ctx.ServiceManager
            self._desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            self._config = smgr.createInstanceWithContext( "com.sun.star.configuration.ConfigurationProvider",ctx)
            self.dispatcher= smgr.createInstance("com.sun.star.frame.DispatchHelper")

    def exportDoc(self, filepath, pdfname, pdfproperties=""):
        if self.oooserver == ('',''):
            self.exportDocUno(filepath, pdfname, pdfproperties)
        else:
            self.exportDocServer(filepath, pdfname, pdfproperties)

    def exportDocServer(self, filepath, pdfname, pdfproperties):
        url = "http://%s:%s" %self.oooserver
        # Initialize pycurl
        c = pycurl.Curl()
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.URL, str(url))
        files = [("file", (c.FORM_FILE, filepath))]
        if exists(pdfproperties):
            files.append(("pdfproperties", (c.FORM_FILE, pdfproperties)))
        c.setopt(pycurl.HTTPPOST, files)
        pdfpath = "%s/%s" %(dirname(filepath),pdfname)
        # Set size of file to be uploaded.
        with open(pdfpath, 'w') as fp:
            c.setopt(pycurl.WRITEFUNCTION, fp.write)
            # Start transfer
            c.perform()
            c.close()

    def exportDocUno(self, filepath, pdfname, pdfproperties):
        debug("Export to pdf")
        #calculate the url
        self._cwd = systemPathToFileUrl(dirname(filepath))
        fileUrl = systemPathToFileUrl(filepath)
        inProps = PropertyValue("Hidden" , 0 , True, 0),
        
        #load the document
        debug("load")
        self._doc = self._desktop.loadComponentFromURL(fileUrl, '_blank', 0, inProps)
        self._doc.reformat()
        #try:
        #    self._exportToPDF('/tmp/nocreate')
        #except:
        #    pass
        f = self._doc.CurrentController.Frame
        debug("repaginate")
        self.dispatcher.executeDispatch(f, ".uno:Repaginate", "", 0, ())
        debug("update index")
        self._updateIndex()
        debug("read properties")
        self._readProperties(pdfproperties)
        debug("export")
        self._exportToPDF(pdfname)
        debug("dispose")
        self._doc.dispose()
        debug("end pdf generation")

    def _updateIndex(self):
        s=self._doc.DocumentIndexes
        try:
            for elt in s.getElementNames():
                idx = s.getByName(elt)
                if idx.ServiceName == u'com.sun.star.text.DocumentIndex' or idx.ServiceName == u'com.sun.star.text.ContentIndex':
                    idx.update()
        except:
            pass

    def _exportToPDF(self,pdfname):
        pdfUrl = absolutize(self._cwd, systemPathToFileUrl(pdfname) )
        filterProps=PropertyValue()
        filterProps.Name="FilterName"
        filterProps.Value="writer_pdf_Export"

        owProps=PropertyValue()
        owProps.Name="Overwrite"
        owProps.Value=True

        self._doc.storeToURL(pdfUrl,(filterProps,owProps))

    def _readProperties(self, pdfproperties):
        try:
            xPDFConfig = self._get_pdf_config_access()
            if exists(pdfproperties):
                pxml = ET.parse(pdfproperties)
            else:
                pxml = None
            for (pname, pvalue) in DEFAULT_PDF_PROPS.iteritems():
                if pxml is not None:
                    try:
                        prop = pxml.xpath("/properties/prop[@name='%s']" %pname)[0]
                        ptype = prop.get('type')
                        pvalue = prop.get('value')
                        if ptype == "int":
                            pvalue = int(pvalue)
                        elif ptype == "boolean":
                            pvalue = pvalue == "true"
                    except IndexError:
                        pass
                    except:
                        dbgexc()
                xPDFConfig.setPropertyValue(pname,pvalue)
            xPDFConfig.commitChanges()
        except:
            pass

    def _get_pdf_config_access(self):
        """Access the PDF configuration."""
        aNamedValue = NamedValue()
        aNamedValue.Name = "nodepath"
        aNamedValue.Value = "/org.openoffice.Office.Common/Filter/PDF/Export/"
        xConfigurationUpdateAccess = self._config.createInstanceWithArguments("com.sun.star.configuration.ConfigurationUpdateAccess", (aNamedValue,) )
        return xConfigurationUpdateAccess
