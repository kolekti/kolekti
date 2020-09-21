<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:h="http://www.w3.org/1999/xhtml"
  xmlns:e="kolekti:extensions:functions:publication"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:k = "http://www.exselt.com/ns/kolekti"
  exclude-result-prefixes="h e k"
  version="1.0">
  
  <xsl:template match="node()|@*" name="id">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="h:img">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="alt">image</xsl:attribute>
    </xsl:copy>

    <xsl:apply-templates select="e:picture_info(string(@src))"/>

  </xsl:template>

  <xsl:template match="k:imageinfo[@error]">
    <p>////// MANQUANTE (image non trouvée) //////</p>
  </xsl:template>
  
  <xsl:template match="k:imageinfo">
    <xsl:value-of select="@hash"/>
    <xsl:text>(</xsl:text>
    <xsl:value-of select="@fileweight"/>
    <xsl:text>o </xsl:text>
    <xsl:value-of select="@format"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="@mode"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="@size"/>
    <xsl:text>px</xsl:text>
    <xsl:if test="@dpi">
      <xsl:text> dpi:</xsl:text>
      <xsl:value-of select="@dpi"/>
    </xsl:if>
    <xsl:text>)</xsl:text>
  </xsl:template>
  
</xsl:stylesheet>
