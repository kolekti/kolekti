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
  xmlns:exsl="http://exslt.org/common"
  xmlns:kfp="kolekti:extensions:functions:publication"
  extension-element-prefixes="exsl kfp"
  exclude-result-prefixes="html kfp"
  version="1.0">

  <!-- retourne la valeur de la variable 'varcode' -->
  
  <xsl:template name="getvariable">
    <xsl:param name="varcode"/>

    <!-- calcul du nom de ficher texte auto -->
    <xsl:variable name="varfile" select="substring-before($varcode,':')"/>

    <!-- récupère le nom local de la variable -->
    <xsl:variable name="varname">
      <xsl:value-of select="substring-after($varcode,':')"/>
    </xsl:variable>

    <!-- ensemble des valeurs de conditions pour le document publié -->
    <xsl:variable name="crits" select="/html:html/html:head/html:meta[@scheme='condition']"/>

    <!-- on calcul la valeur de la variable -->
    <xsl:variable name="res">
      <!-- boucle sur les valeurs conditionnées pour cette variable dans le texte auto -->
      <xsl:for-each select="kfp:variables($varfile)/html:variable[@code=$varname]/html:value">
	<xsl:variable name="checkconds"><!-- chaine 0/1 des evaluations -->
	  <!-- pour chaque critère exprimé dans la definition de valeur conditionnée de la variable--> 
	  <xsl:for-each select="html:crit">
	    <xsl:variable name="critval">
	      <xsl:value-of select="$crits[@name=current()/@name]/@content"/>
	    </xsl:variable>
	    <xsl:choose>
	      <!-- le critère n'est pas exprimé dans le doc : on accepte -->
	      <xsl:when test="$critval=''">1</xsl:when>
	      <!-- le critère est égale (contient) à la valeur de la condition : on accepte -->
	      <xsl:when test="$critval=normalize-space(@value)">1</xsl:when>
	      <xsl:when test="contains(concat(',',translate(@value,' ',''),','),concat(',',$critval,','))">1</xsl:when>
	      <!-- sinon : on refuse -->
	      <xsl:otherwise>0</xsl:otherwise>
	    </xsl:choose>
	  </xsl:for-each>
	</xsl:variable>

	<!-- on teste si un des critères rejete la condition -->
	<xsl:if test="not(contains($checkconds,'0'))">
	  <xsl:copy-of select="html:content/node()"/>
	</xsl:if>
      </xsl:for-each>
    </xsl:variable>

  
    <xsl:choose>
      <xsl:when test="$res!=''">
        <xsl:copy-of select="$res"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>[??]</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
