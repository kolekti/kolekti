# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2017 Stéphane Bonhomme (stephane@exselt.com)

import os
from lxml import etree as ET
import urlparse
import urllib2
import logging
logger = logging.getLogger(__name__)

class AdapterWikimedia(object):

    html_parser = ET.HTMLParser()

    def __init__(self, *args, **kwargs):
        logger.debug("init extension wikimedia")
        self.images = set()
        super(AdapterWikimedia, self).__init__(*args, **kwargs)
        
    def gettopic_wikimedia(self, _, *args):
        logger.debug('gettopic wikimedia')
        url = args[0]
        relspec = args[1]
        logger.debug('url %s', url)
        try:
            page = urllib2.urlopen(url)
            source = ET.HTML(page.read())
            xslpath = os.path.join(self._appdir, 'adapters','xsl','wikimedia.xsl')
            xsldoc = ET.parse(xslpath)
            exts = [n for n in dir(self.__class__) if not(n.startswith('_'))]
            xsl = ET.XSLT(xsldoc, extensions=ET.Extension(self, exts, ns = "kolekti:extensions:functions:publication"))
            res = xsl(source)
            try:
                wmfilter = relspec.split(':')[2]
            except IndexError:
                wmfilter = None
            if wmfilter is not None:
                try:
                    s = self.get_xsl(wmfilter, xsldir = "/kolekti/import-stylesheets/mediawiki")
                    res = s(res)
                except:
                    logger.exception('could not apply mediawiki filter')
                    self.log_xsl(s.error_log)                
        except:
            logger.exception('wikimedia failed')

        for img in res.xpath('//img'):
            newsrc = self.image_wikimedia(None, img.get('src'), url)
            img.set('src', newsrc)
        return res.getroot()

    def image_wikimedia(self, _, *args):
        try:
            src = args[0]
            base = args[1]
            name = src.split('/')[-1]
            newsrc = '/sources/share/pictures/mediawiki/'+name
            imgurl = urlparse.urljoin(base, src)
            if not imgurl in self.images:
                logger.debug('get image wikimedia %s', imgurl)
                self.images.add(imgurl)
                i = urllib2.urlopen(imgurl)
                self.makedirs("/sources/share/pictures/mediawiki/")
                self.write(i.read(),newsrc, mode="wb", sync=False)
            return newsrc
        except:
            logger.exception('wikimedia image failed')
            return "/error"
