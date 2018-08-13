<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ext="kolekti:migrate"
  xmlns="http://www.w3.org/1999/xhtml"
  exclude-result-prefixes="ext"
  >
  <xsl:output method="xml"
              encoding="utf-8"
              doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
              doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <xsl:param name="lang"/>

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  
  <xsl:template match="processing-instruction()"/>
  <xsl:template match="/html/@*"/>
  <xsl:template match="/html/body">
    <xsl:copy>
      <xsl:attribute name="lang">
        <xsl:value-of select="substring($lang,1,3)"/>
      </xsl:attribute>
      <xsl:attribute name="xml:lang">
        <xsl:value-of select="substring($lang,1,3)"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>    
  </xsl:template>
  
  

  <xsl:template match="var">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute name="class">
        <xsl:value-of select="ext:translate_variable(@class)"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>
  

  <xsl:template match="div[@class='moduleinfo']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="class">topicinfo</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>


  <xsl:template match="div[@class='module']">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="class">topic</xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="div[@class='TDM']">
    <div class="TOC "><p class="TOC_title"><var class="kolektitext:TOC"></var></p></div>
  </xsl:template>
  
  <xsl:template match="span[@class='title_num']"/>

  <xsl:template match="img[starts-with(@src, '/projects/')][contains(@src, '/medias/')]">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:attribute name="src">
        <xsl:text>/sources/</xsl:text>
        <xsl:value-of select="$lang"/>
        <xsl:text>/pictures/</xsl:text>
        <xsl:value-of select="substring-after(@src, '/medias/')"/>
      </xsl:attribute>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  
</xsl:stylesheet>
