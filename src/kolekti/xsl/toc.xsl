<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE stylesheet [
  <!ENTITY h "html:h1|html:h2|html:h3|html:h4|html:h5|html:h6">
  <!ENTITY tl "count(ancestor::html:div[@class='section']|ancestor::html:div[@class='topic']|ancestor::html:div[starts-with(@class,'INDEX')]) + substring(local-name(),2,1)">
]>

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
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="node()|@*" mode="titletoc">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="titletoc"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:span[@rel='index']|html:ins[@class='index']|html:a[@class='indexmq']" mode="titletoc"/>

  <xsl:template match="html:div[starts-with(@class,'TOC ')]">
    <div class="TOC">
      <xsl:apply-templates select="html:*[@class='TOC_title']" mode="maintitle" />
      <div class="TOC_body">
	<xsl:apply-templates select="/html:html/html:body" mode="toc"/>
      </div>
    </div>
  </xsl:template>


  <xsl:template match="html:*[@class='TOC_title']" mode="maintitle">
    <p class="TOC_title">
      <xsl:apply-templates />
    </p>
  </xsl:template>
  
  <xsl:template match="html:*[@class='TOC_titre']" mode="toc"> </xsl:template>

  <xsl:template match="&h;" mode="toc">
    <xsl:variable name="lev">
      <xsl:call-template name="titleclass"/>
    </xsl:variable>

    <p class="TOC_level_{$lev - 1}">
      <span class="title_num">
	<xsl:call-template name="number"/>
      </span>
      <xsl:choose>
	<xsl:when test="@id">
	  <a href="#{@id}"><xsl:apply-templates  mode="titletoc"/></a>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates  mode="titletoc"/>
	</xsl:otherwise>
      </xsl:choose>
    </p>
  </xsl:template>

  <xsl:template match="text()" mode="toc"/>




  <xsl:template match="&h;">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="class">
        <xsl:if test="@class">
          <xsl:value-of select="@class"/>
          <xsl:text> </xsl:text>
        </xsl:if>
        <xsl:text>level</xsl:text>
        <xsl:call-template name="level"/>
        <xsl:text> title</xsl:text>
        <xsl:call-template name="titleclass"/>
      </xsl:attribute>
      <span class="title_num">
	<xsl:call-template name="number"/>
      </span>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>


  <xsl:template name="level">
    <xsl:variable name="h">
      <xsl:value-of select="substring(local-name(),2,1)"/>
    </xsl:variable>
        
    <xsl:value-of select="count(ancestor::html:div[@class='section']) + 1"/>
  </xsl:template>

  <xsl:template name="titleclass">
    <xsl:variable name="h">
      <xsl:value-of select="substring(local-name(),2,1)"/>
    </xsl:variable>
    
    <xsl:value-of select="count(ancestor::html:div[@class='section']|ancestor::html:div[@class='topic']|ancestor::html:div[starts-with(@class,'INDEX')]) + $h"/>
  </xsl:template>


  <xsl:template name="number">
    <xsl:variable name="lev">
      <xsl:call-template name="titleclass"/>
    </xsl:variable>
    <!--
    <span class="title_num_level_1"><xsl:number level="any" count="html:h1[&tl;=1]|html:h2[&tl;=1]|html:h3[&tl;=1]|html:h4[&tl;=1]|html:h5[&tl;=1]|html:h6[&tl;=1]|"/></span>
    -->
    <xsl:if test="$lev &gt; 1">
      <!-- <span class="title_num_sep_2">.</span>-->
      <span class="title_num_level_2"><xsl:number level="any" from="html:h1[&tl;=1]|html:h2[&tl;=1]|html:h3[&tl;=1]|html:h4[&tl;=1]|html:h5[&tl;=1]|html:h6[&tl;=1]|" count="html:h1[&tl;=2]|html:h2[&tl;=2]|html:h3[&tl;=2]|html:h4[&tl;=2]|html:h5[&tl;=2]|html:h6[&tl;=2]|"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 2">
      <span class="title_num_sep_3">.</span>
      <span class="title_num_level_3"><xsl:number level="any" from="html:h1[&tl;=2]|html:h2[&tl;=2]|html:h3[&tl;=2]|html:h4[&tl;=2]|html:h5[&tl;=2]|html:h6[&tl;=2]|" count="html:h1[&tl;=3]|html:h2[&tl;=3]|html:h3[&tl;=3]|html:h4[&tl;=3]|html:h5[&tl;=3]|html:h6[&tl;=3]|"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 3">
      <span class="title_num_sep_4">.</span>
      <span class="title_num_level_4"><xsl:number level="any" from="html:h1[&tl;=3]|html:h2[&tl;=3]|html:h3[&tl;=3]|html:h4[&tl;=3]|html:h5[&tl;=3]|html:h6[&tl;=3]|" count="html:h1[&tl;=4]|html:h2[&tl;=4]|html:h3[&tl;=4]|html:h4[&tl;=4]|html:h5[&tl;=4]|html:h6[&tl;=4]|"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 4">
      <span class="title_num_sep_5">.</span>
      <span class="title_num_level_5"><xsl:number level="any" from="html:h1[&tl;=4]|html:h2[&tl;=4]|html:h3[&tl;=4]|html:h4[&tl;=4]|html:h5[&tl;=4]|html:h6[&tl;=4]|" count="html:h1[&tl;=5]|html:h2[&tl;=5]|html:h3[&tl;=5]|html:h4[&tl;=5]|html:h5[&tl;=5]|html:h6[&tl;=5]|"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 5">
      <span class="title_num_sep_6">.</span>
      <span class="title_num_level_6"><xsl:number level="any" from="html:h1[&tl;=5]|html:h2[&tl;=5]|html:h3[&tl;=5]|html:h4[&tl;=5]|html:h5[&tl;=5]|html:h6[&tl;=5]|" count="html:h1[&tl;=6]|html:h2[&tl;=6]|html:h3[&tl;=6]|html:h4[&tl;=6]|html:h5[&tl;=6]|html:h6[&tl;=6]|"/></span>
    </xsl:if>
    <span class="title_num_sep">.</span>
    <xsl:text>&#xA0;</xsl:text>
  </xsl:template>



</xsl:stylesheet>
