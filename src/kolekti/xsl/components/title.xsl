<?xml version="1.0" encoding="utf-8"?>
<!--
    kOLEKTi : a structural documentation generator
    Copyright (C) 2007 Stéphane Bonhomme (stephane@exselt.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


-->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
    xmlns:html="http://www.w3.org/1999/xhtml"
    xmlns="http://www.w3.org/1999/xhtml" 
    exclude-result-prefixes="html"
    version="1.0">

  <xsl:template match="/libs">
    <libs>
      <css>
      </css>
      <scripts>
      </scripts>
    </libs>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topictitle">
    <xsl:apply-templates select =".//html:div[@class='kolekti-sparql-result-template']" mode="topictitle"/>
  </xsl:template>

  <xsl:template match = "html:h1|html:h2|html:h3|html:h4|html:h5|html:h6" mode="topictitle">
    <h4>
      <xsl:apply-templates mode ="topictitle"/>
    </h4>
  </xsl:template>

  
  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topicbody"/>
  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topicpanelinfo"/>
  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topicpanelaction"/>
  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topicpanelbutton"/>  
  <xsl:template match="html:div[@class='kolekti-component-title']" mode="topicpanelbody"/>

  
</xsl:stylesheet>
