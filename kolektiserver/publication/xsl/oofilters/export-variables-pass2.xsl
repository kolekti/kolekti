<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:v="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="v"
  version="1.0">

 <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <variables>
      <critlist>
	<xsl:apply-templates select="v:variables/v:critlist/v:row/v:hcell"/>
      </critlist>
      <xsl:apply-templates select="v:variables/v:values/v:row"/>
    </variables>
  </xsl:template>


  <xsl:template match="v:hcell" mode="listcrits">
    <crit name="{substring-after(.,':')}"/>
  </xsl:template>
  
  <xsl:template match="v:row">
    <xsl:message>line <xsl:value-of select="position()"/></xsl:message>
    <variable code="{substring-after(v:hcell,'&amp;')}">
      <xsl:apply-templates select="v:cell"/>
    </variable>
  </xsl:template>

  <xsl:template match="v:cell">
    <value>
      <xsl:variable name="pos" select="position()"/>
      <xsl:apply-templates select="/v:variables/v:critlist/v:row/v:cell[$pos]" mode="crits"/>
      <content><xsl:copy-of select="node()"/></content>
    </value>
  </xsl:template>
  
  <xsl:template match="v:cell" mode="crits">
    <crit name="{substring-after(preceding-sibling::v:hcell,':')}" value="{.}"/>
  </xsl:template>

</xsl:stylesheet>
