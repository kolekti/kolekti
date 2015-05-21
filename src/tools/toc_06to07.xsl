<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:t="kolekti:trames"
  xmlns:f="kolekti:migrate"
  extension-element-prefixes="f"
>

  <xsl:template match="/t:trame">
    <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;
</xsl:text>
    <html>
  <head>
    <title><xsl:value-of select="f:translate(string(t:head/t:title))"/></title>
    <meta name="kolekti.pubdir" content="{f:fsname(string(t:head/t:title))}"/>
    <meta name="kolekti.jobpath" content="/kolekti/publication-parameters/{f:fsname(string(t:head/t:title))}.xml"/>
    <meta name="kolekti.job" content="{f:fsname(string(t:head/t:title))}.xml"/>
  </head>
  <body>
    <xsl:apply-templates select="t:body"/>
  </body>
</html>
  </xsl:template>

  <xsl:template match="t:section">
    <div class="section">
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <xsl:template match="t:section/t:title">
    <xsl:variable name="sectlvl" select="count(ancestor::t:section)"/>
    <xsl:element name="h{$sectlvl}">
      FIXME <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="t:module">
    <a href="{f:topictranslate(@resid)}" rel="kolekti:topic"/>
  </xsl:template>

</xsl:stylesheet>