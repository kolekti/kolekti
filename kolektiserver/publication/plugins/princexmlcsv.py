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


import pluginBase
import os
import re
import pyPdf
import time

from lxml import etree as ET

from kolekti.logger import dbgexc,debug

htmlns="http://www.w3.org/1999/xhtml"

class plugin(pluginBase.plugin):
    def postpub(self):
        """
        main publication function
        """

        pubpath = self.publisher.model.pubpath
        localdocument = self.publisher.document

        for media in localdocument.xpath("//h:img[@src]|//h:embed[@src]", namespaces={'h':'http://www.w3.org/1999/xhtml'}):
            localsrc = self.publisher.model.abstractIO.local2unicode(self.publisher.model.url2local(str(media.get('src'))))
            media.set('src', localsrc)
        
        self.publisher.model.pubsavepivot(ET.tostring(localdocument, xml_declaration=True, encoding="UTF-8"),
                                                      '%s-local.xml'%self.publisher.pivname,
                                                      False,
                                                      profilename=self.publisher.pivname)

        localpivfile = os.path.join(pubpath.decode(self.LOCAL_ENCODING), u"_pivots", u"%s-local.xml"%self.publisher.pivname)
        css = u'/'.join((pubpath.decode(self.LOCAL_ENCODING), self.label, "css", self.params.get('css', 'default.css')))
        pdf = u'/'.join((pubpath.decode(self.LOCAL_ENCODING), self.label, self.publisher.docname))

        try:
            os.mkdir(os.path.join(pubpath,self.label.encode(self.LOCAL_ENCODING)))
        except:
            pass

        for msg in self.generate_pdf(localpivfile, css, pdf):
            yield msg

        for msg in self.generate_csv(pdf):
            yield msg

    

    def generate_pdf(self, piv, css, pdf):
        ''' Generate pdf file with princeXML '''
        cmd = 'prince "%s" -s "%s" -o "%s"' %(piv, css, pdf)
        cmd = cmd.encode(self.LOCAL_ENCODING)
        debug(cmd)

        import subprocess
        (child_stdin, child_stdout, child_stde) = subprocess.os.popen3(cmd)
        child_stdin.close()
        err = child_stde.read()
        out = child_stdout.read()
        err = err.decode(self.LOCAL_ENCODING)
        out = out.decode(self.LOCAL_ENCODING)

        if not re.search(u'error', err) is None:
            yield(self.publisher.view.error(self.publisher.setmessage(u"[0074]Erreur lors de l'exécution de la commande : %(cmd)s (%(error)s)", {'cmd': cmd.decode(self.LOCAL_ENCODING), 'error': err})))
            raise Exception, 'Failed to execute cmd'
        else:
            outfile = '%s.pdf' %self.publisher.docname
            outref = '/'.join((self.publisher.model.pubdirurl, self.label, '%s.pdf' %self.publisher.docname))
            yield (self.publisher.view.publink(outfile,
                                            self.label,
                                            outref))

    def generate_csv(self, pdf):
        ''' Generate csv file '''
        # CodeArticle             &radical_ref + CODE ZONE + "-" + LANG
        # NoPlan                  CodeNotice
        # IndicePlan              &indice
        # DateRevPlan             Date de publication
        # Nb Pages Notice         Information extraite du pdf
        cart = "%s%s%s-%s" %(self.publisher.replace_strvar('[var RDI:radical_ref]'),
                                 self.publisher.critdict.get('Code', ''),
                                 self.publisher.critdict.get('ZONE', ''),
                                 self.publisher.model.lang)
        nop = self.publisher.critdict.get('CodeNotice', '')
        indp = self.publisher.replace_strvar('[var RDI:indice]')
        drevp = time.strftime("%d/%m/%Y", time.gmtime(self.publisher.model.pubtime))

        pdfpath = self.publisher.model.abstractIO.unicode2local(pdf)
        fpdf = open(pdfpath)
        rpdf = pyPdf.PdfFileReader(fpdf)
        nbpage = str(rpdf.getNumPages())
        fpdf.close()
        buf = ";".join((cart, nop, indp, drevp, nbpage))

        try:
            csvpath = os.path.join(self.publisher.model.pubpath.rsplit(os.sep, 3)[0], "%s.csv" %self.publisher.model.pivname.encode(self.LOCAL_ENCODING))
            if not os.path.exists(csvpath):
                buf = "CodeArticle;NoPlan;IndicePlan;DateRevPlan;NbPages\r\n"+buf
            fpcsv = open(csvpath, 'a')
            fpcsv.write('%s\r\n' %buf)
            fpcsv.close()
            puburl = self.publisher.model.pubdirurl.rsplit('/', 3)[0]
            outref = '/'.join((puburl, '%s.csv' %self.publisher.model.pivname))
            yield (self.publisher.view.publink('%s.csv' %self.publisher.model.pivname,
                                            self.label,
                                            outref))
        except:
            yield self.publisher.view.error(self.publisher.setmessage(u"[0075]Erreur lors de la génération du fichier csv : %(filename)s.csv", {'filename': self.publisher.model.pivname}))
            raise Exception, 'Failed to generate csv file'
