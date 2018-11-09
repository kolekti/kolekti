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
  xmlns:diff="http://namespaces.shoobx.com/diff" 
  exclude-result-prefixes="html"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
	           omit-xml-declaration="yes"
	           />

  <xsl:include href="django_variables.xsl"/>
  <xsl:include href="django_conditions.xsl"/> 
  <xsl:include href="django_tables.xsl"/>
  <xsl:include href="django_identity.xsl"/>
  <xsl:include href="django_pictures.xsl"/>


  <xsl:template match="/">
    <div class="topicdiffsource col-md-12">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  
  <xsl:template match="@diff:insert">
    <xsl:attribute name="data-diff">insert</xsl:attribute>
  </xsl:template>
  
  <xsl:template match="diff:insert">
    <span data-diff="insert">
      <xsl:apply-templates/>
    </span>
  </xsl:template>
  
  <xsl:template match="diff:delete">
    <span data-diff="delete">
      <xsl:apply-templates/>
    </span>
  </xsl:template>
  
  <xsl:template match="@diff:delete">
    <xsl:attribute name="data-diff">delete</xsl:attribute>
  </xsl:template>
  
  <xsl:template match="@diff:rename">
    <xsl:attribute name="data-diff">rename</xsl:attribute>
    <xsl:attribute name="data-diff-elt"><xsl:value-of select="."/></xsl:attribute>
  </xsl:template>
  

  
</xsl:stylesheet>
