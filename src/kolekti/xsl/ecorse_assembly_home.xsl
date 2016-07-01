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

  
  <xsl:output  method="html" 
               indent="yes"
	       omit-xml-declaration="yes"
	       />
  
  <xsl:param name="path"/>
  <xsl:param name="section" select="''"/>
  <xsl:param name="share" select="'False'"/>
  
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
  

  <xsl:template match="html:div[@class='topic']/html:h1">
    <h5>
      <xsl:apply-templates select="node()|@*"/>
    </h5>
  </xsl:template>

  <xsl:template match="html:h1"/>
  <xsl:template match="html:head"/>

  <xsl:template match = "html:div[@class='section']">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match = "html:body">
    <div class="accueil sections">
      <div class="row">
	<xsl:apply-templates select="html:div[@class='section']"/>
      </div>
    </div>
    <div class="accueil alaune">
      <div class="panel panel-default">
	<div class="panel-heading">
	  <h3 class="panel-title">Indicateurs à la une</h3>
	</div>
	<div class="panel-body">
	  <div class="row">
	    <xsl:apply-templates select=".//html:div[@class='topic'][@data-star]"/>
	  </div>
	</div>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template match = "html:body/html:div[@class='section']">
    <xsl:variable name="url">
      <xsl:choose>
	<xsl:when test="$share='False'">
	  <xsl:text>/elocus/report/?release=</xsl:text>
	  <xsl:value-of select="$path"/>
	  <xsl:text>&amp;</xsl:text>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:text>?</xsl:text>
	</xsl:otherwise>
      </xsl:choose>
      <xsl:text>section=</xsl:text>
      <xsl:value-of select="@id"/>
    </xsl:variable>
    
    
    <div class="col-lg-3 col-md-6">
      <div class="panel panel-primary {html:h1/@class}">
	<div class="panel-heading">
	  <div class="row">
	    <div class="col-xs-3">
	      <div class="picto {html:h1/@class}"></div>
	    </div>
	    <div class="col-xs-9 text-right">
	      <div class="huge">
		<xsl:value-of select="html:h1"/>
	      </div>
	      <div>
		<xsl:value-of select="count(.//html:div[@class='topic'])"/>
		&#xA0;Indicateurs
	      </div>
	    </div>
	  </div>
	</div>
	<a href="{$url}">
	  <div class="panel-footer">
	    <span class="pull-left">
	      Voir les détails
	    </span>
	    <span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
	    <div class="clearfix"></div>
	  </div>
	</a>
      </div>
    </div>

  </xsl:template>

  
  <xsl:template match = "html:div[@class='topic'][@data-star]">
    <div class="col-lg-3 col-md-6">
      <div class="panel panel-default {ancestor::html:div[@class='section']/html:h1/@class}">
	<div class="panel-heading">
	  <div class="row">
	    <div class="col-xs-3">
	      <div class="picto {ancestor::html:div[@class='section']/html:h1/@class}"></div>
	    </div>
	    <div class="col-xs-9 text-right">
	      <div class="huge">
	      </div>
	      <div>
		<xsl:value-of select="html:h1"/>
	      </div>
	    </div>
	  </div>
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
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapseDetails{@id}" aria-expanded="false" aria-controls="collapseDetails{@id}">
	<i class="fa fa-info"></i><xsl:text> Détails</xsl:text>
      </a>
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapseAnalyse{@id}" aria-expanded="false" aria-controls="collapseAnalyse{@id}">
	<i class="fa fa-pencil"></i>
	<xsl:text> Analyse</xsl:text>
      </a>
      <xsl:if test="$share='False'">
      <a class="btn btn-default btn-xs ecorse-action-collapse" role="button" data-toggle="collapse" href="#collapsePictures{@id}" aria-expanded="false" aria-controls="collapsePictures{@id}">
	<i class="fa fa-picture-o"></i>
	<xsl:text> Visuels</xsl:text>
      </a>
      </xsl:if>
    </span>
    <xsl:if test="$share='False'">
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
	<xsl:variable name="ckind" select="@data-chart-kind"/>
	<ul class="dropdown-menu" role="menu">
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chart-type="Bar">
	    <xsl:text>Histogramme </xsl:text>

	    <xsl:if test="$ckind='Bar'">
	      <i class="fa fa-check"></i>
	    </xsl:if>
	  </a></li>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="ecorse-action-chart" data-chart-type="Line">
	    <xsl:text>Linéaire </xsl:text>
	    <xsl:if test="$ckind='Line'">
	      <i class="fa fa-check"></i>
	    </xsl:if>
	  </a></li>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_pie">Circulaire</a></li>
	  <li role="presentation" class="divider"/>
	  <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_chart_options">Options...</a></li>
	</ul>
      </span>
    </span>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="html:div[@class='kolekti-sparql-foreach-results']">
    <div class="collapse collapseDetails collapseTopic" id="collapseDetails{ancestor::html:div[@class='topic']/@id}" role="tabpanel">
      <div class="well">
	<table class="table">
	  <xsl:apply-templates/>
	</table>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-analyse">
    <div class="collapse collapseAnalyse collapseTopic" id="collapseAnalyse{@id}"  role="tabpanel">
      <div class="well">
	<div id="editor{@id}" class="anaeditor" contenteditable="true">
	  <xsl:copy-of select="html:div[@class='analyse']"/>
	</div>
      </div>
    </div>
  </xsl:template>
  
  <xsl:template name="topic-visuels">
    <div class="collapse collapsePictures collapseTopic" id="collapsePictures{@id}"  role="tabpanel">
      <div class="well">
	<xsl:copy-of select="div[@class='visuels']"/>
      </div>
    </div>
  </xsl:template>


  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']">
    <tr>
      <xsl:apply-templates mode="tpl"/>
    </tr>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']//html:span" mode="tpl">
    <td>
      <xsl:apply-templates/>
    </td>
  </xsl:template>

  <xsl:template match="html:div[@class='kolekti-sparql-foreach-result']//html:span[@class='tplvalue']" mode="tpl">
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="html:p[@class='kolekti-sparql-result-chartjs']">
    <div class="kolekti-sparql-result-chartjs" data-chartjs-data='{.}' id="chart_{ancestor::html:div[@class='topic']/@id}">
      <xsl:copy-of select='@data-chartjs-kind'/>
      <canvas id="canvas_{ancestor::html:div[@class='topic']/@id}"></canvas>
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
