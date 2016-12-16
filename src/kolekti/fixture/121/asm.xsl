<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:html="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="html"
  version="1.0">

  <xsl:output  method="xml"
    indent="yes"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:div[@class='topicinfo']/html:p[html:span[@class='infolabel' and text() = 'localsource']]">
    <xsl:variable name="src">
      <xsl:value-of select="html:span/html:a/@href"/>
    </xsl:variable>
    <p>
      <span class="infolabel">localsource</span>
      <span class="infovalue"><a href="{$src}"><xsl:value-of select="$src"/></a></span>
    </p>
    <p>
      <span class="infolabel">source</span>
      <span class="infovalue"><a href="/sources/{substring-after($src,'/sources/')}">/sources/<xsl:value-of select="substring-after($src,'/sources/')"/></a></span>
    </p>
  </xsl:template>

</xsl:stylesheet>
