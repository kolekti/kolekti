<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" xmlns="http://www.w3.org/1999/xhtml" version="1.0" exclude-result-prefixes="html">
		
  <xsl:template match="node()|@*">
    <xsl:copy>
	<xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="html:body/html:div[@class='section'][1]">
    <div class="FirstPage">
       <p class="Heading"><xsl:apply-templates select="html:h1"/></p>
    </div>
    <xsl:apply-templates/>
  </xsl:template>
</xsl:stylesheet>
