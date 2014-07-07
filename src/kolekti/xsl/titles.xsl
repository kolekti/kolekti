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


  <!-- copy everything not pprocessed by this stylesheet -->

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>



  <!-- calculate numbering for titles -->




  <!-- calculate numbering, set temporary attributes / class attributes -->

  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>

      <xsl:if test="not(@h)">
        <xsl:variable name="h">
          <xsl:value-of select="substring(local-name(),2,1)"/>
        </xsl:variable>
        
        <xsl:attribute name="h">
          <xsl:value-of select="count(ancestor::html:div[@class='section']|ancestor::html:div[@class='topic']) + $h"/>
        </xsl:attribute>

        
        
        <xsl:attribute name="class">
          <xsl:text>level</xsl:text>
          <xsl:value-of select="count(ancestor::html:div[@class='section'])"/>
          <xsl:text> title</xsl:text>
          <xsl:value-of select="count(ancestor::html:div[@class='section']|ancestor::html:div[@class='topic']) + $h"/>
          <xsl:if test="@class">
            <xsl:text> </xsl:text>
            <xsl:value-of select="@class"/>
          </xsl:if>
        </xsl:attribute>
      </xsl:if>

      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>




  <!-- cleanup -->

  <xsl:template match="html:h1/@h|html:h2/@h|html:h3/@h|html:h4/@h|html:h5/@h|html:h6/@h"/>

</xsl:stylesheet>
