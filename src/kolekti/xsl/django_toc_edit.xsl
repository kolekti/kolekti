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

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="/">
   <div id="toc_root" data-kolekti-title="{html:html/html:head/html:title}">
     <xsl:apply-templates select="html:html/html:body/*"/>
   </div>
  </xsl:template>

  <xsl:template match="html:a[@rel='kolekti:toc']">
    <div class="topic" data-kolekti-topic-rel="kolekti:toc">
      <div class="panel panel-default">
	<div class="panel-heading">
	  <h4 class="panel-title">
	    <input type="checkbox" class="select_topic"/>
	    <xsl:text> </xsl:text>
	    <a data-toggle="collapse" href="#collapse_{generate-id()}">
	      <span data-toggle="tooltip" data-placement="top" title="Table des Matières">
		<span class="glyphicon glyphicon-cog"> </span>
		Table des Matières
	      </span>
	    </a>
	    <xsl:text> </xsl:text>
	    <span class="dropdown">
	      <a data-toggle="dropdown"  href="#" id="dropdownMenu_{generate-id()}">
		<span class="caret"></span>
	      </a>
	      <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu_{generate-id()}">
		<xsl:call-template name="topicmenu"/>
	      </ul>
	    </span>
	  </h4>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="html:a[@rel='kolekti:index']">
    <div class="topic" data-kolekti-topic-rel="kolekti:index">
      <div class="panel panel-default">
	<div class="panel-heading">
	  <h4 class="panel-title">
	    <input type="checkbox" class="select_topic"/>
	    <xsl:text> </xsl:text>
	    <a data-toggle="collapse" href="#collapse_{generate-id()}">
	      <span data-toggle="tooltip" data-placement="top" title="Index alphabétique">
		<span class="glyphicon glyphicon-cog"> </span>
		Index alphabétique
	      </span>
	    </a>
	    <xsl:text> </xsl:text>
	    <span class="dropdown">
	      <a data-toggle="dropdown"  href="#" id="dropdownMenu_{generate-id()}">
		<span class="caret"></span>
	      </a>
	      <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu_{generate-id()}">
		<xsl:call-template name="topicmenu"/>
	      </ul>
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
	    <input type="checkbox" class="select_topic"/>
	    <xsl:text> </xsl:text>
	    <a data-toggle="collapse" href="#collapse_{generate-id()}">
	      <span data-toggle="tooltip" data-placement="top" title="{@href}">
		<xsl:value-of select="$topic/html:html/html:head/html:title"/>
	      </span>
	    </a>
	    <xsl:text> </xsl:text>
	    <span class="dropdown">
	      <a data-toggle="dropdown"  href="#" id="dropdownMenu_{generate-id()}">
		<span class="caret"></span>
	      </a>
	      <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu_{generate-id()}">
		<li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_edit">Editer</a></li>
		<xsl:call-template name="topicmenu"/>
	      </ul>
	    </span>
	  </h4>
	</div>
      </div>
      <div class="panel-collapse collapse" id="collapse_{generate-id()}">
	<div class="topiccontent ">
	  <xsl:copy-of select="$topic/html:html/html:body/*"/>
	</div>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="topicmenu">
    <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_delete">Supprimer</a></li>
    <li role="presentation" class="divider"></li>
    <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_up">Monter</a></li>
    <li role="presentation"><a role="menuitem" tabindex="-1" href="#" class="btn_topic_down">Descendre</a></li>
  </xsl:template>


</xsl:stylesheet>
