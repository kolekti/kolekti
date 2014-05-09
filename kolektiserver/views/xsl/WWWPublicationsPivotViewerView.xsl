<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"

                extension-element-prefixes="ke"
                exclude-result-prefixes="html i kf ke kcd kd">

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />

  <xsl:template match="node()|@*">
   <xsl:copy>
      <xsl:apply-templates select="node()|@*" />
   </xsl:copy>
  </xsl:template>

  <xsl:template match="/">
   <xsl:apply-templates select="kcd:view/kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']" />
  </xsl:template>

  <xsl:template match="kcd:view/kcd:data/kcd:namespace[@id='http']/kcd:value[@key='body']">
   <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="html:div[@class='moduleinfo']//html:span[@class='infovalue']">
   <xsl:choose>
      <xsl:when test="preceding-sibling::html:span[@class='infolabel'][1]/text() = 'source'">
         <xsl:apply-templates select="html:a" mode="sourcelink" />
      </xsl:when>
      <xsl:otherwise>
         <xsl:copy-of select="." />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:template>

  <xsl:template match="html:a[not(contains(@href, '#'))]" mode="sourcelink">
   <xsl:variable name="modpath" select="substring-after(@href, '/modules/')" />
   <a href="/projects/{$project/@directory}/modules?open={$modpath}"><xsl:apply-templates /></a>
  </xsl:template>
</xsl:stylesheet>
