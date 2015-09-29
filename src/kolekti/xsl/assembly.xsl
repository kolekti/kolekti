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
  xmlns="http://www.w3.org/1999/xhtml" 
  xmlns:exsl="http://exslt.org/common"
  xmlns:html="http://www.w3.org/1999/xhtml" 
  xmlns:kt="kolekti:trames"
  xmlns:kf="kolekti:extensions:functions:publication"
  extension-element-prefixes="exsl kf" 
  exclude-result-prefixes="html kf kt"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <!-- parametres d'entrée : langue et basepath -->
  <xsl:param name="lang"/>

  <xsl:template match="/">
    <xsl:apply-templates mode="aggreg"/>
  </xsl:template>
 
  <xsl:template match="html:*" mode="aggreg">
    <xsl:param name="section_depth"/>
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="html:html" mode="aggreg">
    <html>
      <head>
        <title>
          <xsl:value-of select="html:head/html:title/text()"/>
        </title>
      </head>
      <body lang="{$lang}" xml:lang="{$lang}">
        <xsl:apply-templates select="html:body" mode="aggreg">
          <xsl:with-param name="section_depth" select="'0'"/>
        </xsl:apply-templates>
      </body>
    </html>
  </xsl:template>
  
  
  <!-- traitement d'une section -->
 
  <xsl:template match="html:section|html:div[@class='section']" mode="aggreg">
    <xsl:param name="section_depth"/>
    <div class="section">
      <!--
	  <xsl:comment>
        <xsl:text>depth </xsl:text>
        <xsl:value-of select="$section_depth"/>
	</xsl:comment>
      -->
      <xsl:copy-of select="@data-hidden"/>
      <xsl:apply-templates mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth+1"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>



  <!-- traitement des topics -->

  <xsl:template match="html:a[@rel = 'kolekti:toc']" mode="aggreg" >
    <xsl:param name="section_depth"/>

    <div class='TOC {@class}'>
      <p class="TOC_title">
        <var class="kolektitext:TOC"/>
      </p>
    </div>
  </xsl:template>


  <xsl:template match="html:a[@rel = 'kolekti:index']" mode="aggreg" >
    <xsl:param name="section_depth"/>
    <xsl:variable name="hx">
      <xsl:choose>
        <xsl:when test="$section_depth &lt; 5">
          <xsl:text>h</xsl:text>
          <xsl:value-of select="$section_depth + 1"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>h6</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <div>
      <xsl:attribute name="class">
        <xsl:text>INDEX</xsl:text>
        <xsl:if test="@class"> <xsl:value-of select="@class"/></xsl:if>
      </xsl:attribute>
      <h1 class="INDEX_titre">
        <var class="kolektitext:INDEX"/>
      </h1>
    </div>
  </xsl:template>


  <xsl:template match="html:a[@rel = 'kolekti:revnotes']" mode="aggreg" >
    <xsl:param name="section_depth"/>
    <xsl:variable name="hx">
      <xsl:choose>
        <xsl:when test="$section_depth &lt; 5">
          <xsl:text>h</xsl:text>
          <xsl:value-of select="$section_depth + 1"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>h6</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <div class='REVNOTES {@class}'>
      <xsl:element name="{$hx}">
        <xsl:attribute name="class">REVNOTES_titre</xsl:attribute>
        <var class="kolektitext:REVNOTES"/>
      </xsl:element>
    </div>
  </xsl:template>


  <xsl:template match="html:a[@rel = 'kolekti:topic']" mode="aggreg" >
    <xsl:param name="section_depth"/>
    
    <xsl:variable name="topic_url" select="kf:gettopic(string(@href))"/>
    <xsl:variable name="topic" select="document($topic_url)"/>
    <div class="topic" id="{generate-id()}">
      <div class="topicinfo">
         <xsl:comment>Do not translate</xsl:comment>
         <p><span class="infolabel">source</span><span class="infovalue"><a href="{$topic_url}"><xsl:value-of select="$topic_url"/></a></span></p>
         <xsl:apply-templates select="$topic/html:html/html:head/html:meta|$topic/html/head/meta" mode="topic_info"/>
      </div>

      <xsl:apply-templates select="$topic/html:html/html:body|$topic/html/body" mode="aggreg">
	<xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>



  <xsl:template match="html:meta[@name]|meta[@name]" mode="topic_info">
    <p><span class="infolabel"><xsl:value-of select="@name"/></span><span class="infovalue"><xsl:value-of select="@content"/></span></p>
  </xsl:template>



  <!-- traitement du corps du topic -->

  <xsl:template match="html:body|body" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:apply-templates select="node()" mode="aggreg">
      <xsl:with-param name="section_depth" select="$section_depth"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- copie tous les noeuds des topics -->

  <xsl:template match="node()|@*" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="*" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="node()|@*" mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </xsl:element>
  </xsl:template>

  <!-- marques d'index : normalize le contenu des entrées -->

  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']|ins[@class='index']|span[@rel='index']" mode="aggreg">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="@*" mode="aggreg"/>
      <xsl:value-of select="normalize-space(.)"/>
    </xsl:element>
  </xsl:template>


</xsl:stylesheet>
