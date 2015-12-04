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
  
  exclude-result-prefixes="html"
  version="1.0">

  
  <xsl:output  method="html" 
               indent="yes"
	       omit-xml-declaration="yes"
	       />
  
  <xsl:param name="path"/>
  <xsl:param name="section" select="''"/>
  
  <xsl:template match="text()|@*">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="*[namespace-uri(self::*)='http://www.w3.org/1999/xhtml']" priority="-10">
    <xsl:element name="{local-name()}" namespace="">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  

  <xsl:template match="html:h1">
    <xsl:element name="h{count(ancestor::html:div[@class='section']) + 1}" namespace="">
      <xsl:attribute name="class">
	<xsl:value-of select="@class"/>
	<xsl:text> clearfix col-lg-12</xsl:text>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="html:div[@class='topic']/html:h1">
    <h5>
      <xsl:apply-templates select="node()|@*"/>
    </h5>
  </xsl:template>
  
  <xsl:template match = "html:div[@class='section']">
    <xsl:if test="ancestor-or-self::html:div[@id=$section]">
      <xsl:copy>
	<xsl:apply-templates select="@*"/>
	<xsl:apply-templates select="html:h1"/>
	<xsl:apply-templates select="html:div"/>
      </xsl:copy>
    </xsl:if>
  </xsl:template>

  <xsl:template match = "html:div[@class='topic']">
    <div class="col-sm-12 col-lg-6">
      <div class="thumbnail">
	<xsl:apply-templates select="html:div[@class='kolekti-sparql']"/>
	<div class="caption">
	  <xsl:copy>
	    <xsl:apply-templates select="@*"/>
	    <xsl:apply-templates select="html:h1"/>
	    <hr/>
	    <div class="topicCollapses" id="collapseTopic{generate-id()}" role="tablist">

	      <xsl:call-template name="topic-controls"/>
	      <xsl:apply-templates select="html:div[@class='details']"/>
	      <xsl:call-template name="topic-analyse"/>
	      <xsl:call-template name="topic-visuels"/>
	    </div>
	  </xsl:copy>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match = "html:div[@class='topicinfo']"/>

  <xsl:template match = "html:div[@class='kolekti-sparql-foreach']">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match = "html:p[@class='kolekti-sparql-foreach-query']"/>
  <xsl:template match = "html:div[@class='kolekti-sparql-foreach-template']"/>
  <xsl:template match = "html:div[@class='kolekti-sparql-results']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match = "html:div[@class='kolekti-sparql']">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match = "html:p[@class='kolekti-sparql-query']"/>
  <xsl:template match = "html:p[@class='kolekti-sparql-result-json']"/>


  <xsl:template name="topic-controls">
    <span class="btn-group">
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapseDetails{generate-id()}" aria-expanded="false" aria-controls="collapseDetails{generate-id()}">
	<i class="fa fa-info"></i><xsl:text> Détails</xsl:text>
      </a>
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapseAnalyse{generate-id()}" aria-expanded="false" aria-controls="collapseAnalyse{generate-id()}">
	<i class="fa fa-pencil"></i>
	<xsl:text> Analyse</xsl:text>
      </a>
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapsePictures{generate-id()}" aria-expanded="false" aria-controls="collapsePictures{generate-id()}">
	<i class="fa fa-picture-o"></i>
	<xsl:text> Visuels</xsl:text>
      </a>
    </span>
    <span class="btn-group pull-right">
      <button title="A la une">
	<xsl:attribute name="class">
	  <xsl:text>btn btn-xs btn-default  ecorse-action-star </xsl:text>
	  <xsl:choose>
	    <xsl:when test="ancestor-or-self::html:div[@class='topic'][@data-star]">btn-warning</xsl:when>
	    <xsl:otherwise>btn-default</xsl:otherwise>
	    </xsl:choose>
	</xsl:attribute>
	
	  
	<i class="fa fa-star-o"></i>
      </button>
      <button title="Supprimer" class="btn btn-xs btn-default  ecorse-action-hide">
	<i class="fa fa-trash-o"></i>
      </button>
      <span class="btn-group">
	<button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
	  <i class="fa fa-bar-chart-o"></i>&#xA0;<span class="caret"> </span>
	</button>
	<ul class="dropdown-menu" role="menu">
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chart-type="bar">
	    <xsl:text>Histogramme </xsl:text>
	    <xsl:if test="@data-chart-type='bar'">
	      <span class="glyphicon glyphicon-ok"></span>
	    </xsl:if>
	  </a></li>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chart-type="line">
	    <xsl:text>Linéaire </xsl:text>
	    <xsl:if test="@data-chart-type='bar'">
	      <span class="glyphicon glyphicon-ok"></span>
	    </xsl:if>
	  </a></li>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_pie">Circulaire</a></li>
	  <li role="presentation" class="divider"/>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_options">Options...</a></li>
	</ul>
      </span>
    </span>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-sparql-foreach-results']">
    <div class="collapse collapseDetails collapseTopic" id="collapseDetails{generate-id(ancestor::html:div[@class='topic'])}" role="tabpanel">
      <div class="well">
	<table class="table">
	  <xsl:apply-templates/>
	</table>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-analyse">
    <div class="collapse collapseAnalyse collapseTopic" id="collapseAnalyse{generate-id()}"  role="tabpanel">
      <div class="well">
	<div id="editor{generate-id()}" class="anaeditor" contenteditable="true">
	  <xsl:copy-of select="html:div[@class='analyse']"/>
	</div>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-visuels">
    <div class="collapse collapsePictures collapseTopic" id="collapsePictures{generate-id()}"  role="tabpanel">
      <div class="well">
	<xsl:copy-of select="div[@class='visuels']"/>
      </div>
    </div>
  </xsl:template>


  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']">
    <tr>
      <xsl:apply-templates select=".//html:span"/>
    </tr>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']//html:span">
    <td>
      <xsl:apply-templates/>
    </td>
  </xsl:template>

  <xsl:template match="html:p[@class='kolekti-sparql-result-chartjs']">
    <div class="kolekti-sparql-result-chartjs" data-chartjs-data='{.}'>
      <xsl:copy-of select='@data-chartjs-kind'/>
      <canvas id="{generate-id()}"></canvas>
      <div class="legend">
      </div>
    </div>
  </xsl:template>

  
  <xsl:template match="html:img/@src">
    <xsl:attribute name="src">
      <xsl:value-of select="$path"/>
      <xsl:value-of select="."/>
    </xsl:attribute>
  </xsl:template>
      


  
  
</xsl:stylesheet>
