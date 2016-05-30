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

  <xsl:template match="/libs">
    <libs>
      <css>
	<link rel="stylesheet" type="text/css" href="/static/components/css/chart.css"/>
      </css>
      <scripts>
	<script src="/static/d3.min.js"/>
	<script src="/static/components/js/chart.js"/>
      </scripts>
    </libs>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicbody">
    <xsl:variable name="data" select="string(html:div[@class='kolekti-sparql']/html:div[@class='kolekti-sparql-result']/html:div[@class='kolekti-sparql-result-json'])"/>
    <xsl:if test="string-length($data)">
      <div class="ecorse-chart">
      
	<xsl:attribute name="data-chartdata">
	  <xsl:value-of select="$data"/>
	</xsl:attribute>
	<xsl:attribute name="data-chartkind">
	  <xsl:choose>
	    <xsl:when test="@data-chartkind">
	      <xsl:value-of select="@data-chartkind"/>
	    </xsl:when>
	    <xsl:otherwise>bar</xsl:otherwise>
	  </xsl:choose>
	</xsl:attribute>
      </div>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanelaction">
    <span class="btn-group">
      <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
	<i class="fa fa-bar-chart-o"></i>&#xA0;<span class="caret"> </span>
      </button>
      <xsl:variable name="ckind" select="@data-chartkind"/>
      <ul class="dropdown-menu" role="menu">
	<li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chartkind="bar">
	  <xsl:text>Histogramme </xsl:text>
	  
	  <xsl:if test="$ckind='bar' or not(@data-chartkind)">
	    <i class="fa fa-check"></i>
	  </xsl:if>
	</a></li>
	<li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chartkind="line">
	  <xsl:text>Linéaire </xsl:text>
	  <xsl:if test="$ckind='line'">
	    <i class="fa fa-check"></i>
	  </xsl:if>
	</a></li>
	<!--
	<li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_pie">Circulaire</a></li>
	<li role="presentation" class="divider"/>
	<li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_options">Options...</a></li>
	-->
      </ul>
    </span>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanelbutton"/>
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanel"/>

</xsl:stylesheet>
