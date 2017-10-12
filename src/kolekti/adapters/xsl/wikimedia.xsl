<?xml version="1.0" encoding="utf-8"?>
<!--
     kOLEKTi : a structural documentation generator
     Copyright (C) 2007-2017 Stéphane Bonhomme (stephane@exselt.com)

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
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:kfp="kolekti:extensions:functions:publication"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <xsl:param name="base_url"/>

  <xsl:key name="id" match="*[@id]" use="@id"/>
  
  <xsl:output  method="xml"
    indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="/">
    <div>
      <xsl:apply-templates select=".//h1[@id='firstHeading']"/>
      <xsl:apply-templates select=".//div[@id='mw-content-text']"/>
    </div>
  </xsl:template>
  
<!--
  <xsl:template match='img/@src'>
    <xsl:attribute name="src">
      <xsl:value-of select="kfp:image_wikimedia(string(.), $base_url)"/>
    </xsl:attribute>
  </xsl:template>
-->

  <xsl:template match='@id'>
    <xsl:if test="count(key('id',.)) &lt; 2">
      <xsl:copy/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="div[@id='toc']"/>
  
</xsl:stylesheet>
