# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
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




""" properties controller"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

# python import
from lxml import etree as ET
import re
import traceback
import urllib2

# kolekti imports
from kolekti.http import statuscodes as HS
from kolekti.exceptions import exceptions as EXC


# parent classes
from kolekti.mvc.controllers.Controller import Controller

class PropertiesController(Controller):

    def ctrOPTIONS(self):
        self.http.response.setHeader("Allow", "OPTIONS,PROPFIND")
        self.http.response.setHeader("DAV", "1")

    def ctrPROPFIND(self):
        # self.response=ET.XML("{DAV:}multistatus")
        # should be better, but don't know how to set the nsmap for output
        # for generating D: prefixes instead of ns0:
        self.response = ET.XML('<D:multistatus xmlns:D="DAV:"/>')

        depth = self.http.headers.get('DEPTH','infinity')

        # Horrible hack for "DAV:" namespace handling
        propq = ET.fromstring(self.http.body)
        if self.model.isCollection(self.http.path):
            if depth == "0":
                self._props(self.http.path, propq)
            elif depth == "1":
                self._props(self.http.path, propq)
                for f in self.model.listCollection(self.http.path):
                    if self.http.path[-1]=='/':
                        childpath=self.http.path+f
                    else:
                        childpath=self.http.path+'/'+f   
                    self._props(childpath, propq)
            elif depth == "infinity":
                self._props(self.http.path, propq)
                self.__recursprops(self.http.path, propq)
            else:
                raise Exception
#        elif self.model.isResource(self.http.path): #ressource
        else:
            self._props(self.http.path, propq)
#        else:
#            raise EXC.NotFound

        body = ET.tostring(self.response)

        # Format response with xsl
        if self.http.headers.get('KOLEKTIFORCEVIEW', None):
            body = self.view.format_properties(body)

        raise EXC.Multistatus, body

    def ctrPROPPATCH(self):
        self.response = ET.XML('<D:multistatus xmlns:D="DAV:"/>')
        r = ET.SubElement(self.response, "{DAV:}response");
        ruri = ET.SubElement(r, "{DAV:}href")
        ruri.text = self.http.path
        propq = ET.fromstring(self.http.body)
        pcat = {}
        pcat[200]=self.__create_propstat_element(r,200)

        self.model.proppatch_prepare(self.http.path)

        # update properties
        for p in propq.xpath("/D:propertyupdate/D:set/D:prop/*", namespaces={'D':'DAV:'}):
            try:
                m = re.match(r'{([^}]+)}(.*)', p.tag)
                (ns, propname) = m.groups()
                try:
                    # try to set xml property
                    pval = self.model.setpropval(self.http.path, propname, ns,p[0])
                except IndexError:
                    # sets text property
                    pval = self.model.setpropval(self.http.path, propname, ns,p.text)
                pcat[200].append(pval)

            except EXC.Error, (ec, dd):
                if not pcat.has_key(ec):
                    pcat[ec] = self.__create_propstat_element(r,ec,dd)
                ET.SubElement(pcat[ec], "{%s}%s" % (ns, propname))

            except:
                if not pcat.has_key(500):
                    pcat[500] = self.__create_propstat_element(r,500,traceback.format_exc())
                ET.SubElement(pcat[500], "{%s}%s" % (ns, propname))

        # Remove properties
        for p in  propq.xpath("/D:propertyupdate/D:remove/D:prop/*", namespaces={'D':'DAV:'}):
            try:
                m = re.match(r'{([^}]+)}(.*)', p.tag)
                (ns, propname) = m.groups()
                self.model.delprop(self.http.path, propname, ns)

            except EXC.Error, (ec, dd):
                if not pcat.has_key(ec):
                    pcat[ec] = self.__create_propstat_element(r,ec,dd)
                ET.SubElement(pcat[ec], "{%s}%s" % (ns, propname))
            except:
                if not pcat.has_key(500):
                    pcat[500] = self.__create_propstat_element(r,500,traceback.format_exc())
                ET.SubElement(pcat[500], "{%s}%s" % (ns, propname))

        # there was an error : set all ok (200) to Failed dependancy (424), and rollback model
        if pcat.keys() != [200]:
            pp=pcat[200].getparent()
            status=pp.find("{DAV:}status")
            status.text="HTTP/1.1 409 Conflict"
            self.model.proppatch_rollback()
        # all went ok, commit model
        else :
            self.model.proppatch_commit()


        body = ET.tostring(self.response)
        # Format response with xsl
        if self.http.headers.get('KOLEKTIFORCEVIEW', None):
            body = self.view.format_properties(body)

        raise EXC.Multistatus, body

    def __create_propstat_element(self, resp, code, error=None):
        ps = ET.SubElement(resp, "{DAV:}propstat")
        prop = ET.SubElement(ps, "{DAV:}prop")
        s = ET.SubElement(ps, "{DAV:}status")
        s.text = "HTTP/1.1 %d %s"%(code, HS.STATUS_CODES[code])
        if not error is None:
            s = ET.SubElement(ps, "{DAV:}error")
            s.text = error
        return prop

    def _props(self, path, pfreq):
        r = ET.SubElement(self.response, "{DAV:}response");
        ruri = ET.SubElement(r, "{DAV:}href")
        ruri.text = urllib2.quote(path.encode('utf-8'))
        pcat = {}

        pcat[200]=self.__create_propstat_element(r,200)

        # propname request : returns the list of all supported properties
        if pfreq.xpath("/D:propfind/D:propname", namespaces={'D':'DAV:'}):
            try:
                for p in self.model.getproplist(path):
                    ET.SubElement(pcat[200], "{%s}%s" % p)
            except EXC.Error, (ec, dd):
                self.__create_propstat_element(r,ec,dd)

        # allprop request : returns all props with value
        elif pfreq.xpath("/D:propfind/D:allprop", namespaces={'D':'DAV:'}):
            for (ns, propname) in self.model.getproplist(path):
                try:
                    p = self.model.getpropval(path, propname, ns)
                    pcat[200].append(p)
                    propsok=True

                except EXC.Error, (ec, dd):
                    if not pcat.has_key(ec):
                        pcat[ec] = self.__create_propstat_element(r,ec,dd)
                    ET.SubElement(pcat[ec], "{%s}%s" % (ns, propname))
                except:
                    if not pcat.has_key(500):
                        pcat[500] = self.__create_propstat_element(r,500,traceback.format_exc())
                    ET.SubElement(pcat[500], "{%s}%s" % (ns, propname))
        elif pfreq.xpath("/D:propfind/D:noprop", namespaces={'D':'DAV:'}):
            pass
        # prop request : returns some props with value
        else:
            lp = pfreq.xpath("/D:propfind/D:prop/*", namespaces={'D':'DAV:'})
            if len(lp)==0:
                raise EXC.BadRequest
            for p in lp:
                try:
                    m = re.match(r'{([^}]+)}(.*)', p.tag)
                    (ns, propname) = m.groups()
                    pval = self.model.getpropval(path, propname, ns)
                    pcat[200].append(pval)

                except EXC.Error, (ec, dd):
                    if not pcat.has_key(ec):
                        pcat[ec] = self.__create_propstat_element(r,ec,dd)
                    ET.SubElement(pcat[ec], "{%s}%s" % (ns, propname))
                except:
                    if not pcat.has_key(500):
                        pcat[500] = self.__create_propstat_element(r,500,traceback.format_exc())
                    ET.SubElement(pcat[500], "{%s}%s" % (ns, propname))

        if len(pcat[200])==0:
            r.remove(r.find('{DAV:}propstat'))

    def __recursprops(self, resid, propq):
        for f in self.model.listCollection(resid):
            if resid[-1]==u'/':
                childresid=resid+f
            else:
                childresid=resid+u'/'+f
            self._props(childresid, propq)
            if self.model.isCollection(childresid):
               self.__recursprops(childresid, propq)
