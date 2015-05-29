<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  exclude-result-prefixes="v"
  version="1.0">

 <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <variables>
      <critlist>
	<xsl:apply-templates select="variables/critlist/row/hcell"/>
      </critlist>
      <xsl:apply-templates select="variables/values/row"/>
    </variables>
  </xsl:template>


  <xsl:template match="hcell" mode="listcrits">
    <crit name="{substring-after(.,':')}"/>
  </xsl:template>
  
  <xsl:template match="row">
    <xsl:message>line <xsl:value-of select="position()"/></xsl:message>
    <variable code="{substring-after(hcell,'&amp;')}">
      <xsl:apply-templates select="cell"/>
    </variable>
  </xsl:template>

  <xsl:template match="cell">
    <value>
      <xsl:variable name="pos" select="position()"/>
      <xsl:apply-templates select="/variables/critlist/row/cell[$pos]" mode="crits"/>
      <content><xsl:copy-of select="node()"/></content>
    </value>
  </xsl:template>
  
  <xsl:template match="cell" mode="crits">
    <crit name="{substring-after(preceding-sibling::hcell,':')}" value="{.}"/>
  </xsl:template>

</xsl:stylesheet>
