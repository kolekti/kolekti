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

  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topictitle"/>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicbody">
    <xsl:call-template name="chartbody"/>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanelinfo">
    <xsl:call-template name="chartbody"/>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanelbody"/>
    
  <xsl:template name="chartbody">
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
    <xsl:variable name="data" select="string(html:div[@class='kolekti-sparql']/html:div[@class='kolekti-sparql-result']/html:div[@class='kolekti-sparql-result-json'])"/>
    <xsl:if test="string-length($data)">
      <div class="row">
	<div class="col-sm-4">Type de graphique</div>
	<div class="col-sm-6">
	  <span class="btn-group">
	    <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
	      <i class="fa fa-bar-chart-o"></i>&#xA0;<span class="caret"> </span>
	    </button>
	    <xsl:variable name="ckind" select="@data-chartkind"/>
	    <ul class="dropdown-menu" role="menu">
	      <li role="presentation">
		<a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart-kind" data-chartkind="bar">
		  <xsl:text>Histogramme </xsl:text>
		</a>
	      </li>
		  <li role="presentation">
		    <a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart-kind" data-chartkind="line">
		      <xsl:text>Linéaire </xsl:text>
		    </a>
		  </li>
		  <li role="presentation">
		    <a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart-kind" data-chartkind="draw">
		      <xsl:text>Illustrations</xsl:text>
		    </a>
		  </li>
	    </ul>
	  </span>
	</div>
	<div class="col-sm-4">Afficher l'icone</div>
	<div class="col-sm-6"><input type="checkbox" class="ecorse-action-chart-icon"/></div>
	<div class="col-sm-4">Texte du graphique</div>
	<div class="col-sm-6"><input type="text" class="ecorse-action-chart-text"/></div>
      </div>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanelbutton"/>
  
  <xsl:template match="html:div[@class='kolekti-component-chart']" mode="topicpanel"/>

</xsl:stylesheet>
