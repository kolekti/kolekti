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
  xmlns:kfp="kolekti:extensions:functions:publication"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />


  <xsl:param name="basepath"/>
<!--
  <xsl:param name="lang">fr</xsl:param>
-->

  <xsl:include href="textes-auto.xsl"/>


  <xsl:template match="html:head">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>    
  </xsl:template>

<!-- substitution des éléments var par la valeur d'un texte automatique -->
  <xsl:template match="html:var">
    <xsl:choose>
      <xsl:when test="contains(@class,':')">
	<!-- le texte est récupéré d'un fichier de textes auto l'attribut class est de la forme : 
	     <src>:_<critère>_ ou <src>:<entrée> src peut contenir _critère_ (en fin)-->

	<xsl:variable name="fileref">
	  <xsl:choose>
	    <xsl:when test="contains(substring-before(@class,':'),'_')">
	      <xsl:value-of select="substring-before(@class,'_')"/>
	      <xsl:variable name="critname">
		<xsl:value-of select="substring-before(substring-after(@class,'_'),'_')"/>
	      </xsl:variable>
	      <xsl:value-of select="/html:html/html:head/html:meta[@scheme='condition'][@name=$critname]/@content"/>
	    </xsl:when>

	    <xsl:otherwise>
	      <xsl:value-of select="substring-before(@class,':')"/>
	    </xsl:otherwise>
	  </xsl:choose>
	</xsl:variable>

	<xsl:variable name="varref">
	  <xsl:variable name="varid">
	    <xsl:value-of select="substring-after(@class,':')"/>
	  </xsl:variable>
	  <xsl:choose>
	    <xsl:when test="starts-with($varid,'_') and substring($varid,string-length($varid))='_'">
	      <!-- la class est de la forme : <src>:_<critère>_ on va chercher dans le fichier src, 
		   la ligne correspondant à la valeur du critère pour cette publication-->
	      <xsl:variable name="critname">
		<xsl:value-of select="substring-before(substring-after($varid,'_'),'_')"/>
	      </xsl:variable>
	      <xsl:value-of select="/html:html/html:head/html:meta[@scheme='condition'][@name=$critname]/@content"/>
	    </xsl:when>
	    <xsl:otherwise>
	      <!-- la class est de la forme : <src>:<entree> on va chercher dans le fichier src,
	      la ligne &entree -->
	      <xsl:value-of select="$varid"/>
	    </xsl:otherwise>
	  </xsl:choose>	    
	</xsl:variable>	

	<xsl:call-template name="getvariable">
	  <xsl:with-param name="varcode" select="concat($fileref,':',$varref)"/>
	</xsl:call-template>
      </xsl:when>

      <xsl:otherwise>
	<!-- l'attribut class est de la forme <critère> : on substitue avec la valeur du critère -->
	<xsl:choose>
	  <xsl:when test="/html:html/html:head/html:meta[@scheme='condition'][@name=current()/@class]">
	    <xsl:value-of select="/html:html/html:head/html:meta[@scheme='condition'][@name=current()/@class]/@content"/>
	  </xsl:when>
	  <xsl:otherwise>
	    <xsl:text>[variable </xsl:text>
	    <xsl:value-of select="@class"/>
	    <xsl:text> non définie]</xsl:text>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
