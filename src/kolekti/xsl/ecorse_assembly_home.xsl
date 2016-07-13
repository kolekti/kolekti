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

  <xsl:include href="ecorse_components.xsl"/>
  
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
    
    
    <div class="col-lg-4 col-md-6">
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
		<xsl:value-of select="count(.//html:div[@class='topic'][not(@data-hidden='yes')])"/>
		&#xA0;Indicateurs
	      </div>
	    </div>
	  </div>
	</div>
	<a href="{$url}">
	  <div class="panel-footer">
	    <span class="pull-left">
	      Accéder aux indicateurs
	    </span>
	    <span class="pull-right"><i class="fa fa-arrow-circle-right"></i></span>
	    <div class="clearfix"></div>
	  </div>
	</a>
      </div>
    </div>

  </xsl:template>

  <!-- topics à la une -->
  <xsl:template match = "html:div[@class='topic'][@data-star]">
    <div class="col-lg-3 col-md-6">
      <div class="panel panel-default {ancestor::html:div[@class='section']/html:h1/@class}">
	<div class="panel-heading">
	  <div class="row">
	    <div class="col-xs-3">
	      <div class="picto {ancestor::html:div[@class='section']/html:h1/@class}"></div>
	    </div>
	    <div class="col-xs-9 text-right">
	      <div>
		<xsl:apply-templates select=".//html:div[@class='kolekti-component-title']" mode="topictitle"/>
	      </div>
	    </div>
	  </div>
	</div>
	<div class="panel-body">
	  <xsl:apply-templates select=".//html:div[@class='kolekti-component-chart']" mode="topicbody"/>
	  <xsl:apply-templates select=".//html:div[@class='kolekti-component-map']" mode="topicbody"/>
	</div>
      </div>
    </div>

  </xsl:template>


  <xsl:template match = "html:div[@class='topicinfo']"/>


  
  
</xsl:stylesheet>
