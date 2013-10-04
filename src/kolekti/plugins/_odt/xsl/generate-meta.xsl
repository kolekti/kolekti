<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
		xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" 
		xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
		xmlns:html="http://www.w3.org/1999/xhtml"
		exclude-result-prefixes="html"
		>
  <xsl:output indent="yes"/>
  <xsl:param name="pivot"/>

  <xsl:template match="/office:document-meta">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="/office:document-meta//node() | /office:document-meta//@*" priority="-1">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="office:meta">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
      <!--
      <xsl:apply-templates select="document($pivot)/html:html/html:head/html:meta[@scheme='condition']"/>
      -->
      <xsl:apply-templates select="document($pivot)/html:html/html:body//html:p[starts-with(@class,'k ')]"/>
    </xsl:copy>

  </xsl:template>
  <xsl:template match="meta:user-defined"/>

  <xsl:template match="html:meta">
    <meta:user-defined meta:name="{@name}"><xsl:value-of select="@content"/></meta:user-defined>
  </xsl:template>

  <xsl:template match="html:p[starts-with(@class,'k ')]">
    <meta:user-defined meta:name="{substring-after(@class,'k ')}"><xsl:value-of select="."/></meta:user-defined>
  </xsl:template>



</xsl:stylesheet>