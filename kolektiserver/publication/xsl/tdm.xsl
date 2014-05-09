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
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="node()|@*" mode="titletdm">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="titletdm"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:span[@rel='index']|html:ins[@class='index']|html:a[@class='indexmq']" mode="titletdm"/>

  <xsl:template match="html:div[@class='TDM']">
    <div class="TDM">
      <xsl:apply-templates select="html:*[@class='TDM_titre']" mode="maintitle" />
      <div class="TDM_corps">
	<xsl:apply-templates select="/html:html/html:body" mode="tdm"/>
      </div>
    </div>
  </xsl:template>


  <xsl:template match="html:*[@class='TDM_titre']" mode="maintitle">
    <p class="TDM_titre">
      <xsl:apply-templates />
    </p>
  </xsl:template>
  
  <xsl:template match="html:*[@class='TDM_titre']" mode="tdm"> </xsl:template>

  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6" mode="tdm">
    <xsl:variable name="lev">
      <xsl:value-of select="substring-after(name(),'h')"/>
    </xsl:variable>
    <p class="TDM_niveau_{$lev}">
      <span class="title_num">
	<xsl:call-template name="number"/>
      </span>
      <xsl:choose>
	<xsl:when test="@id">
	  <a href="#{@id}"><xsl:apply-templates  mode="titletdm"/></a>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates  mode="titletdm"/>
	</xsl:otherwise>
      </xsl:choose>
    </p>
  </xsl:template>

  <xsl:template match="text()" mode="tdm"/>



  <xsl:template match="html:h1|html:h2|html:h3|html:h4|html:h5|html:h6">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <span class="title_num">
	<xsl:call-template name="number"/>
      </span>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

  <xsl:template name="number">
    <xsl:variable name="lev">
      <xsl:value-of select="substring-after(name(),'h')"/>
    </xsl:variable>
    <span class="title_num_level_1"><xsl:number level="any" count="html:h1"/></span>
    <xsl:if test="$lev &gt; 1">
      <span class="title_num_sep_2">.</span>
      <span class="title_num_level_2"><xsl:number level="any" from="html:h1" count="html:h2"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 2">
      <span class="title_num_sep_3">.</span>
      <span class="title_num_level_3"><xsl:number level="any" from="html:h2" count="html:h3"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 3">
      <span class="title_num_sep_4">.</span>
      <span class="title_num_level_4"><xsl:number level="any" from="html:h3" count="html:h4"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 4">
      <span class="title_num_sep_5">.</span>
      <span class="title_num_level_5"><xsl:number level="any" from="html:h4" count="html:h5"/></span>
    </xsl:if>
    <xsl:if test="$lev &gt; 5">
      <span class="title_num_sep_6">.</span>
      <span class="title_num_level_6"><xsl:number level="any" from="html:h5" count="html:h6"/></span>
    </xsl:if>
    <span class="title_num_sep">.</span>
    <xsl:text>&#xA0;</xsl:text>
  </xsl:template>

</xsl:stylesheet>
