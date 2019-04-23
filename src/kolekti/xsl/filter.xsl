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
    xmlns:xt="http://ns.inria.org/xtiger"
    xmlns:kf="kolekti:extensions:functions"
    xmlns:kfp="kolekti:extensions:functions:publication"
    extension-element-prefixes="kfp kf"
    exclude-result-prefixes="html kfp kf"
    version="1.0">

  <xsl:output  method="xml" 
               indent="no"
               doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
               doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />


  <!--
      <xsl:param name="action">publish</xsl:param>
  -->

  
  <xsl:include href="filter-share.xsl"/>


  <!-- templates de remplacement des prédicats dans les chemins d'images -->

  <xsl:template match="html:a[@class='resource']/@href">
    <xsl:attribute name="href">
      <xsl:value-of select="kfp:replace_publication_criteria(string(.))" />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="html:img/@src|html:embed/@src">
    <xsl:attribute name="src">
      <xsl:value-of select="kfp:replace_publication_criteria(string(.))" />
    </xsl:attribute>
  </xsl:template>

  <!-- templates de remplacement des conditions -->

  <xsl:template match="@class[contains(.,'=')]"/>
  
  <xsl:template match="html:div[@class='topic']">    
    <xsl:variable name="children">
      <xsl:apply-templates select="node()[not(self::html:div[@class='topicinfo'])]"/>
    </xsl:variable>
    
    <xsl:if test="normalize-space(string($children))">
      <xsl:copy>
        <xsl:apply-templates select="@*"/>
        <xsl:copy-of select="html:div[@class='topicinfo']"/>
        <xsl:copy-of select="$children"/>
      </xsl:copy>
    </xsl:if>
  </xsl:template>

  <xsl:template match="html:*[contains(@class,'=')]">
    <xsl:variable name="classcond">
      <xsl:choose>
	    <xsl:when test="starts-with(@class,'cond:')">
	      <xsl:value-of select="translate(substring-after(@class,':'),' ','')"/>    
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:value-of select="translate(@class,' ','')"/>
	    </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>     

    <xsl:variable name="cond">
      <xsl:call-template name="process_list_cond">
        <xsl:with-param name="listcond" select="$classcond"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$cond='true'">
        <!--
            <xsl:comment><xsl:value-of select="$action"/><xsl:value-of select="$classcond"/> -> true</xsl:comment>
        -->
        <xsl:choose>
          <xsl:when test="self::html:div|self::html:span">
            <xsl:apply-templates select="node()"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:copy>          
              <xsl:apply-templates select="node()|@*"/>        
            </xsl:copy>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:when test="$cond='false'"/>
      
      <xsl:when test="$cond='user'">
        <!--
            <xsl:comment><xsl:value-of select="$classcond"/> -> user</xsl:comment>
        -->
	    <xsl:copy>
	      <xsl:copy-of select="@class"/>
	      <xsl:apply-templates select="node()|@*"/>
	    </xsl:copy>        
      </xsl:when>

      <xsl:when test="$cond='none'">
        <!--
            <xsl:comment><xsl:value-of select="$classcond"/> -> none</xsl:comment>
        -->
        <xsl:choose>
          <xsl:when test="self::html:div|self::html:span">
            <xsl:apply-templates select="node()"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:copy>          
              <xsl:apply-templates select="node()|@*"/>        
            </xsl:copy>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
    
  </xsl:template>

  
</xsl:stylesheet>
