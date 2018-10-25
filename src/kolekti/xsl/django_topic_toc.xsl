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
  xmlns:kf="kolekti:extensions:functions:publication"
  exclude-result-prefixes="kf html"
  version="1.0">

  <xsl:output  method="xml"
               omit-xml-declaration="yes"
               indent="yes"/>

  <xsl:include href="django_conditions.xsl"/> 
  <xsl:include href="django_variables.xsl"/> 
  
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="comment()"/>
  <xsl:template match="/">
    <div>
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="html:html">
    <xsl:apply-templates select="html:body"/>
  </xsl:template>
  
  <xsl:template match="html:body">
    <xsl:apply-templates/>
  </xsl:template>
  
</xsl:stylesheet>
