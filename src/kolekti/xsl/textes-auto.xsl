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
    <xsl:variable name="res" select="kfp:variable($varfile,$varname)"/>


  
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
