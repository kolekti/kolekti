# -*- coding: utf-8 -*-
#
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


""" Publish View class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''



from kolekti.mvc.views.View import View
from lxml import etree as ET

class PublishView(View):
    def start(self):
        return "<div class='publish'>"

    def finalize(self):
        return "</div>"

    def start_section(self, classname):
        return "<div class='%s'>" %classname

    def chunck(self,msg):
        #should escape msg
        p=ET.Element("p")
        p.text=msg
        return ET.tostring(p)

    def title(self,msg):
        #should escape msg
        h=ET.Element("h3")
        h.text=msg
        return ET.tostring(h)
    
    def info(self, label, msg, attrib=None):
        p=ET.Element("p", attrib)
        sp=ET.SubElement(p, "span", {"class":"label"})
        sp.text=label
        sp=ET.SubElement(p, "span")
        sp.text=msg
        return ET.tostring(p)

    def profile(self,msg):
        d=ET.Element('div')
        d.set('class', 'title')
        spicon=ET.SubElement(d, 'span', {'class': 'ui-icon ui-icon-plusthick'})
        spicon.text=' '
        sp=ET.SubElement(d, 'span')
        sp.text="Publication profile : %s"%msg
        return ET.tostring(d)

    def success(self,msg):
        p=ET.Element("p")
        p.set('class','success')
        p.text=msg
        return ET.tostring(p)

    def error(self,msg):
        p=ET.Element("p")
        p.set('class','error')
        p.text=msg
        return ET.tostring(p)

    def details(self,msg):
        p=ET.Element("p")
        p.set('class','details')
        p.text=msg
        return ET.tostring(p)

    def labellink(self, ref, label, msg, attrib=None):
        p=ET.Element("p", attrib)
        sp=ET.SubElement(p, "span", {"class":"label"})
        sp.text=label
        sp=ET.SubElement(p, "span", {"class":"link"})
        a=ET.SubElement(sp, 'a', {'href':ref,'target':"_kolektipub"})
        a.text=msg
        return ET.tostring(p)

    def publink(self,name,label,ref):
        sp=ET.Element("span")
        sp.set('class','link')
        a=ET.SubElement(sp, 'a', {'href':ref,'target':"_kolektipub"})
        a.text='%s (%s)' %(name, label)
        return ET.tostring(sp)
