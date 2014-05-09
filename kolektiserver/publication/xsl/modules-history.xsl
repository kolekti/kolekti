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
  xmlns:exsl="http://exslt.org/common"
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns:kt="kolekti:trames"
  xmlns:kfp="kolekti:extensions:functions:publication"
  extension-element-prefixes="exsl kfp" 
  exclude-result-prefixes="html kfp kt"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes" />

  <!-- parametres d'entrée : langue et basepath -->
  <xsl:param name="lang"><xsl:value-of select="kfp:lang()" /></xsl:param>

  <xsl:template match="/">
   <moduleshistory>
      <xsl:apply-templates select="//html:div[@class='module']" />
   </moduleshistory>
  </xsl:template>

  <xsl:template match="html:div[@class='module']">
    <xsl:variable name="path" select="string(html:div[@class='moduleinfo']/html:p[html:span[@class='infolabel']/text() = 'source']/html:span[@class='infovalue']/html:a)" />
    <xsl:variable name="revnotes" select="kfp:get_revnotes($path)" />
    <revnotes path="{$path}">
      <xsl:for-each select="$revnotes/log">
         <xsl:variable name="author">
            <xsl:choose>
               <xsl:when test="number(@uid) &gt;= 0">
                  <xsl:value-of select="kfp:username(string(@uid))" />
               </xsl:when>
               <xsl:otherwise>
                  <xsl:value-of select="@author" />
               </xsl:otherwise>
            </xsl:choose>
         </xsl:variable>
         <revnote rev="{@number}" user="{$author}" date="{@date}"><xsl:value-of select="@msg"/></revnote>
      </xsl:for-each>
   </revnotes>
  </xsl:template>
</xsl:stylesheet>
