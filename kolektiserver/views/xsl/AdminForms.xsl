<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kcd="kolekti:ctrdata"

                exclude-result-prefixes="i kcd">

  <xsl:template name="status">
      <xsl:apply-templates select="/kcd:view/kcd:data/kcd:namespace[@id='status']" mode="status"/>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='status']"/>
  <xsl:template match="kcd:namespace[@id='status']" mode="status">
    <p>
      <xsl:attribute name="class">
	<xsl:text> formstatus </xsl:text>
   <xsl:choose>
      <xsl:when test="kcd:value[@key='error']"><xsl:text>error</xsl:text></xsl:when>
      <xsl:otherwise><xsl:text>ok</xsl:text></xsl:otherwise>
   </xsl:choose>
      </xsl:attribute>
      <xsl:choose>
   <xsl:when test="not(kcd:value[@key='ok'] = '')"><xsl:apply-templates/></xsl:when>
	<xsl:when test="not(kcd:value[@key='error'])"><i:text>[0102]Modifications enregistrées</i:text></xsl:when>
	<xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
      </xsl:choose>
    </p>
  </xsl:template>
</xsl:stylesheet>
