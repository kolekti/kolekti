<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:f="kolekti:migrate"
  extension-element-prefixes="f"
  exclude-result-prefixes="html f"
  >
  <xsl:output method="xml" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />
  <xsl:namespace-alias stylesheet-prefix="html" result-prefix="#default"/>


  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:var">
    <var>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </var>
  </xsl:template>
  
  <xsl:template match="html:img">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="src">
        <xsl:value-of select="f:img_path(string(@src))"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="html:a[@href]">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="href">
        <xsl:value-of select="f:link_path(string(@href))"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>
  


  
</xsl:stylesheet>
