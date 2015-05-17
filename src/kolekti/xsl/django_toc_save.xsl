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
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"/>

  <xsl:template match="text()|@*">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:element namespace="http://www.w3.org/1999/xhtml" name="{local-name()}">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="head">
    <xsl:element namespace="http://www.w3.org/1999/xhtml" name="head">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="div[div/@id='collapseMeta']"/>

  <xsl:template match="/div">
    <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;
</xsl:text>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
	<title><xsl:value-of select="@data-kolekti-title"/></title>
	<xsl:for-each select="@*[starts-with(name(),'data-kolekti-meta')]">
	  <xsl:element namespace='http://www.w3.org/1999/xhtml' name="meta">
	    <xsl:attribute name="name">kolekti.<xsl:value-of select="substring(name(),19)"/></xsl:attribute>
	    <xsl:attribute name="content"><xsl:value-of select="."/></xsl:attribute>
	  </xsl:element>
	</xsl:for-each>
      </head>
      <body>
	<xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="a[@data-toggle='collapse']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="*[@data-ui='yes']"/>
  <xsl:template match="*[@data-ui='wrap']">
    <xsl:apply-templates/>
  </xsl:template>
</xsl:stylesheet>