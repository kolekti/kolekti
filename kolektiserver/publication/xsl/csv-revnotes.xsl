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
  xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns:kfp="kolekti:extensions:functions:publication"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <xsl:output  method="text" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:variable name="revisions" select="kfp:modules_history()" />

  <xsl:template match="/">
    <xsl:variable name="modulespath" select="//html:div[@class='module']/html:div[@class='moduleinfo'][html:p/html:span[@class='infolabel']/text() = 'source']/html:p/html:span[@class='infovalue']/html:a" />
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:NomMod]')" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:Location]')" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:RevInd]')" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:Author]')" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:Date]')" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="kfp:replace_strvar('[var kolektitext:Comments]')" />
    <xsl:text>;&#10;</xsl:text>

    <xsl:apply-templates select="$revisions/revnotes[$modulespath/text() = @path]" mode="revnotes"/>
  </xsl:template>
  
  <xsl:template match="moduleshistory/revnotes" mode="revnotes">
      <xsl:apply-templates select="revnote" mode="revnotes">
         <xsl:sort select="@rev" order="descending" />
      </xsl:apply-templates>
   </xsl:template>
   
  <xsl:template match="moduleshistory/revnotes/revnote" mode="revnotes">
   <xsl:variable name="modname">
      <xsl:call-template name="modname">
         <xsl:with-param name="path" select="../@path" />
      </xsl:call-template>
   </xsl:variable>
    <xsl:value-of select="$modname" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="@rev" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="@user" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="@date" />
    <xsl:text>;</xsl:text>
    <xsl:value-of select="." />
    <xsl:text>;&#10;</xsl:text>
  </xsl:template>

  <xsl:template name="modname">
   <xsl:param name="path" />
   <xsl:choose>
      <xsl:when test="contains($path, '/')">
         <xsl:call-template name="modname">
            <xsl:with-param name="path" select="substring-after($path, '/')" />
         </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="$path" />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
