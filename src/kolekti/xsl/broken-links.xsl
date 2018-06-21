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

  <!-- associe a chaque element portant un attribut id, la valeur de ce attribut -->
  <xsl:key name="id" match="*[@id]" use="@id"/>
  <xsl:key name="id" match="html:a[@name]" use="@name"/>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- supprime la meta processedid -->
  <xsl:template match='html:meta[@name="kolekti:processedid"][@content="yes"]'/>
  
  <xsl:template match="html:div[@class='topicinfo']">
    <xsl:copy-of select="."/>
  </xsl:template>


  <!--traitement des liens -->
  <xsl:template match="html:a[@href]">
    <xsl:copy>
      <!-- calcul du nouveau lien -->
      <xsl:choose>      
        <!-- lien externe -->
        <xsl:when test="starts-with(@href,'http://') or starts-with(@href,'https://')">
          <xsl:apply-templates select="@*" />
        </xsl:when>

        <!-- lien vers resource -->
        <xsl:when test="@class='resource'">
          <xsl:apply-templates select="@*" />
        </xsl:when>
        
        <!-- lien interne a l'assemblage -->
        <xsl:when test="starts-with(@href, '#')">
          <xsl:choose>
            <xsl:when test="key('id', substring-after(@href,'#'))">
              <xsl:apply-templates select="@*" />
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="brokenlink"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>

        <xsl:otherwise>
          <xsl:call-template name="brokenlink"/>
        </xsl:otherwise>
      </xsl:choose>
      
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template name="brokenlink">
    <xsl:if test="not(@class)">
      <xsl:attribute name="class">
        <xsl:text>brokenlink</xsl:text>
      </xsl:attribute>
    </xsl:if>
    
    <xsl:apply-templates select="@*" mode="brokenlink"/>
    <xsl:comment>
	  ref <xsl:value-of select="@href"/>
    </xsl:comment>
  </xsl:template>

  <xsl:template match="@href" mode="brokenlink">
    <xsl:attribute name="href">#</xsl:attribute>
  </xsl:template>

  <xsl:template match="@class" mode="brokenlink">
    <xsl:attribute name="class"><xsl:value-of select="."/> brokenlink</xsl:attribute>
  </xsl:template>

  <xsl:template match="@*" mode="brokenlink">
    <xsl:copy/>
  </xsl:template>
  
</xsl:stylesheet>
