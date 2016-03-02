# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

import sys
import os
import logging
from lxml import etree as ET

from kolekti.common import kolektiBase

class fixture(kolektiBase):
    def __init__(self, base):
        super(fixture, self).__init__(base)
        self._fixdir = os.path.dirname(os.path.realpath( __file__ ))

        
    def apply(self, number):
        fixdir = os.path.join(self._fixdir, str(number))
        for f in os.listdir(fixdir):
            if f == "job.xsl":
                xsl = ET.XSLT(ET.parse(os.path.join(fixdir,f)))
                for job in self.iterjobs:
                    jpath = job.get('path')
                    logging.info("fix %s"%jpath)
                    xjob = self.parse(jpath)
                    newjob = xsl(xjob)
                    self.xwrite(newjob, jpath)

