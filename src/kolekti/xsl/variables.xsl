<?xml version="1.0" encoding="ISO-8859-1"?>
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
  xmlns:kfp="kolekti:extensions:functions:publication"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

 
  
  <xsl:template name="getvariable">
    <xsl:param name="varfile"/>
    <xsl:param name="varname"/>

    <!-- on calcul la valeur de la variable -->
    <xsl:variable name="res" select="kfp:variable($varfile,$varname)"/>
  
    <xsl:choose>
      <xsl:when test="$res!=''">
        <xsl:apply-templates select="$res/node()" mode="varcontent"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>[?? Undefined </xsl:text>
        <xsl:value-of select="$varfile"/>
        <xsl:text>:</xsl:text>
        <xsl:value-of select="$varname"/>
        <xsl:text>]</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="*" mode="varcontent">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
<!-- substitution des éléments var par la valeur d'un texte automatique -->

  <xsl:template match="html:var">
    <xsl:choose>
      <xsl:when test="contains(@class,':')">
	<xsl:call-template name="getvariable">
          <xsl:with-param name="varfile" select="substring-before(@class,':')"/>
          <xsl:with-param name="varname" select="substring-after(@class,':')"/>
	</xsl:call-template>
      </xsl:when>

      <xsl:otherwise>
        <xsl:variable name="res" select="kfp:replace_criteria(concat('{',@class,'}'))"/>
        <xsl:value-of select="$res"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="/html:html/html:head/html:title">
    <xsl:copy>
      <xsl:value-of select='kfp:replace_strvar(string(.))'/>
    </xsl:copy>
  </xsl:template>
    


  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
