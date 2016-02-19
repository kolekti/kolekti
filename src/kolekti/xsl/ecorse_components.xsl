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

     <xsl:include href="components/details.xsl"/>
      <xsl:include href="components/chart.xsl"/>
  <!--
      <xsl:include href="components/wysiwyg.xsl"/>
      <xsl:include href="components/pad.xsl"/>
      <xsl:include href="components/leaflet.xsl"/>
      <xsl:include href="components/d3js.xsl"/>
  -->

  <xsl:template name="makepanel">
    <xsl:param name="content"/>
    <xsl:param name="id" select="generate-id()"/>
    <div class="collapse collapseTopic" id="collapse{$id}" role="tabpanel">
      <div class="well">
	<xsl:copy-of select="$content"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="makepanelbutton">
    <xsl:param name="content"/>
    <xsl:param name="id" select="generate-id()"/>
    <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapse{$id}" aria-expanded="false" aria-controls="collapse{$id}">
      <xsl:copy-of select="$content"/>
    </a>
  </xsl:template>


  <xsl:template match="html:div[@class='kolekti-sparql-query']" mode="topicpanel"/>
  <xsl:template match="html:div[@class='kolekti-sparql-query']" mode="topicpanelbutton"/>
  <xsl:template match="html:div[@class='kolekti-sparql-query']" mode="topicpanelaction"/>

  <xsl:template match="html:div[@class='kolekti-sparql-result-json']" mode="topicpanel">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="html:div[@class='kolekti-sparql-result-json']" mode="topicpanelbutton"/>
  <xsl:template match="html:div[@class='kolekti-sparql-result-json']" mode="topicpanelaction"/>

</xsl:stylesheet>
