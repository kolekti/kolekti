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

  
  <xsl:output  method="xml" 
               indent="yes"
	           omit-xml-declaration="yes"
	       />
  <xsl:param name="path"/>

  
  <xsl:include href="django_variables.xsl"/>
  <xsl:include href="django_conditions.xsl"/> 
  <xsl:include href="django_tables.xsl"/>
  <xsl:include href="django_identity.xsl"/>
  <xsl:include href="django_pictures.xsl"/>



  
  <xsl:template name="basename">
    <xsl:param name="path"/>
    <xsl:choose>
      <xsl:when test="contains($path,'/')">
	<xsl:call-template name="basename">
	  <xsl:with-param name="path" select="substring-after($path,'/')"/>
	</xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
	<xsl:value-of select="$path"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  

  
  <xsl:template match = "html:div[@class='topic']">    
    <xsl:copy>
      <xsl:apply-templates select="@class"/>
      <xsl:copy-of select="@id"/>
      <xsl:attribute name="data-topic-source">
        <xsl:value-of select="html:div[@class='topicinfo']/html:p[html:span[@class='infolabel'][text()='source']]/html:span[@class='infovalue']"/>
      </xsl:attribute>
      <div class="panel panel-default">
        <div class="panel-heading">
          <xsl:apply-templates select="html:div[@class='topicinfo']"/>
        </div>
        <div class="panel-body">
          <div class="row">
            <div class="topicstatus alert alert-info col-md-12 hidden" role="alert">
              <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">×</span>
              </button>
              <span class="content"></span>
            </div>                        
            <div class="topiccontent col-md-12">
              <xsl:apply-templates select="*[not(@class='topicinfo')]"/>
            </div>
          </div>
        </div>
      </div>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match = "html:div[@class='topicinfo']">
    <xsl:variable name="topicsource" select="html:p[html:span[@class='infolabel'][text()='source']]/html:span[@class='infovalue']"/>
    <div class="dropdown pull-right">
      <button class="btn btn-xs btn-default dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
        <span class="glyphicon glyphicon-cog"/>
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right" aria-labelledby="dLabel">
        
        <li>
          <a href="#" class="compare_topic_source">Comparer avec le module source</a>
        </li>
        
        <li><a href="#" class="compare_topic_release">Comparer avec une version...</a></li>
        
        <li><a href="#" class="edit_topic_release">Modifier l'assemblage</a></li>
        <li><a href="/{$project}{$topicsource}/edit" target="new" class="edit_topic_source">Éditer le module source </a></li>
      </ul>
    </div>
    
    <span>
      <xsl:call-template name="basename">
        <xsl:with-param name="path" select="translate($topicsource, '\', '/')"/>
      </xsl:call-template>
    </span>
    
  </xsl:template>


  
      

  <xsl:template match="html:div[starts-with(@class,'TOC')]">
    <div class="alert alert-warning" role="alert">Table des matières</div>
  </xsl:template>

  <xsl:template match="html:div[@class='section']">
    <div class="panel panel-default panel-section">
      <div class="panel-heading">
        <xsl:apply-templates select="html:h1"/>
      </div>
      <div class="panel-body">
          <xsl:apply-templates select="html:div[@class='topic']|html:div[@class='section']"/>
      </div>
    </div>    
  </xsl:template>
    
    
</xsl:stylesheet>
