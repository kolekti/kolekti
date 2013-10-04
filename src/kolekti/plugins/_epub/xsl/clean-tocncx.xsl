<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns="http://www.daisy.org/z3986/2005/ncx/"
      xmlns:ncx="http://www.daisy.org/z3986/2005/ncx/"
      xmlns:exsl="http://exslt.org/common"
      
      extension-element-prefixes="exsl"
      exclude-result-prefixes="html ncx">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  
  <xsl:key name="navmap" match="ncx:navPoint" use="@playOrder" />
  
  <xsl:template match="node()|@*">
   <xsl:copy>
      <xsl:apply-templates select="node()|@*" />
   </xsl:copy>
  </xsl:template>
  
  <xsl:template match="ncx:navPoint">
   <xsl:if test="generate-id() = generate-id(key('navmap', @playOrder)[1])">
      <navPoint id="{@id}" playOrder="{@playOrder}">
         <xsl:apply-templates/>
      </navPoint>
   </xsl:if>  
  </xsl:template>
</xsl:stylesheet>
