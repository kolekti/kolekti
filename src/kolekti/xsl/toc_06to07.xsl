<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:html="http://www.w3.org/1999/xhtml"
  xmlns:t="kolekti:trames"
  xmlns:f="kolekti:migrate"
  extension-element-prefixes="f"
  exclude-result-prefixes="html"
  >
  <xsl:output method="xml" omit-xml-declaration="yes"/>
  <xsl:namespace-alias stylesheet-prefix="html" result-prefix="#default"/>
  <xsl:param name="job" select="'FIXME'"/>
  
  <xsl:template match="/t:trame">
    <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;
</xsl:text>
    <html>
  <head>
    <title><xsl:value-of select="f:translate(string(t:head/t:title))"/></title>
    <meta name="DC.title" content="f:translate(string(t:head/t:title))"/>
    <meta name="DC.creator" content="convert"/>
    <meta name="kolekti.jobclass" content="{job}"/>
    <meta name="kolekti.job" content="{job}"/>
    <meta name="kolekti.jobpath" content="/kolekti/publication-parameters/{job}.xml"/>
    <meta name="kolekti.pubdir" content="{job}"/>

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
    <h1>
      <xsl:apply-templates select="f:var_section_title(string(.))"/>
    </h1>
  </xsl:template>

  <xsl:template match="html:var">
    <var>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </var>
  </xsl:template>
  
  <xsl:template match="t:module">
    <a href="{f:topictranslate(@resid)}" rel="kolekti:topic"/>
  </xsl:template>

</xsl:stylesheet>
