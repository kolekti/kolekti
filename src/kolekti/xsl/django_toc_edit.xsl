<?xml version="1.0" encoding="ISO-8859-1"?>
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
  xmlns:kf="kolekti:extensions:functions:publication"
  exclude-result-prefixes="kf html"
  version="1.0">

  <xsl:output  method="html" 
               indent="yes"/>

  <xsl:template match="text()|@*">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="/">
     <xsl:apply-templates select="html:html/html:body/*"/>
  </xsl:template>


  <xsl:template match="html:div[@class='section']">
    <div class="section panel panel-info">
      <div class="panel-heading">
	<xsl:apply-templates select="*[not(self::html:a)]" mode="collapse"/>
      </div>

      <div class="panel-collapse collapse in" id="collapse_{generate-id()}">
	<div class="panel-body">
	  <xsl:apply-templates select="html:a"/>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="*" mode="collapse">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*"/>
      <a data-toggle="collapse" href="#collapse_{generate-id(ancestor::html:div)}">
	<xsl:apply-templates/>
      </a>
    </xsl:element>
  </xsl:template>


  <xsl:template match="html:a[@rel='kolekti:toc']">
    <div class="topic" data-kolekti-topic-rel="kolekti:toc">
      <div class="panel panel-warning">
	<div class="panel-heading">
	  <h4 class="panel-title">
	    <span data-toggle="tooltip" data-placement="top" title="Table des Matières">
	      <em>Table des Matières</em>
	    </span>
	  </h4>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="html:a[@rel='kolekti:index']">
    <div class="topic" data-kolekti-topic-rel="kolekti:index">
      <div class="panel panel-warning">
	<div class="panel-heading">
	  <h4 class="panel-title">
	    <span data-toggle="tooltip" data-placement="top" title="Index alphabétique">
	      <em>Index alphabétique</em>
	    </span>
	  </h4>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="html:a[@rel='kolekti:topic']">
    <div class="topic" data-kolekti-topic-href="{@href}" data-kolekti-topic-rel="kolekti:topic">

      <xsl:variable name="topic_url" select="kf:gettopic(string(@href))"/>
      <xsl:variable name="topic" select="document($topic_url)"/>

      <div class="panel panel-default">
	<div class="panel-heading">
	  <h4 class="panel-title">
	    <a data-toggle="collapse" href="#collapse_{generate-id()}">
	      <span data-toggle="tooltip" data-placement="top" title="{@href}">
		<xsl:value-of select="$topic/html:html/html:head/html:title"/>
	      </span>
	    </a>
	  </h4>
	</div>
      </div>
      <div class="panel-collapse collapse" id="collapse_{generate-id()}">
	<div class="topiccontent">
	  <xsl:copy-of select="$topic/html:html/html:body/*"/>
	</div>
      </div>
    </div>
  </xsl:template>



</xsl:stylesheet>
