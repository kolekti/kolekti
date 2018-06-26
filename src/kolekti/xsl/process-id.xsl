<?xml version="1.0" encoding="utf-8"?>
<!--
     kOLEKTi : a structural documentation generator
     Copyright (C) 2007 StÃ©phane Bonhomme (stephane@exselt.com)

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
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:kfp="kolekti:extensions:functions:publication"
  exclude-result-prefixes="htm kfp"
  version="1.0">

  <xsl:output  method="xml"
    indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <!-- associe a chaque element topic son path source -->
  <xsl:key name="modref" match="//html:div[@class='topic']" use="string(html:div[@class='topicinfo']/html:p[html:span[@class='infolabel' and text() = 'source']]/html:span[@class='infovalue']/html:a/@href)"/>


  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- cree la meta processedid -->
  
  <xsl:template match='html:head'>
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
      <meta name="kolekti:processedid" content="yes"/>
    </xsl:copy>
  </xsl:template>
  
  
  <xsl:template match="html:div[@class='topicinfo']">
    <xsl:copy-of select="."/>
  </xsl:template>


  <!-- change les id en les prefixant avec l'id du topic -->
  
  <xsl:template match="html:div[@class='topic']//*[@id]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="id">
        <xsl:text>topic_</xsl:text>
        <xsl:value-of select="generate-id(ancestor::html:div[@class='topic'][1])"/>
        <xsl:text>_</xsl:text>
        <xsl:value-of select="@id"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
  <!-- genere un attribut id sur les topics -->
  <xsl:template match="html:div[@class='topic']">
    <xsl:copy>
      <xsl:attribute name="id">
        <xsl:text>topic_</xsl:text>
        <xsl:value-of select="generate-id()"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- supprime tous attributs id existant sur les elements topic  -->
  <xsl:template match="html:div[@class='topic']/@id"/>

  
  <!--traitement des liens -->
  <xsl:template match="html:a[@href]">

    <!-- path du topic source -->
    <xsl:variable name="modpath" select="ancestor::html:div[@class='topic']/html:div[@class='topicinfo']/html:p[html:span[@class='infolabel' and text() = 'source']]/html:span[@class='infovalue']/html:a/@href" />
    <xsl:variable name="lhref" select="@href"/>

    <!-- url du topic cible -->
    <xsl:variable name="tmod">
      <xsl:choose>
        <xsl:when test="contains($lhref,'#')">
          <xsl:value-of select="substring-before($lhref,'#')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$lhref"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    
    <!-- calcul du nouveau lien -->
    <xsl:variable name="href">
      <xsl:choose>
        
        <!-- lien vers resource -->
        <xsl:when test="@class='resource'">
          <xsl:value-of select="@href" />
        </xsl:when>
        
        <!-- lien externe -->
        <xsl:when test="starts-with(@href,'http://') or starts-with(@href,'https://')">
          <xsl:value-of select="@href" />
        </xsl:when>
        
        <!-- lien interne au topic -->
        <xsl:when test="starts-with(@href, '#')">
          <xsl:text>#</xsl:text>
          <xsl:text>topic_</xsl:text>
          <xsl:value-of select="generate-id(ancestor::html:div[@class='topic'])"/>
          <xsl:text>_</xsl:text>
          <xsl:value-of select="substring-after(@href,'#')"/>
        </xsl:when>

        <!-- lien absolu (/sources/[lg]/topics/... -->
        <xsl:when test="starts-with($tmod, '/')">
	      <xsl:variable name="ref" select="$tmod" />
          <xsl:variable name="refid" select="generate-id(key('modref',string($ref)))"/>
          <xsl:text>#</xsl:text>
          <xsl:if test="$refid!=''">
            <xsl:text>topic_</xsl:text>
            <xsl:value-of select="$refid"/>
            <xsl:if test="contains(@href,'#') and not(@href='#')">
              <xsl:text>_</xsl:text>
              <xsl:value-of select="substring-after(@href,'#')"/>
            </xsl:if>
          </xsl:if>
        </xsl:when>

        <!-- lien relatif -->
        <xsl:otherwise>
	      <!-- calcul du chemin absolu de la référence -->
	      <xsl:variable name="ref" select="kfp:normpath( string($tmod),string($modpath))" />
          <xsl:variable name="refid" select="generate-id(key('modref',string($ref)))"/>
          <xsl:text>#</xsl:text>
          <xsl:if test="$refid!=''">
            <xsl:text>topic_</xsl:text>
            <xsl:value-of select="$refid"/>
            <xsl:if test="contains(@href,'#') and not(@href='#')">
              <xsl:text>_</xsl:text>
              <xsl:value-of select="substring-after(@href,'#')"/>
            </xsl:if>
          </xsl:if>
        </xsl:otherwise>
        
      </xsl:choose>
    </xsl:variable>

    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="href">
        <xsl:value-of select="$href"/>
      </xsl:attribute>
      <xsl:if test="$href='#'">
        <!-- add class="brokenlink" if link is broken -->
        <xsl:attribute name="class">
          <xsl:if test="@class">
            <xsl:value-of select="@class"/>
            <xsl:text> </xsl:text>
          </xsl:if>
          <xsl:text>brokenlink</xsl:text>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
    
  </xsl:template>

  <xsl:template match="html:a/@href"/>

  <xsl:template match="html:a[@name]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="name">
        <xsl:text>topic_</xsl:text>
        <xsl:value-of select="generate-id(ancestor::html:div[@class='topic'])"/>
        <xsl:text>_</xsl:text>
        <xsl:value-of select="@name"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:h1|html:h2|html:h3">
    <xsl:copy>
      <xsl:if test="not(@id)">
        <xsl:attribute name="id">
          <xsl:value-of select="generate-id()"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
