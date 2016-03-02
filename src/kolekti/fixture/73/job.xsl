<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns:html="http://www.w3.org/1999/xhtml" 
  version="1.0">

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="script">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <label><xsl:value-of select="@name"/></label>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>    
  
</xsl:stylesheet>
