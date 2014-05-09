<?xml version="1.0" encoding="utf-8"?>
<!--
     kOLEKTi : a structural documentation generator
     Copyright (C) 2007 StÃ©phane Bonhomme (stephane@exselt.com)

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
  exclude-result-prefixes="htm kfpl"
  version="1.0">

  <xsl:output  method="xml"
    indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!--traitement des liens -->
  <xsl:template match="html:a[@href]">
    <xsl:copy>
      <xsl:if test="@href='#' and not(contains(@class,'brokenlink'))">
        <!-- add class="brokenlink" if link is broken -->
        <xsl:attribute name="class">
          <xsl:if test="@class">
            <xsl:value-of select="@class"/>
            <xsl:text> </xsl:text>
          </xsl:if>
          <xsl:text>brokenlink</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:attribute name="href">
        <xsl:value-of select="@href"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:a/@href"/>

</xsl:stylesheet>
