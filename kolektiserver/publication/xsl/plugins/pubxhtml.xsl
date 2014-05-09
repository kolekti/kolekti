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
  xmlns:h="http://www.w3.org/1999/xhtml"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="h"
  version="1.0">

  <xsl:param name="css"/>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="h:a[@class='indexmq']" />

  <xsl:template match="h:head">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
      <link rel="stylesheet" type="text/css" href="css/{$css}.css"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="h:img">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>../medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <img src="{$src}" alt="{@alt}" title="{@title}" />
  </xsl:template>

  <xsl:template match="h:embed">
   <xsl:variable name="src">
      <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
            <xsl:text>../medias/</xsl:text>
            <xsl:value-of select="substring-after(@src, 'medias/')" />
         </xsl:otherwise>
      </xsl:choose>
   </xsl:variable>
   <embed width="{@width}" height="{@height}" type="{@type}" pluginspage="{@pluginspage}" src="{$src}" />
  </xsl:template>
  
  <xsl:template match="h:meta[@schema='condition']"/>
  <xsl:template match="h:div[@class='moduleinfo']"/>

</xsl:stylesheet>
