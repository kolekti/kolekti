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
  xmlns:kf="kolekti:extensions:functions:publication"
  exclude-result-prefixes="kf html"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
	       
	       doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	       doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	       />

  
  <xsl:template match="text()|@*">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="*[not(namespace-uri(self::*)='')]">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="node()">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>



  <xsl:template match="/html">
    <html xmlns="http://www.w3.org/1999/xhtml" >
      <head>
	<xsl:apply-templates select="body/div/div[@id='kolekti_meta']/ul/li" mode="meta"/>
      </head>
      <body>
	<xsl:apply-templates select="body/div/div[@id='kolekti_body']/*"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="li[@data-tag='meta']" mode="meta">
    <meta>
      <xsl:if test="@data-name != 'None'">
	<xsl:attribute name="name">
	  <xsl:value-of select="@data-name"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-content != 'None'">
	<xsl:attribute name="content">
	  <xsl:value-of select="@data-content"/>
	</xsl:attribute>
      </xsl:if>
    </meta>
  </xsl:template>

  <xsl:template match="li[@data-tag='title']" mode="meta">
    <title>
      <xsl:value-of select="@data-title"/>
    </title>
  </xsl:template>

  <xsl:template match="li[@data-tag='link']" mode="meta">
    <link>
      <xsl:if test="@data-rel != 'None'">
	<xsl:attribute name="rel">
	  <xsl:value-of select="@data-rel"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-type != 'None'">
	<xsl:attribute name="type">
	  <xsl:value-of select="@data-type"/>
	</xsl:attribute>
      </xsl:if>
      <xsl:if test="@data-href != 'None'">
	<xsl:attribute name="href">
	  <xsl:value-of select="@data-href"/>
	</xsl:attribute>
      </xsl:if>
    </link>
  </xsl:template>

</xsl:stylesheet>