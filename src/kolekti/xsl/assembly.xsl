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
  xmlns:kfp="kolekti:extensions:functions:publication"
  extension-element-prefixes="exsl kfp" 
  exclude-result-prefixes="html kfp kt"
  version="1.0">

  <xsl:output  method="xml" 
               indent="yes"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <!-- parametres d'entrée : langue et basepath -->
  <xsl:param name="lang"/>
  <xsl:param name="title"/>

  <xsl:template match="/">
    <xsl:apply-templates mode="aggreg"/>
  </xsl:template>
 
  <!-- trames 0.6 -->

  <xsl:template match="kt:trame" mode="aggreg">
    <html>
      <head>
        <title>
          <xsl:call-template name="titlecontent">
            <xsl:with-param name="titlestr" select="$title"/>
          </xsl:call-template>
         </title>
      </head>
      <body lang="{$lang}" xml:lang="{$lang}">
        <xsl:apply-templates select="kt:body" mode="aggreg">
          <xsl:with-param name="section_depth" select="'0'"/>
        </xsl:apply-templates>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="kt:body" mode="aggreg">
    <xsl:param name="section_depth"/>
    <xsl:apply-templates mode="aggreg">
      <xsl:with-param name="section_depth" select="$section_depth"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- traitement d'une section -->
  <xsl:template match="kt:section" mode="aggreg">
    <xsl:param name="section_depth"/>
    <div class="section">
      <xsl:apply-templates mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth+1"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>


  <!-- traitement d'un titre de section -->
  <xsl:template match="kt:section/kt:title" mode="aggreg">
    <xsl:param name="section_depth"/>
    <xsl:variable name="hx">
      <xsl:choose>
        <xsl:when test="$section_depth &lt; 6">
          <xsl:text>h</xsl:text>
          <xsl:value-of select="$section_depth"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>h6</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:element name="{$hx}">
      <xsl:apply-templates mode="aggreg"/>
    </xsl:element>
 </xsl:template>



  <!-- si le titre est un texte : on le copie simplement -->
  <xsl:template match="kt:section/kt:title/text()" mode="aggreg">
    <xsl:call-template name="titlecontent">
      <xsl:with-param name="titlestr" select="."/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="titlecontent">
    <xsl:param name="titlestr"/>
    <xsl:choose>
      <xsl:when test="contains($titlestr,'[var')">
        <xsl:value-of select="substring-before($titlestr,'[var')"/>
        <var>
          <xsl:attribute name="class">
            <xsl:value-of select="substring-before(substring-after($titlestr,'[var '),']')"/>
          </xsl:attribute>
        </var>
        <xsl:call-template name="titlecontent">
          <xsl:with-param name="titlestr" select="substring-after(substring-after($titlestr,'[var '),']')"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$titlestr"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- si le titre est variable : crée la balise var -->
  <xsl:template match="kt:section/kt:title/kt:var" mode="aggreg">
    <var>
      <xsl:attribute name="class">
        <xsl:value-of select="@code"/>
      </xsl:attribute>
    </var>
  </xsl:template>






  <!-- trames 0.7 -->

  <xsl:template match="html:*" mode="aggreg">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="aggreg"/>
    </xsl:copy>
 </xsl:template>


  <xsl:template match="html:html" mode="aggreg">
    <html>
      <head>
        <title>
          <xsl:copy-of select="html:head/html:title/text()"/>
         </title>
      </head>
      <body lang="{$lang}" xml:lang="{$lang}">
        <xsl:apply-templates select="html:body" mode="aggreg">
          <xsl:with-param name="section_depth" select="'0'"/>
        </xsl:apply-templates>
      </body>
    </html>
  </xsl:template>




  <xsl:template match="html:body" mode="aggreg">
    <xsl:param name="section_depth"/>
    <xsl:apply-templates mode="aggreg">
      <xsl:with-param name="section_depth" select="$section_depth"/>
    </xsl:apply-templates>
  </xsl:template>

  
  <!-- traitement d'une section -->
  <xsl:template match="html:section|html:div[@class='section']" mode="aggreg">
    <xsl:param name="section_depth"/>
    <div class="section">
      <xsl:apply-templates mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth+1"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>


  <xsl:template match="html:a[@role = 'kolekti:include']" mode="aggreg" >
    <xsl:param name="section_depth"/>
    
    <xsl:variable name="modurl" select="kfp:getmodule(string(@href))"/>
    <xsl:variable name="module" select="document($modurl)"/>

    <div class="module" id="{generate-id()}">
      <div class="moduleinfo">
         <xsl:comment>Do not translate</xsl:comment>
         <p><span class="infolabel">source</span><span class="infovalue"><a href="{$modurl}"><xsl:value-of select="$modurl"/></a></span></p>
         <xsl:apply-templates select="$module/html:html/html:head/html:meta" mode="module_info"/>
      </div>

      <xsl:apply-templates select="$module/html:html/html:body" mode="aggreg">
	<xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>



  <!-- traitement des modules -->

  <xsl:template match="kt:module[@resid='kolekti://TDM']" mode="aggreg" >
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

    <div class='TDM'>
      <xsl:element name="p">
        <xsl:attribute name="class">TDM_titre</xsl:attribute>
        <var class="kolektitext:TOC"/>
      </xsl:element>
    </div>
  </xsl:template>

  <xsl:template match="kt:module[@resid='kolekti://INDEX']" mode="aggreg" >
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

    <div class='INDEX'>
      <xsl:element name="{$hx}">
        <xsl:attribute name="class">INDEX_titre</xsl:attribute>
        <var class="kolektitext:INDEX"/>
      </xsl:element>
    </div>
  </xsl:template>


  <xsl:template match="kt:module[@resid='kolekti://REVNOTES']" mode="aggreg" >
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

    <div class='REVNOTES'>
      <xsl:element name="{$hx}">
        <xsl:attribute name="class">REVNOTES_titre</xsl:attribute>
        <var class="kolektitext:REVNOTES"/>
      </xsl:element>
    </div>
  </xsl:template>

  <xsl:template match="kt:module" mode="aggreg" >
    <xsl:param name="section_depth"/>
    
    <xsl:variable name="modurl" select="kfp:getmodule(string(@resid))"/>
    <xsl:variable name="module" select="document($modurl)"/>

    <div class="module" id="{generate-id()}">
      <div class="moduleinfo">
         <xsl:comment>Do not translate</xsl:comment>
         <p><span class="infolabel">source</span><span class="infovalue"><a href="{$modurl}"><xsl:value-of select="$modurl"/></a></span></p>
         <xsl:apply-templates select="$module/html:html/html:head/html:meta" mode="module_info"/>
      </div>

      <xsl:apply-templates select="$module/html:html/html:body" mode="aggreg">
	<xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>











  <xsl:template match="html:meta[@name]" mode="module_info">
    <p><span class="infolabel"><xsl:value-of select="@name"/></span><span class="infovalue"><xsl:value-of select="@content"/></span></p>
  </xsl:template>



  <!-- traitement des titres des modules : dépendent du niveau de sections -->
  <xsl:template match="html:h1" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:choose>
      <xsl:when test="$section_depth=0">
        <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </xsl:copy>
      </xsl:when>
      <xsl:when test="$section_depth=1">
        <h2>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h2>
      </xsl:when>
      <xsl:when test="$section_depth=2">
        <h3>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>
        </h3>
      </xsl:when>
      <xsl:when test="$section_depth=3">
        <h4>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>
        </h4>
      </xsl:when>
      <xsl:when test="$section_depth=4">
        <h5>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>
        </h5>
      </xsl:when>
      <xsl:otherwise>
        <h6>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html:h2" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:choose>
      <xsl:when test="$section_depth=0">
        <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </xsl:copy>
      </xsl:when>
      <xsl:when test="$section_depth=1">
        <h3>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h3>
      </xsl:when>
      <xsl:when test="$section_depth=2">
        <h4>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h4>
      </xsl:when>
      <xsl:when test="$section_depth=3">
        <h5>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h5>
      </xsl:when>
      <xsl:otherwise>
        <h6>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html:h3" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:choose>
      <xsl:when test="$section_depth=0">
        <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </xsl:copy>
      </xsl:when>
      <xsl:when test="$section_depth=1">
        <h4>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h4>
      </xsl:when>
      <xsl:when test="$section_depth=2">
        <h5>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h5>
      </xsl:when>
      <xsl:otherwise>
        <h6>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html:h4" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:choose>
      <xsl:when test="$section_depth=0">
        <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </xsl:copy>
      </xsl:when>
      <xsl:when test="$section_depth=1">
        <h5>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h5>
      </xsl:when>
      <xsl:otherwise>
        <h6>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="html:h5" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:choose>
      <xsl:when test="$section_depth=0">
        <xsl:copy>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <h6>
          <xsl:apply-templates select="node()|@*" mode="aggreg"/>          
        </h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- traitement du corps du module -->

  <xsl:template match="html:body" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:apply-templates select="node()" mode="aggreg">
      <xsl:with-param name="section_depth" select="$section_depth"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- copie tous les noeuds des modules -->

  <xsl:template match="node()|@*" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:copy>
      <xsl:apply-templates select="node()|@*" mode="aggreg">
        <xsl:with-param name="section_depth" select="$section_depth"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>


  <!-- illustrations : cree la référence dans le sous-repertoire illustrations du repertoire de publication -->
<!--
  <xsl:template match="html:img|html:embed" mode="aggreg">
    <xsl:param name="section_depth"/>    
    <xsl:copy>
      <xsl:apply-templates select="@*" mode="aggreg"/>
      <xsl:attribute name="src">
        <xsl:choose>
         <xsl:when test="starts-with(@src, 'http://')">
            <xsl:value-of select="@src" />
         </xsl:when>
         <xsl:otherwise>
           <xsl:call-template name="remove_pdir">
             <xsl:with-param name="src" select="@src"/>
           </xsl:call-template>
         </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:img/@src" mode="aggreg"/>
-->
  <!-- marques d'index : normalize le contenu des entrées -->

  <xsl:template match="html:ins[@class='index']|html:span[@rel='index']" mode="aggreg">
    <xsl:copy>
      <xsl:apply-templates select="@*" mode="aggreg"/>
      <xsl:value-of select="normalize-space(.)"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template name="remove_pdir">
    <xsl:param name="src"/>
    <xsl:choose>
      <xsl:when test="contains($src,'/illustrations/')">
    <xsl:text>illustrations/</xsl:text>
    <xsl:value-of select="substring-after($src,'/illustrations/')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$src"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
