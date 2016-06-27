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

  <xsl:template match="html:div[@class='kolekti-component-details']" mode="topictitle"/>
  <xsl:template match="html:div[@class='kolekti-component-details']" mode="topicbody"/>

  <xsl:template match="html:div[@class='kolekti-component-details']" mode="topicpanelaction">
    <xsl:apply-templates mode="compdetails"/>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-details']" mode="topicpanelbutton"/>
  <!--
      <xsl:call-template name="makepanelbutton">
      <xsl:with-param name="content">
	<i class="fa fa-info"></i><xsl:text> Détails</xsl:text>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>
  -->
  
  <xsl:template match="html:div[@class='kolekti-component-details']" mode="topicpanel"/>
<!--    <xsl:call-template name="makepanel">
      <xsl:with-param name="content">
	<xsl:apply-templates mode="compdetails"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>
-->
  <xsl:template match="node()|@*" mode="compdetails">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="compdetails"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql']" mode="compdetails">
    <xsl:apply-templates select="html:div[@class='kolekti-sparql-result']/html:tr" mode="compdetails"/>
  </xsl:template>


</xsl:stylesheet>
